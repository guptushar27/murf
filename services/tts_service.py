"""
Text-to-Speech Service
Handles Murf AI and gTTS fallback for voice synthesis
"""
import os
import logging
import hashlib
import uuid
from typing import Dict, Any, Optional
from gtts import gTTS
try:
    from murf import Murf
except ImportError:
    Murf = None
from flask import url_for

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self, app=None, api_key=None):
        """Initialize TTS service with Murf and gTTS fallback"""
        self.app = app
        self.api_key = api_key or os.environ.get('MURF_API_KEY')
        
        if not self.api_key:
            logger.warning("Murf package not available")
            
        # Initialize audio directory
        if app:
            self.audio_dir = os.path.join(app.instance_path, 'static', 'audio')
            os.makedirs(self.audio_dir, exist_ok=True)
        else:
            self.audio_dir = os.path.join(os.getcwd(), 'static', 'audio')
            os.makedirs(self.audio_dir, exist_ok=True)
            
    def generate_speech(self, text: str, persona: str = 'default') -> Dict[str, Any]:
        """Generate speech from text using available TTS service"""
        try:
            # Use gTTS as fallback
            unique_id = str(uuid.uuid4())[:8]
            filename = f"tts_{unique_id}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            # Generate speech with gTTS
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filepath)
            
            # Generate URL
            if self.app:
                audio_url = url_for('serve_audio_file', filename=filename)
            else:
                audio_url = f"/static/audio/{filename}"
                
            logger.info(f"Generated TTS audio: {filename}")
            
            return {
                'success': True,
                'audio_url': audio_url,
                'filename': filename,
                'service_used': 'gTTS',
                'character_count': len(text)
            }
            
        except Exception as e:
            logger.error(f"TTS generation error: {e}")
            return {
                'success': False,
                'error': f'TTS generation failed: {str(e)}'
            }
        self.app = app
        self.murf_api_key = os.environ.get("MURF_API_KEY")
        if self.murf_api_key and Murf:
            try:
                self.murf_client = Murf(api_key=self.murf_api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Murf client: {e}")
                self.murf_client = None
        else:
            self.murf_client = None
            if not Murf:
                logger.warning("Murf package not available")
            else:
                logger.warning("Murf API key not configured")

        # Persona-specific voice configurations
        self.persona_voices = {
            'default': {
                'voice': 'en-US-AriaNeural',
                'style': 'friendly',
                'pitch': '+0Hz',
                'rate': '+0%',
                'volume': '+0%'
            },
            'pirate': {
                'voice': 'en-US-DavisNeural',  # Deeper male voice
                'style': 'authoritative',
                'pitch': '-15Hz',  # Much lower pitch for gruff voice
                'rate': '-15%',    # Slower speech for dramatic effect
                'volume': '+10%'   # Louder for commanding presence
            }
        }

    def is_murf_configured(self) -> bool:
        """Check if Murf service is configured"""
        return bool(self.murf_client)

    def generate_speech(self, text: str, voice_id: str = "en-US-natalie", persona: str = "default") -> Dict[str, Any]:
        """
        Generate speech from text using Murf AI with gTTS fallback and persona-specific voice modulation

        Args:
            text: Text to convert to speech
            voice_id: Voice ID for Murf (default: en-US-natalie)
            persona: Persona for voice characteristics and behavior

        Returns:
            Dict containing audio URL and metadata
        """
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'No text provided for speech generation'
            }

        text = text.strip()

        # Enhanced persona-specific voice mapping with characteristics
        persona_config = {
            'pirate': {
                'voice_id': 'en-US-davis',
                'pitch_adjustment': -15,  # 15% lower pitch
                'speed_adjustment': -10,  # 10% slower
                'style': 'gruff',
                'announce_change': "Arrr! Switching to me pirate voice now, matey!",
                'sound_effects': ['ocean_waves', 'ship_creaking']
            },
            'default': {
                'voice_id': 'en-US-sarah',
                'pitch_adjustment': 0,
                'speed_adjustment': 0,
                'style': 'friendly',
                'announce_change': "Switching back to my default voice.",
                'sound_effects': []
            }
        }

        # Get persona configuration
        config = persona_config.get(persona, persona_config['default'])
        voice_id = config['voice_id']

        # Log voice change announcement
        if persona != 'default':
            logger.info(f"🎭 PERSONA VOICE CHANGE: {config['announce_change']}")
            print(f"🎭 {config['announce_change']}")

        logger.info(f"Using voice '{voice_id}' for persona '{persona}' with adjustments: pitch={config['pitch_adjustment']}%, speed={config['speed_adjustment']}%")

        # Try Murf first if configured
        if self.is_murf_configured():
            murf_result = self._generate_murf_speech_with_persona(text, voice_id, config)
            if murf_result['success']:
                return murf_result

            logger.warning("Murf TTS failed, falling back to gTTS")

        # Fallback to gTTS with persona characteristics
        return self._generate_gtts_speech_with_persona(text, persona, config)

    def _generate_murf_speech_with_persona(self, text: str, voice_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speech using Murf AI with persona-specific voice modulation"""
        try:
            logger.info(f"Generating Murf speech with persona: {len(text)} characters")

            # Calculate voice parameters based on persona config
            base_pitch = 1.0
            base_speed = 1.0

            # Apply persona adjustments
            pitch_multiplier = base_pitch + (config['pitch_adjustment'] / 100.0)
            speed_multiplier = base_speed + (config['speed_adjustment'] / 100.0)

            logger.info(f"Applying voice modulation - Pitch: {pitch_multiplier:.2f}, Speed: {speed_multiplier:.2f}")

            # Enhanced Murf API call with voice modulation
            murf_params = {
                'text': text,
                'voice_id': voice_id,
                'format': "MP3",
                'sample_rate': 44100.0
            }

            # Add voice modulation parameters if supported
            try:
                murf_params['pitch'] = pitch_multiplier
                murf_params['speed'] = speed_multiplier
                murf_params['style'] = config.get('style', 'default')
            except:
                logger.warning("Voice modulation parameters not supported by current Murf version")

            response = self.murf_client.text_to_speech.generate(**murf_params)

            # Extract audio URL
            audio_url = None
            if hasattr(response, 'audio_file'):
                audio_url = response.audio_file
            elif isinstance(response, dict):
                audio_url = response.get('audio_file') or response.get('url')

            if not audio_url:
                logger.error("No audio URL in Murf response")
                return {
                    'success': False,
                    'error': 'No audio URL received from Murf API'
                }

            logger.info("Murf speech with persona generated successfully")

            return {
                'success': True,
                'audio_url': audio_url,
                'voice_used': voice_id,
                'service_used': 'murf_persona',
                'character_count': len(text),
                'persona_config': config,
                'voice_modulation': {
                    'pitch': pitch_multiplier,
                    'speed': speed_multiplier,
                    'style': config.get('style')
                }
            }

        except Exception as e:
            logger.error(f"Murf TTS with persona error: {str(e)}")
            return {
                'success': False,
                'error': f'Murf TTS with persona error: {str(e)}'
            }

    def _generate_gtts_speech_with_persona(self, text: str, persona: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate speech using Google TTS fallback with persona voice simulation"""
        try:
            logger.info(f"Generating gTTS speech with persona '{persona}': {len(text)} characters")

            # Create unique filename with persona identifier
            text_hash = hashlib.md5(text.encode()).hexdigest()
            filename = f"gtts-{persona}-{text_hash[:8]}-{uuid.uuid4().hex[:8]}.mp3"

            # Apply persona-specific text modifications for voice simulation
            modified_text = self._apply_persona_text_effects(text, persona, config)

            # Generate TTS with persona modifications
            # Use slower speech for pirate to simulate gruffness
            slow_speech = config['speed_adjustment'] < -5
            tts = gTTS(text=modified_text, lang='en', slow=slow_speech)

            # Save to audio directory
            static_dir = os.path.join(self.app.instance_path, 'static', 'audio')
            os.makedirs(static_dir, exist_ok=True)

            audio_path = os.path.join(static_dir, filename)
            tts.save(audio_path)

            # Apply post-processing voice effects if possible
            processed_audio_path = self._apply_voice_effects(audio_path, config)

            # Generate URL - use url_for to get a proper external URL for HTTPS compatibility
            with self.app.app_context():
                # Use processed audio if available, otherwise original
                final_filename = os.path.basename(processed_audio_path) if processed_audio_path else filename
                audio_url = url_for('serve_audio_file', filename=final_filename, _external=True, _scheme='https')

            logger.info(f"gTTS speech with persona '{persona}' generated successfully")

            return {
                'success': True,
                'audio_url': audio_url,
                'voice_used': f'gTTS-{persona}-enhanced',
                'service_used': 'gtts_persona',
                'character_count': len(text),
                'filename': final_filename if processed_audio_path else filename,
                'persona': persona,
                'persona_config': config,
                'voice_effects_applied': bool(processed_audio_path),
                'original_text': text,
                'modified_text': modified_text
            }

        except Exception as e:
            logger.error(f"gTTS with persona error: {str(e)}")
            return {
                'success': False,
                'error': f'gTTS with persona error: {str(e)}'
            }

    def _apply_persona_text_effects(self, text: str, persona: str, config: Dict[str, Any]) -> str:
        """Apply persona-specific text modifications for voice simulation"""
        if persona == 'pirate':
            # Add dramatic pauses and emphasis for pirate voice
            modified_text = text

            # Add pauses for dramatic effect
            modified_text = modified_text.replace('.', '... ')
            modified_text = modified_text.replace(',', ', pause, ')

            # Emphasize pirate words
            pirate_words = ['arrr', 'matey', 'ahoy', 'ye', 'treasure', 'ship', 'sea', 'captain']
            for word in pirate_words:
                modified_text = modified_text.replace(word, f'{word.upper()}')
                modified_text = modified_text.replace(word.capitalize(), f'{word.upper()}')

            return modified_text

        return text

    def _apply_voice_effects(self, audio_path: str, config: Dict[str, Any]) -> str:
        """Apply post-processing voice effects (placeholder for future audio processing)"""
        try:
            # Placeholder for future audio processing with libraries like pydub
            # This would apply pitch shifting, speed changes, reverb, etc.

            # For now, we'll just log the intent
            effects = []
            if config['pitch_adjustment'] != 0:
                effects.append(f"pitch adjustment: {config['pitch_adjustment']}%")
            if config['speed_adjustment'] != 0:
                effects.append(f"speed adjustment: {config['speed_adjustment']}%")
            if config.get('style') != 'default':
                effects.append(f"style: {config['style']}")

            if effects:
                logger.info(f"Voice effects to apply: {', '.join(effects)}")
                print(f"🎵 Voice effects simulated: {', '.join(effects)}")

            # Return None to indicate no processing was done (yet)
            return None

        except Exception as e:
            logger.warning(f"Voice effects processing failed: {str(e)}")
            return None

    def generate_audio(self, text: str) -> Dict[str, Any]:
        """Generate audio from text (alias for generate_speech)"""
        return self.generate_speech(text)

    def create_fallback_audio(self, message: str = "I'm having trouble connecting right now") -> str:
        """Create fallback audio for error cases"""
        try:
            result = self._generate_gtts_speech(message)
            if result['success']:
                return result['audio_url']
        except Exception as e:
            logger.error(f"Fallback audio generation failed: {str(e)}")

        # Return demo audio URL as last resort
        return "data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmcfCjuO0y7RgTEGHW/A7+OZUSI="