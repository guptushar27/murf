# Overview

VoxAura AI is a sophisticated voice-enabled conversational agent that provides ChatGPT-like interactions through both voice and text modalities. The system combines real-time speech recognition, intelligent AI conversations, neural text-to-speech synthesis, and specialized skills like weather analysis, web search, document processing, and study assistance. The application features a modern glassmorphism interface with animated backgrounds, real-time WebSocket communication, and comprehensive chat management capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Modern Web Interface**: ChatGPT-style interface with glassmorphism design and animated star backgrounds
- **WebSocket Integration**: Real-time bidirectional communication using Flask-SocketIO for streaming audio and live responses
- **Responsive Design**: Mobile-friendly interface with collapsible sidebar and interactive voice orb
- **Progressive Enhancement**: Graceful degradation when services are unavailable with fallback interfaces

## Backend Architecture
- **Flask Web Framework**: Python web application with modular service architecture
- **Service-Oriented Design**: Separated services for STT (Speech-to-Text), LLM (Language Models), TTS (Text-to-Speech), and specialized skills
- **WebSocket Services**: Real-time audio streaming, transcription, and response generation
- **Error Handling**: Comprehensive fallback mechanisms for each service layer

## Core Services
- **Speech Recognition**: AssemblyAI integration with real-time streaming and turn detection
- **Language Models**: Google Gemini 2.0 for intelligent conversations with special skill routing
- **Text-to-Speech**: Murf AI premium voices with gTTS fallback for voice synthesis
- **Document Processing**: PDF analysis and text extraction using PyPDF2

## Specialized AI Skills
- **Weather Analysis**: Comprehensive weather data with forecasts, air quality, and clothing suggestions
- **Web Search**: DuckDuckGo integration for real-time information retrieval
- **Study Assistant**: Document summarization, concept explanation, and quiz generation
- **PDF Processing**: File upload, text extraction, and intelligent document analysis

## Data Management
- **Chat History**: Persistent conversation storage with search and session management
- **File Handling**: Secure upload processing with validation and size limits
- **Session Management**: User session tracking with WebSocket state management

## Authentication & Security
- **API Key Management**: Dynamic configuration through environment variables and settings panel
- **Request Validation**: Pydantic models for comprehensive input/output validation
- **File Security**: Upload validation with size limits and type checking

# External Dependencies

## Core AI Services
- **AssemblyAI**: Real-time speech recognition and transcription services
- **Google Gemini**: Advanced language model for conversational AI responses
- **Murf AI**: Premium neural text-to-speech voice synthesis (with gTTS fallback)

## Search & Information Services
- **DuckDuckGo API**: Web search functionality without API key requirements
- **OpenWeatherMap/WeatherAPI**: Comprehensive weather data and forecasting

## Python Framework & Libraries
- **Flask**: Web application framework with SocketIO for real-time communication
- **Pydantic**: Data validation and serialization for API requests/responses
- **SQLAlchemy**: Database ORM for data persistence
- **WebSockets**: Real-time bidirectional communication protocol

## Document Processing
- **PyPDF2**: PDF text extraction and processing
- **python-docx**: Microsoft Word document processing
- **html2text**: Web content extraction for study assistant features

## Audio & Media
- **WebRTC**: Browser-based audio capture and streaming
- **MediaRecorder API**: Client-side audio recording and processing