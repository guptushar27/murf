#!/usr/bin/env python3
"""
VoxAura - Day 21: Streaming Audio Data to Client
Advanced AI Voice Agent with WebSocket Communication
"""

import os
import logging
import asyncio
import json  # Import json for parsing API keys
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, session, has_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename

# Import services
from services.websocket_service import WebSocketService
from services.llm_service import LLMService
from services.stt_service import STTService
from services.tts_service import TTSService
from services.pdf_service import PDFService # Import PDFService for document processing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voxaura.log'),
        logging.StreamHandler()
    ])
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY',
                                          'voxaura-day21-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB limit for file uploads

# Initialize SocketIO
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    async_mode='threading',
                    logger=False,
                    engineio_logger=False)

# Initialize services
# Moved initialization to after configuration checks to allow dynamic API key setting
websocket_service = None
llm_service = None
stt_service = None
tts_service = None

# --- API Key Management and Service Initialization ---

def get_configured_api_keys():
    """Retrieves API keys from session first, then environment variables"""
    # Check if we're in a request context
    from flask import has_request_context

    if has_request_context():
        # Prioritize session (user-provided) keys over environment keys when in request context
        assemblyai_key = session.get('assemblyai_api_key') or os.environ.get('ASSEMBLYAI_API_KEY')
        gemini_key = session.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
        murf_key = session.get('murf_api_key') or os.environ.get('MURF_API_KEY')
        weather_key = session.get('openweather_api_key') or os.environ.get('WEATHER_API_KEY') or os.environ.get('OPENWEATHER_API_KEY')
    else:
        # Use only environment variables during startup
        assemblyai_key = os.environ.get('ASSEMBLYAI_API_KEY')
        gemini_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_API_KEY')
        murf_key = os.environ.get('MURF_API_KEY')
        weather_key = os.environ.get('WEATHER_API_KEY') or os.environ.get('OPENWEATHER_API_KEY')

    return {
        'assemblyai': assemblyai_key,
        'gemini': gemini_key,
        'murf': murf_key,
        'weather': weather_key
    }

def initialize_services(api_keys):
    """Initializes services with provided API keys"""
    global websocket_service, llm_service, stt_service, tts_service

    try:
        logger.info("Initializing services...")
        stt_service = STTService(api_key=api_keys.get('assemblyai'))
        tts_service = TTSService(api_key=api_keys.get('murf')) # TTSService might not need direct API key here if it reads from env or session internally

        # LLMService needs weather and potentially other services, initialize it last
        llm_service = LLMService(
            gemini_api_key=api_keys.get('gemini'),
            weather_api_key=api_keys.get('weather')
        )
        websocket_service = WebSocketService(llm_service=llm_service, tts_service=tts_service)
        logger.info("Services initialized successfully.")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        # Depending on severity, you might want to re-raise or handle gracefully
        raise

def check_api_configuration():
    """Check API key configuration and print status"""
    print("\n" + "=" * 60)
    print("API Configuration Status:")
    print("-" * 60)

    api_keys = get_configured_api_keys()
    config_status = {
        'assemblyai': bool(api_keys['assemblyai']),
        'gemini': bool(api_keys['gemini']),
        'murf': bool(api_keys['murf']),
        'weather': bool(api_keys['weather'])
    }

    print(
        f"AssemblyAI (STT): {'✅ Configured' if config_status['assemblyai'] else '❌ Missing ASSEMBLYAI_API_KEY'}"
    )
    print(
        f"Gemini AI (LLM): {'✅ Configured' if config_status['gemini'] else '❌ Missing GEMINI_API_KEY or GOOGLE_AI_API_KEY'}"
    )
    print(
        f"Murf AI (TTS): {'✅ Configured' if config_status['murf'] else '❌ Missing MURF_API_KEY'}")
    print(
        f"Weather API (Enhanced): {'✅ Configured' if config_status['weather'] else '❌ Missing WEATHER_API_KEY or OPENWEATHER_API_KEY'}"
    )
    print(f"Web Search: ✅ Configured (DuckDuckGo - no API key required)")
    print(
        f"Study Assistant: ✅ Configured (Document analysis, URL/PDF parsing - no API key required)"
    )
    print("-" * 60)

    if not config_status['weather']:
        print(
            "\n💡 Tip: For enhanced weather features (hourly forecast, air quality, alerts, clothing suggestions),"
        )
        print("   get a free API key from WeatherAPI.com: https://www.weatherapi.com/signup.aspx")
        print("   or use your OpenWeatherMap API key as OPENWEATHER_API_KEY.")
        print("   Add it to your .env file or the UI configuration.")
        print("-" * 60)

    return config_status

