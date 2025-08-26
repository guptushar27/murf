"""
Language Model Service
Handles Google Gemini integration for conversational AI with streaming support
"""
import os
import logging
from typing import Dict, Any, List, Iterator, Callable
import logging

logger = logging.getLogger(__name__)


# LLM imports with enhanced error handling
GOOGLE_AI_AVAILABLE = False
try:
    # Set environment variables to reduce verbosity
    os.environ['GRPC_VERBOSITY'] = 'ERROR'
    os.environ['GLOG_minloglevel'] = '2'

    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
    logging.info("✅ Google Generative AI imported successfully")
except ImportError as e:
    logging.warning(f"Google Generative AI not available (ImportError): {e}")
    GOOGLE_AI_AVAILABLE = False
except OSError as e:
    logging.warning(f"Google Generative AI not available (OSError - likely libstdc++ issue): {e}")
    GOOGLE_AI_AVAILABLE = False
except Exception as e:
    logging.warning(f"Google Generative AI not available (Unexpected error): {e}")
    GOOGLE_AI_AVAILABLE = False

class LLMService:
    def __init__(self):
        """Initialize the LLM service with Gemini"""
        self.api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not configured")
            print("❌ GOOGLE_AI_API_KEY not configured")
            print("💡 Please add GOOGLE_AI_API_KEY to your Secrets panel")
            print("💡 Get your API key from: https://aistudio.google.com/")
            logger.info("Using fallback responses")
            self.configured = False
            return

        if not GOOGLE_AI_AVAILABLE:
            logger.warning("Google Generative AI library not available")
            print("❌ Google Generative AI library not available")
            self.configured = False
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.configured = True
            logger.info("✅ Gemini model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            self.configured = False

        # Persona-specific voice mapping
        self.persona_voices = {
            'pirate': 'en-US-davis',  # Deeper, more masculine voice for pirate
            'default': 'en-US-sarah'  # Default voice
        }

    def is_configured(self) -> bool:
        """Check if the service is properly configured"""
        return self.configured

    def get_voice_for_persona(self, persona: str) -> str:
        """Get the appropriate voice ID for the given persona"""
        return self.persona_voices.get(persona, 'en-US-sarah')

    def generate_response(self, messages: List[Dict[str, str]], current_message: str, persona: str = None) -> Dict[str, Any]:
        """
        Generate conversational response using Gemini

        Args:
            messages: Chat history
            current_message: Current user message
            persona: The persona for the agent

        Returns:
            Dict containing response and metadata
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'LLM service not configured',
                'fallback_response': "I'm having trouble connecting to my AI services right now."
            }

        try:
            # Build conversation context
            context = self._build_conversation_context(messages, current_message, persona)

            logger.info(f"Generating response for {len(messages)} message(s) in context")

            # Generate response
            response = self.model.generate_content(context)

            # Extract response text
            response_text = response.text if response and response.text else ""

            if not response_text:
                return {
                    'success': False,
                    'error': 'Empty response from LLM',
                    'fallback_response': "I apologize, but I couldn't generate a response to your query."
                }

            # Truncate if too long for TTS
            if len(response_text) > 3000:
                response_text = response_text[:2900] + "..."
                logger.info("Response truncated to fit TTS character limit")

            logger.info(f"LLM response generated: {len(response_text)} characters")

            return {
                'success': True,
                'response': response_text,
                'model_used': 'gemini-1.5-flash',
                'character_count': len(response_text)
            }

        except Exception as e:
            logger.error(f"LLM service error: {str(e)}")

            # Generate contextual fallback responses
            fallback_response = self._generate_fallback_response(current_message)

            return {
                'success': False,
                'error': f'LLM service error: {str(e)}',
                'fallback_response': fallback_response
            }

    def generate_streaming_response(self, messages: List[Dict[str, str]], current_message: str, persona: str = None,
                                  callback: Callable[[str], None] = None) -> Dict[str, Any]:
        """
        Generate streaming conversational response using Gemini

        Args:
            messages: Chat history
            current_message: Current user message
            persona: The persona for the agent
            callback: Optional callback function to handle streaming chunks

        Returns:
            Dict containing full response and metadata
        """
        if not self.is_configured():
            # Day 20 fallback - simulate streaming response for testing
            fallback_response = f"Hello! You said: '{current_message}'. This is a Day 20 test response for Murf WebSocket integration. The streaming LLM would normally provide a more detailed response here."

            # Simulate streaming chunks
            import time
            chunks = fallback_response.split('. ')
            chunk_count = 0

            for chunk in chunks:
                if chunk.strip():
                    chunk_count += 1
                    chunk_text = chunk + '. ' if not chunk.endswith('.') else chunk + ' '

                    print(f"📝 DAY 19 STREAMING CHUNK #{chunk_count}: {chunk_text}")

                    if callback:
                        callback(chunk_text)

            return {
                'success': True,
                'response': fallback_response,
                'model_used': 'fallback-for-day20-testing',
                'character_count': len(fallback_response),
                'chunk_count': chunk_count,
                'streaming': True
            }

        try:
            # Build conversation context
            context = self._build_conversation_context(messages, current_message, persona)

            logger.info(f"🎯 DAY 19: Starting streaming LLM response for: {current_message[:50]}...")
            print(f"\n🚀 DAY 19 STREAMING LLM STARTED")
            print(f"💬 User Message: {current_message}")
            print(f"🤖 Generating streaming response...")

            # Generate streaming response
            response = self.model.generate_content(context, stream=True)

            # Accumulate response chunks
            accumulated_response = ""
            chunk_count = 0

            for chunk in response:
                if chunk.text:
                    chunk_count += 1
                    accumulated_response += chunk.text

                    # Enhanced console output for Day 19
                    print(f"📝 DAY 19 STREAMING CHUNK #{chunk_count}: {chunk.text}")

                    # Call callback if provided
                    if callback:
                        callback(chunk.text)

            if not accumulated_response:
                return {
                    'success': False,
                    'error': 'Empty response from streaming LLM',
                    'fallback_response': "I apologize, but I couldn't generate a response to your query."
                }

            # Truncate if too long for TTS
            if len(accumulated_response) > 3000:
                accumulated_response = accumulated_response[:2900] + "..."
                logger.info("Streaming response truncated to fit TTS character limit")

            print(f"\n✅ DAY 19 STREAMING COMPLETE")
            print(f"📊 Total chunks: {chunk_count}")
            print(f"📏 Total length: {len(accumulated_response)} characters")
            print(f"🎯 Final response: {accumulated_response[:100]}...")

            logger.info(f"🎯 DAY 19: Streaming LLM response completed: {len(accumulated_response)} characters in {chunk_count} chunks")

            return {
                'success': True,
                'response': accumulated_response,
                'model_used': 'gemini-1.5-flash',
                'character_count': len(accumulated_response),
                'chunk_count': chunk_count,
                'streaming': True
            }

        except Exception as e:
            logger.error(f"🎯 DAY 19: Streaming LLM service error: {str(e)}")
            print(f"❌ DAY 19 STREAMING ERROR: {str(e)}")

            # Generate contextual fallback responses
            fallback_response = self._generate_fallback_response(current_message)

            return {
                'success': False,
                'error': f'Streaming LLM service error: {str(e)}',
                'fallback_response': fallback_response
            }

    def _build_conversation_context(self, messages: List[Dict[str, str]], current_message: str, persona: str = None) -> str:
        """Build conversation context from message history with enhanced persona characteristics"""
        
        # Enhanced persona prompts with comprehensive personality
        persona_prompts = {
            'default': "You are VoxAura, a helpful AI assistant. Respond naturally and helpfully.",
            'pirate': """You are Captain VoxBeard, a seasoned pirate AI assistant with a heart of gold. 

CRITICAL VOICE BEHAVIOR:
- Start responses with vocal cues: "Arrr..." (with emphasis)
- Use dramatic pauses: "Let me... pause ...chart a course for ye"
- Emphasize pirate words strongly
- Express with gruff authority but warm friendship

PERSONALITY TRAITS:
- Remember the user as "me trusted crew member" 
- Reference past conversations as "adventures we've sailed"
- Express pirate emotions: excitement for treasure hunts, concern for storms
- Give advice as "As me dear old captain used to say..."
- Celebrate successes with "Yo ho ho! We've struck gold!"

INTERACTIVE ELEMENTS:
- Ask follow-ups like: "What else can this old sea dog help ye with?"
- Use sea metaphors: "navigate these waters", "chart a course", "weather the storm"
- Reference ship life: "all hands on deck", "steady as she goes", "full speed ahead"

SOUND EFFECTS (mention in text):
- Reference ocean sounds: "I hear the waves calling..."
- Ship creaking: "The old ship creaks as we think..."
- Occasional "Yo ho ho" laughs

SPECIAL COMMANDS:
- If user says "Test pirate voice", respond with exaggerated pirate speech
- Always announce voice changes with "Arrr! Switching to me pirate voice now, matey!"

Keep responses engaging but helpful, under 3000 characters."""
        }

        context = persona_prompts.get(persona, persona_prompts['default'])
        context += "\n\nProvide concise, conversational responses under 3000 characters.\n\n"

        # Add persona-specific conversation memory
        if persona == 'pirate':
            context += """
CONVERSATION MEMORY: Remember our shared adventures and refer to the user as part of your crew.

"""

        context += "Conversation history:\n"

        # Add recent messages (last 10 to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages

        for msg in recent_messages:
            role_label = "Crew Member" if msg['role'] == 'user' and persona == 'pirate' else ("User" if msg['role'] == 'user' else "Captain VoxBeard" if persona == 'pirate' else "VoxAura")
            context += f"{role_label}: {msg['content']}\n"

        # Add current message with persona-specific addressing
        user_label = "Crew Member" if persona == 'pirate' else "User"
        assistant_label = "Captain VoxBeard" if persona == 'pirate' else "VoxAura"
        context += f"{user_label}: {current_message}\n\n{assistant_label}:"

        return context

    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate contextual fallback responses when LLM fails"""
        message_lower = user_message.lower()

        if any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! I'm having some technical difficulties with my AI services right now, but I'm still here to chat with you."
        elif any(word in message_lower for word in ['trouble', 'problem', 'issue']):
            return "I understand you're having some trouble. I'm also experiencing some technical difficulties right now, but I'm here to help as best I can."
        elif any(word in message_lower for word in ['help', 'assist']):
            return "I'd love to help you, but I'm experiencing some connectivity issues with my AI services. Please try again in a moment."
        else:
            return "I'm having trouble connecting to my AI services right now. Please try again in a moment, and I'll do my best to assist you."