# Initialize services with keys from environment or session
initial_api_keys = get_configured_api_keys()
initialize_services(initial_api_keys)


# --- Routes ---

@app.route('/')
def index():
    """Main application page"""
    # Pass API key status to template for UI configuration
    api_config_status = check_api_configuration()
    return render_template('index.html', api_config_status=api_config_status)


@app.route('/day18_turn_detection')
def day18_turn_detection():
    """Day 18 turn detection page with Day 21 features"""
    return render_template('day18_turn_detection.html')


@app.route('/llm/query', methods=['POST'])
def llm_query():
    """Handle LLM queries with enhanced error handling"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'success': False, 'error': 'Message is required'}), 400

        message = data['message']
        persona = data.get('persona', 'default')

        # Get API keys from request
        api_keys_header = request.headers.get('X-API-Keys')
        api_keys = {}
        if api_keys_header:
            try:
                api_keys = json.loads(api_keys_header)
            except:
                api_keys = data.get('api_keys', {})
        else:
            api_keys = data.get('api_keys', {})

        # Use provided API key or fallback to environment
        gemini_key = api_keys.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
        if not gemini_key:
            return jsonify({
                'success': False,
                'error': 'Gemini API key not configured',
                'response': 'Please configure your Gemini API key in settings.'
            })

        llm_service = LLMService(api_key=gemini_key)

        result = llm_service.generate_response(
            message=message,
            persona=persona
        )

        if result['success']:
            return jsonify({
                'success': True,
                'response': result['response']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'response': result.get('fallback_response', 'Service temporarily unavailable')
            })

    except Exception as e:
        logger.error(f"LLM query error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'response': 'I apologize, but I\'m experiencing technical difficulties. Please try again.'
        }), 500


@app.route('/generate-tts', methods=['POST'])
def generate_tts():
    """Generate TTS audio with enhanced error handling"""
    try:
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'success': False, 'error': 'Text is required'}), 400

        text = data['text']
        persona = data.get('persona', 'default')

        if len(text.strip()) == 0:
            return jsonify({'success': False, 'error': 'Text cannot be empty'})

        if len(text) > 1000:  # Reasonable limit
            text = text[:1000] + "..."

        # Get API keys from headers or request data
        api_keys_header = request.headers.get('X-API-Keys')
        api_keys = {}
        if api_keys_header:
            try:
                api_keys = json.loads(api_keys_header)
            except:
                api_keys = data.get('api_keys', {})
        else:
            api_keys = data.get('api_keys', {})

        murf_key = api_keys.get('murf_api_key') or os.environ.get('MURF_API_KEY')
        tts_service = TTSService(api_key=murf_key)
        result = tts_service.generate_speech(text=text, persona=persona)

        if result['success']:
            return jsonify({
                'success': True,
                'audio_url': result['audio_url'],
                'persona': persona
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            })

    except Exception as e:
        logger.error(f"TTS generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'TTS generation failed'
        }), 500




@app.route('/test-llm')
def test_llm():
    """Test LLM service page"""
    return render_template('test_llm.html')


@app.route('/static/audio/<filename>')
def serve_audio_file(filename):
    """Serve generated audio files with HTTPS support"""
    try:
        audio_dir = os.path.join(app.instance_path, 'static', 'audio')
        file_path = os.path.join(audio_dir, filename)

        if os.path.exists(file_path):
            response = send_file(file_path, mimetype='audio/mpeg')
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Cache-Control'] = 'public, max-age=3600'
            return response
        else:
            return jsonify({'error': 'Audio file not found'}), 404

    except Exception as e:
        logger.error(f"Error serving audio file: {str(e)}")
        return jsonify({'error': 'Failed to serve audio file'}), 500


@app.route('/agent/chat/<session_id>', methods=['POST'])
def agent_chat(session_id):
    """Enhanced chat endpoint with complete pipeline"""
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No audio file selected'}), 400

        logger.info(f"Processing audio message for session: {session_id}")

        # Get persona from form data
        persona = request.form.get('persona', 'default')
        logger.info(f"Using persona: {persona}")

        # Get API keys from headers or form data
        api_keys_header = request.headers.get('X-API-Keys')
        api_keys = {}
        if api_keys_header:
            try:
                api_keys = json.loads(api_keys_header)
            except:
                api_keys_str = request.form.get('api_keys')
                if api_keys_str:
                    try:
                        api_keys = json.loads(api_keys_str)
                    except:
                        pass

        # 1. STT Processing
        assemblyai_key = api_keys.get('assemblyai_api_key') or os.environ.get('ASSEMBLYAI_API_KEY')
        stt_service = STTService(api_key=assemblyai_key)
        stt_result = stt_service.transcribe_audio(audio_file)

        if not stt_result['success']:
            return jsonify({
                'success': False,
                'error': stt_result['error'],
                'fallback_message': stt_result.get('fallback_message', 'Speech recognition failed')
            }), 400

        transcription = stt_result['transcription']
        logger.info(f"STT Success: {transcription}")

        # 2. LLM Processing
        gemini_key = api_keys.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
        llm_service = LLMService(api_key=gemini_key)
        llm_result = llm_service.generate_response(
            message=transcription,
            persona=persona
        )

        if not llm_result['success']:
            return jsonify({
                'success': False,
                'error': llm_result['error'],
                'fallback_message': llm_result.get('fallback_response', 'AI response generation failed')
            }), 500

        llm_response = llm_result['response']
        logger.info(f"LLM Success: Generated {len(llm_response)} character response")

        # 3. TTS Processing (with error handling)
        murf_key = api_keys.get('murf_api_key') or os.environ.get('MURF_API_KEY')
        tts_service = TTSService(api_key=murf_key)
        try:
            tts_result = tts_service.generate_speech(
                text=llm_response,
                persona=persona
            )

            audio_url = None
            if tts_result['success']:
                audio_url = tts_result['audio_url']
                logger.info(f"TTS Success: {audio_url}")
            else:
                logger.warning(f"TTS failed: {tts_result['error']}")

        except Exception as tts_error:
            logger.error(f"TTS processing error: {str(tts_error)}")
            audio_url = None

        # Return successful response (even if TTS failed)
        response_data = {
            'success': True,
            'transcription': transcription,
            'llm_response': llm_response,
            'session_id': session_id,
            'persona': persona,
            'stt_metadata': {
                'confidence': stt_result.get('confidence'),
                'word_count': stt_result.get('word_count'),
                'audio_duration': stt_result.get('audio_duration')
            }
        }

        if audio_url:
            response_data['audio_url'] = audio_url

        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Agent chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'fallback_message': 'Voice processing service is temporarily unavailable'
        }), 500


@app.route('/agent/chat/<session_id>/history')
def get_chat_history(session_id):
    """Get chat history for a session"""
    return jsonify({'success': True, 'messages': [], 'message_count': 0})


@app.route('/agent/chat/<session_id>/clear', methods=['POST'])
def clear_chat_history(session_id):
    """Clear chat history for a session"""
    return jsonify({'success': True})

# --- API Configuration Routes ---
@app.route('/api/config', methods=['GET'])
def get_config_status():
    """Get current API configuration status"""
    try:
        config_status = check_api_configuration()
        return jsonify({
            'success': True,
            'config_status': config_status
        })
    except Exception as e:
        logger.error(f"Error getting configuration status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['POST'])
def update_config():
    """Update API keys configuration"""
    try:
        data = request.get_json()
        logger.info(f"Received config update: {list(data.keys())}")

        # Update API keys in session
        updated = False

        if 'assemblyai_api_key' in data and data['assemblyai_api_key']:
            session['assemblyai_api_key'] = data['assemblyai_api_key']
            updated = True
            logger.info("AssemblyAI API Key updated.")

        if 'gemini_api_key' in data and data['gemini_api_key']:
            session['gemini_api_key'] = data['gemini_api_key']
            updated = True
            logger.info("Gemini API Key updated.")

        if 'murf_api_key' in data and data['murf_api_key']:
            session['murf_api_key'] = data['murf_api_key']
            updated = True
            logger.info("Murf API Key updated.")

        if 'openweather_api_key' in data and data['openweather_api_key']:
            session['openweather_api_key'] = data['openweather_api_key']
            updated = True
            logger.info("OpenWeather API Key updated.")

        # Re-initialize services if any API key was updated
        if updated:
            try:
                logger.info("Re-initializing services with updated API keys...")
                current_api_keys = get_configured_api_keys()
                initialize_services(current_api_keys)
                logger.info("Services re-initialized successfully.")

                # Get updated configuration status
                config_status = check_api_configuration()

                return jsonify({
                    'success': True,
                    'message': 'Configuration updated successfully. Services reloaded.',
                    'services_updated': updated,
                    'config_status': config_status
                })
            except Exception as e:
                logger.error(f"Failed to reinitialize services: {e}")
                return jsonify({
                    'success': False,
                    'message': f'Configuration updated but service reload failed: {str(e)}',
                    'services_updated': updated,
                    'config_status': check_api_configuration()
                }), 500
        else:
            return jsonify({
                'success': False,
                'message': 'No valid API keys provided for update.',
                'config_status': check_api_configuration()
            }), 400

    except Exception as e:
        logger.error(f"Error updating configuration: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/upload_pdf', methods=['POST'])
def upload_pdf():
    """Handle PDF upload and analysis with enhanced error handling"""
    try:
        if 'pdf_file' not in request.files:
            return jsonify({'success': False, 'error': 'No PDF file provided'}), 400

        pdf_file = request.files['pdf_file']
        analysis_type = request.form.get('analysis_type', 'summarize')
        user_query = request.form.get('user_query', 'Please summarize this document')
        persona = request.form.get('persona', 'default')

        if pdf_file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        # Get API keys from headers or form data
        api_keys_header = request.headers.get('X-API-Keys')
        api_keys = {}
        if api_keys_header:
            try:
                api_keys = json.loads(api_keys_header)
            except:
                api_keys_str = request.form.get('api_keys')
                if api_keys_str:
                    try:
                        api_keys = json.loads(api_keys_str)
                    except:
                        pass

        # Check file type
        allowed_extensions = {'.pdf', '.doc', '.docx', '.txt'}
        file_ext = os.path.splitext(pdf_file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            return jsonify({'success': False, 'error': 'Unsupported file type'}), 400

        # Check file size (10MB limit)
        pdf_file.seek(0, 2)  # Seek to end
        file_size = pdf_file.tell()
        pdf_file.seek(0)  # Reset to beginning

        if file_size > 10 * 1024 * 1024:  # 10MB
            return jsonify({'success': False, 'error': 'File size too large (max 10MB)'}), 400

        # Process the document
        pdf_service = PDFService()
        extraction_result = pdf_service.extract_text_from_file(pdf_file)

        if not extraction_result['success']:
            return jsonify({
                'success': False,
                'error': f"Document processing failed: {extraction_result['error']}"
            }), 400

        extracted_text = extraction_result['text']
        logger.info(f"Document processed: {len(extracted_text)} characters extracted")

        # Generate LLM response based on the document content
        gemini_key = api_keys.get('gemini_api_key') or os.environ.get('GEMINI_API_KEY')
        if not gemini_key:
            return jsonify({
                'success': False,
                'error': 'Gemini API key required for document analysis'
            }), 400

        llm_service = LLMService(api_key=gemini_key)

        # Create context-aware prompt
        if analysis_type == 'summarize':
            prompt = f"Please provide a comprehensive summary of the following document:\n\n{extracted_text}"
        else:
            prompt = f"Based on the following document content, please answer this question: {user_query}\n\nDocument content:\n{extracted_text}"

        llm_result = llm_service.generate_response(
            message=prompt,
            persona=persona
        )

        if not llm_result['success']:
            return jsonify({
                'success': False,
                'error': 'Failed to generate AI response for the document'
            }), 500

        response_text = llm_result['response']

        # Store the analysis result for potential future reference
        analysis_data = {
            'session_id': session_id,
            'filename': pdf_file.filename,
            'analysis_type': analysis_type,
            'user_query': user_query,
            'response': response_text,
            'timestamp': datetime.now().isoformat(),
            'persona': persona
        }

        logger.info(f"PDF analysis completed for {pdf_file.filename}")

        return jsonify({
            'success': True,
            'response': response_text,
            'filename': pdf_file.filename,
            'analysis_type': analysis_type,
            'persona': persona,
            'document_stats': {
                'size_mb': round(file_size / (1024 * 1024), 2),
                'text_length': len(extracted_text),
                'response_length': len(response_text)
            }
        })

    except Exception as e:
        logger.error(f"PDF upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during document processing'
        }), 500


# --- WebSocket Event Handlers ---
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit(
        'status', {
            'connected': True,
            'active_sessions': websocket_service.get_active_sessions_count()
        })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    websocket_service.unregister_session(request.sid)


@socketio.on('register_session')
def handle_register_session(data):
    """Register a new session"""
    session_id = data.get('session_id', 'unknown')
    websocket_service.register_session(session_id, request.sid)
    join_room(request.sid)
    print(f"Session registered: {session_id} for socket {request.sid}")


@socketio.on('message')
def handle_message(message):
    """Handle general messages"""
    try:
        response = websocket_service.handle_echo_message(request.sid, message)
        emit('echo_response', response)
    except Exception as e:
        logger.error(f"Message handling error: {str(e)}")
        emit('error', {'message': str(e)})


@socketio.on('chat_message')
def handle_chat_message(data):
    """Handle chat messages"""
    try:
        response = websocket_service.handle_chat_message(request.sid, data)
        emit('chat_response', response)
    except Exception as e:
        logger.error(f"Chat message handling error: {str(e)}")
        emit('error', {'message': str(e)})


@socketio.on('audio_stream')
def handle_audio_stream(data):
    """Handle audio stream data"""
    try:
        response = websocket_service.handle_audio_stream(request.sid, data)
        emit('audio_processed', response)
    except Exception as e:
        logger.error(f"Audio stream handling error: {str(e)}")
        emit('error', {'message': str(e)})


@socketio.on('start_streaming_transcription')
def handle_start_streaming_transcription(data):
    """Start streaming transcription"""
    try:
        result = websocket_service.start_realtime_transcription(request.sid)
        emit('transcription_status', result)
    except Exception as e:
        logger.error(f"Start transcription error: {str(e)}")
        emit('transcription_status', {'status': 'error', 'message': str(e)})


@socketio.on('stop_streaming_transcription')
def handle_stop_streaming_transcription(data):
    """Stop streaming transcription"""
    try:
        websocket_service.stop_realtime_transcription(request.sid)
        emit('transcription_status', {
            'status': 'stopped',
            'message': 'Transcription stopped'
        })
    except Exception as e:
        logger.error(f"Stop transcription error: {str(e)}")
        emit('transcription_status', {'status': 'error', 'message': str(e)})


@socketio.on('streaming_audio_transcription')
def handle_streaming_audio_transcription(data):
    """Handle streaming audio for transcription"""
    try:
        response = websocket_service.handle_streaming_audio_transcription(
            request.sid, data)
        if 'error' in response:
            emit('transcription_status', {
                'status': 'error',
                'message': response['error']
            })
    except Exception as e:
        logger.error(f"Streaming audio transcription error: {str(e)}")
        emit('transcription_status', {'status': 'error', 'message': str(e)})


@socketio.on('process_llm_request')
def handle_process_llm_request(data):
    """Process LLM request from transcript"""
    try:
        transcript = data.get('transcript', '')
        session_id = data.get('session_id', 'unknown')

        print(f"\nDAY 19: PROCESSING LLM REQUEST")
        print(f"Transcript: {transcript}")
        print(f"Session ID: {session_id}")

        # Process with streaming LLM
        websocket_service._process_transcript_with_streaming_llm(
            request.sid, transcript)

    except Exception as e:
        logger.error(f"LLM request processing error: {str(e)}")
        emit('llm_error', {'error': str(e)})


@socketio.on('start_murf_websocket')
def handle_start_murf_websocket(data):
    """Start Murf WebSocket connection"""
    try:
        result = websocket_service.start_murf_websocket_sync(request.sid)
        emit('murf_websocket_status', result)

        if result['status'] == 'connected':
            print(f"DAY 20: Murf WebSocket started for session {request.sid}")

    except Exception as e:
        logger.error(f"Murf WebSocket start error: {str(e)}")
        emit('murf_websocket_status', {'status': 'error', 'message': str(e)})


@socketio.on('stop_murf_websocket')
def handle_stop_murf_websocket(data):
    """Stop Murf WebSocket connection"""
    try:
        asyncio.create_task(websocket_service.stop_murf_websocket(request.sid))
        emit('murf_websocket_status', {
            'status': 'disconnected',
            'message': 'Murf WebSocket stopped'
        })
    except Exception as e:
        logger.error(f"Murf WebSocket stop error: {str(e)}")
        emit('murf_websocket_status', {'status': 'error', 'message': str(e)})


@socketio.on('start_realtime_transcription')
def handle_start_realtime_transcription(data):
    """Start real-time transcription"""
    try:
        result = websocket_service.start_realtime_transcription(request.sid)
        emit('transcription_status', result)
    except Exception as e:
        logger.error(f"Real-time transcription start error: {str(e)}")
        emit('transcription_status', {'status': 'error', 'message': str(e)})


@socketio.on('stop_realtime_transcription')
def handle_stop_realtime_transcription(data):
    """Stop real-time transcription"""
    try:
        websocket_service.stop_realtime_transcription(request.sid)
        emit('transcription_status', {
            'status': 'stopped',
            'message': 'Real-time transcription stopped'
        })
    except Exception as e:
        logger.error(f"Real-time transcription stop error: {str(e)}")
        emit('transcription_status', {'status': 'error', 'message': str(e)})


@socketio.on('audio_chunk')
def handle_audio_chunk(data):
    """Handle audio chunk for processing"""
    try:
        response = websocket_service.handle_streaming_audio_transcription(
            request.sid, data)
        if 'error' in response:
            emit('error', response)
    except Exception as e:
        logger.error(f"Audio chunk handling error: {str(e)}")
        emit('error', {'message': str(e)})


# Day 21 & 22 specific event handlers
@socketio.on('test_request')
def handle_test_request(data):
    """Handle test requests for different days' functionalities"""
    sid = request.sid
    action = data.get('action')
    logger.info(f"Received test request: {action} from SID: {sid}")

    # Day 21: Test audio streaming
    if action == 'test_day21_streaming':
        logger.info("DAY 21: Testing audio streaming functionality")

        test_text = "This is a Day 21 test of streaming audio data to the client. The audio is being sent in chunks for real-time playback."

        # Generate TTS for the test
        tts_result = tts_service.generate_speech(test_text)

        if tts_result['success']:
            # Simulate streaming the audio data
            audio_url = tts_result['audio_url']

            # For demo purposes, simulate streaming with chunks
            demo_audio_data = "VGhpcyBpcyBhIERBWSAyMSB0ZXN0IG9mIGF1ZGlvIHN0cmVhbWluZw=="  # Base64 demo
            chunk_size = 100
            total_chunks = len(demo_audio_data) // chunk_size + 1

            def stream_audio_chunks():
                for i in range(total_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(demo_audio_data))
                    chunk = demo_audio_data[start_idx:end_idx]

                    chunk_data = {
                        'audio_chunk': chunk,
                        'chunk_index': i + 1,
                        'chunk_size': len(chunk),
                        'total_chunks': total_chunks,
                        'original_text': test_text
                    }

                    socketio.emit('audio_chunk_streamed', chunk_data, room=sid)
                    socketio.sleep(0.1)  # Small delay between chunks

                # Signal completion
                socketio.emit('audio_stream_complete', {
                    'total_chunks': total_chunks,
                    'total_size': len(demo_audio_data),
                    'original_text': test_text
                },
                              room=sid)

            # Start streaming in background
            socketio.start_background_task(stream_audio_chunks)

            emit(
                'status', {
                    'message': 'Day 21 audio streaming test started',
                    'test_text': test_text
                })
        else:
            emit('status', {
                'error': 'Failed to generate test audio for Day 21 streaming'
            })

    # Day 22: Test streaming audio playback
    elif action == 'test_day22_playback':
        logger.info("DAY 22: Testing streaming audio playback functionality")

        test_text = "This is a Day 22 test of seamless audio playback. The audio should start playing as chunks arrive for real-time streaming experience."

        # Generate actual TTS audio
        tts_result = tts_service.generate_speech(test_text)

        if tts_result['success']:
            try:
                # Read the actual audio file and stream it
                if 'filename' in tts_result:
                    audio_path = os.path.join(app.instance_path, 'static',
                                              'audio', tts_result['filename'])
                    if os.path.exists(audio_path):
                        with open(audio_path, 'rb') as f:
                            audio_data = f.read()

                        # Convert to base64 for streaming
                        import base64
                        audio_base64 = base64.b64encode(audio_data).decode(
                            'utf-8')

                        # Stream in chunks
                        chunk_size = 8192  # 8KB chunks
                        total_chunks = len(audio_base64) // chunk_size + 1

                        def stream_real_audio():
                            for i in range(total_chunks):
                                start_idx = i * chunk_size
                                end_idx = min((i + 1) * chunk_size,
                                              len(audio_base64))
                                chunk = audio_base64[start_idx:end_idx]

                                chunk_data = {
                                    'audio_chunk': chunk,
                                    'chunk_index': i + 1,
                                    'chunk_size': len(chunk),
                                    'total_chunks': total_chunks,
                                    'original_text': test_text,
                                    'is_real_audio': True
                                }

                                socketio.emit('audio_chunk_streamed',
                                              chunk_data,
                                              room=sid)
                                socketio.sleep(0.2)  # Simulate network delay

                            # Signal completion
                            socketio.emit('audio_stream_complete', {
                                'total_chunks': total_chunks,
                                'total_size': len(audio_base64),
                                'original_text': test_text,
                                'is_real_audio': True
                            },
                                          room=sid)

                        # Start streaming
                        socketio.start_background_task(stream_real_audio)

                        emit(
                            'status', {
                                'message':
                                'Day 22 streaming audio playback test started',
                                'test_text': test_text
                            })
                        return

            except Exception as e:
                logger.error(
                    f"Error reading audio file for streaming: {str(e)}")

            # Fallback to demo streaming if actual audio file reading fails
            demo_audio_data = "VGhpcyBpcyBhIERBWSAyMiB0ZXN0IG9mIGF1ZGlvIHBsYXliYWNr"
            chunk_size = 100
            total_chunks = len(demo_audio_data) // chunk_size + 1

            def stream_demo_audio():
                for i in range(total_chunks):
                    start_idx = i * chunk_size
                    end_idx = min((i + 1) * chunk_size, len(demo_audio_data))
                    chunk = demo_audio_data[start_idx:end_idx]

                    chunk_data = {
                        'audio_chunk': chunk,
                        'chunk_index': i + 1,
                        'chunk_size': len(chunk),
                        'total_chunks': total_chunks,
                        'original_text': test_text
                    }

                    socketio.emit('audio_chunk_streamed', chunk_data, room=sid)
                    socketio.sleep(0.1)

                socketio.emit('audio_stream_complete', {
                    'total_chunks': total_chunks,
                    'total_size': len(demo_audio_data),
                    'original_text': test_text
                },
                              room=sid)

            socketio.start_background_task(stream_demo_audio)

            emit(
                'status', {
                    'message':
                    'Day 22 demo streaming audio playback test started',
                    'test_text': test_text
                })
        else:
            emit(
                'status',
                {'error': 'Failed to generate test audio for Day 22 playback'})


if __name__ == '__main__':
    import socket
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    # Find available port starting from 5000
    port = 5000
    while is_port_in_use(port) and port < 5010:
        port += 1

    print("Starting VoxAura - Complete Voice Conversational Agent")
    print("=" * 60)
    print("🎯 COMPLETE FEATURES:")
    print("  • ✅ Real-time Speech-to-Text (AssemblyAI)")
    print("  • ✅ Advanced Turn Detection")
    print("  • ✅ Streaming LLM Responses (Google Gemini)")
    print("  • ✅ Murf TTS Integration with Fallback")
    print("  • ✅ Audio Data Streaming to Client")
    print("  • ✅ Seamless Audio Playback")
    print("  • ✅ Complete Conversation Pipeline")
    print("  • ✅ Chat History Management")
    print("  • ✅ Multi-modal Input (Voice + Text)")
    print("  • ✅ Error Handling & Fallbacks")
    print(
        "  • 🌤️ SPECIAL SKILL: Enhanced Weather (hourly, air quality, alerts, clothing)"
    )
    print("  • 🔍 SPECIAL SKILL: Web Search")
    print(
        "  • 📚 SPECIAL SKILL: Study/Work Assistant (summarize, explain, quiz, PDF processing)"
    )
    print("  • 🎭 Enhanced Persona Voice Characteristics")
    print("=" * 60)

    check_api_configuration() # Display initial configuration status
    print("=" * 60)

    # Run the application
    try:
        print(f"🚀 Starting server on port {port}")
        app.run(debug=True, host='0.0.0.0', port=port, threaded=True)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        print("❌ Server startup failed. Check the logs for details.")