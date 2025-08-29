
# 🎙️ VoxAura AI - Complete Voice Conversational Agent

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-green.svg)](https://flask.palletsprojects.com)
[![AI-Powered](https://img.shields.io/badge/AI-Powered-purple.svg)](https://github.com)
[![Voice-Enabled](https://img.shields.io/badge/Voice-Enabled-orange.svg)](https://github.com)

> A sophisticated AI-powered voice conversational agent with ChatGPT-like interface, featuring real-time speech recognition, intelligent conversations, neural text-to-speech, document analysis, and complete chat history management.

## 🚀 Key Features

### 🎯 Core Voice Capabilities
- **🎤 Real-time Voice Recording** - High-quality browser-based audio capture with WebSocket streaming
- **🧠 Advanced Speech Recognition** - Professional transcription using AssemblyAI with turn detection
- **🤖 Intelligent Conversations** - Context-aware responses powered by Google Gemini 2.0
- **🗣️ Neural Text-to-Speech** - Premium voice synthesis with Murf AI and gTTS fallback
- **🔄 Multi-Modal Input** - Seamless voice and text interactions
- **📡 Real-time Communication** - WebSocket-powered streaming for instant responses

### 🎨 Modern Interface Features
- **📱 Responsive Sidebar** - Collapsible sidebar with chat history, search, and new chat functionality
- **✨ Animated Star Background** - Interactive starfield with mouse-responsive movement and pulsing effects
- **🌊 Wave Processing Animation** - Beautiful wave effects during AI processing
- **🎛️ Interactive Voice Orb** - Animated circular voice interface with visual feedback
- **🔮 Glassmorphism Effects** - Modern translucent design with backdrop blur
- **🎭 Dynamic Personas** - Multiple AI personalities (Default, Pirate) with unique voices

### 📄 Document Intelligence
- **📁 PDF Processing** - Extract text, summarize, and analyze PDF documents
- **📝 Document Analysis** - Support for PDF, DOC, DOCX, and TXT files
- **🔍 Smart Queries** - Ask questions about uploaded documents
- **📊 Content Extraction** - Key points, concepts, and question generation
- **💡 AI-Powered Insights** - Intelligent document summarization and analysis

### 🗂️ Chat Management
- **💾 Persistent Chat History** - All conversations saved locally with full context
- **🔍 Search Functionality** - Find past conversations instantly
- **➕ New Chat Sessions** - Start fresh conversations while preserving history
- **📋 Session Management** - Switch between multiple chat sessions seamlessly
- **💭 Smart Previews** - Quick preview of conversation topics in sidebar

### 🛠️ Technical Excellence
- **🏗️ Modular Architecture** - Clean separation of services with robust error handling
- **🔒 API Key Management** - Dynamic configuration through settings panel
- **📊 Request Validation** - Pydantic models for API request/response validation
- **🔍 Comprehensive Logging** - Structured logging for debugging and monitoring
- **⚡ Performance Optimized** - Efficient audio processing and streaming
- **🌐 WebSocket Integration** - Real-time bidirectional communication

## 🔧 API Services Integration

### Primary AI Services
- **AssemblyAI** - Professional speech-to-text with real-time streaming
- **Google Gemini 2.0** - Advanced language model for intelligent conversations
- **Murf AI** - Premium neural text-to-speech synthesis
- **WeatherAPI** - Enhanced weather information with forecasts and alerts

### Fallback Services
- **Google TTS (gTTS)** - Reliable text-to-speech fallback
- **DuckDuckGo Search** - Web search capabilities (no API key required)
- **Built-in PDF Processing** - Document analysis without external dependencies

## 📦 Quick Setup

### 1. Environment Setup
Create a `.env` file in the root directory:

```env
# Required API Keys
ASSEMBLYAI_API_KEY=your_assemblyai_api_key_here
GEMINI_API_KEY=your_google_gemini_api_key_here
MURF_API_KEY=your_murf_ai_api_key_here

# Optional Services
WEATHER_API_KEY=your_weather_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Application Settings
FLASK_SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True
```

### 2. Installation & Run
```bash
# Clone and navigate to directory
git clone <your-repo-url>
cd voxaura-voice-agent

# Run the application (dependencies auto-install)
python main.py
```

The app will be available at `http://localhost:5000`

### 3. API Keys Setup

#### AssemblyAI (Speech Recognition)
1. Visit [AssemblyAI](https://www.assemblyai.com/) and create account
2. Get API key from dashboard
3. Add to `.env` or configure in app settings

#### Google Gemini (AI Conversations)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create API key
3. Add to `.env` or configure in app settings

#### Murf AI (Premium Voice)
1. Sign up at [Murf AI](https://murf.ai/)
2. Get API credentials
3. Add to `.env` or configure in app settings

## 🎯 How to Use

### Voice Conversations
1. **Click the microphone orb** to start recording
2. **Speak naturally** - the app detects when you stop talking
3. **Watch the animations** - stars pulse and waves flow during processing
4. **Listen to responses** - AI responds with natural voice synthesis
5. **View in chat** - All conversations appear in ChatGPT-style interface

### Text Conversations
1. **Type in the input box** at the bottom
2. **Press Enter** or click send button
3. **Get instant responses** with optional audio playback
4. **Use voice commands** by clicking the mic button next to input

### Document Analysis
1. **Click the attachment button** next to text input
2. **Upload PDF, DOC, DOCX, or TXT** files (max 10MB)
3. **Choose analysis type**: Summarize, Q&A, Key Points, Concepts
4. **Ask questions** about the document content
5. **Get AI insights** based on document analysis

### Chat Management
1. **Open sidebar** by clicking the hamburger menu (☰)
2. **Start new chat** with the "+" button
3. **Browse chat history** - all past conversations saved
4. **Search conversations** using the search box
5. **Switch between chats** by clicking on history items

### Settings & Configuration
1. **Click settings icon** to open configuration panel
2. **Add API keys** for enhanced features
3. **Choose AI personas** (Default, Pirate)
4. **Configure voice settings** and preferences

## 🏗️ Project Architecture

```
voxaura-voice-agent/
├── 📁 services/                    # AI service integrations
│   ├── stt_service.py             # Speech-to-Text (AssemblyAI)
│   ├── llm_service.py             # Language Model (Gemini)
│   ├── tts_service.py             # Text-to-Speech (Murf + gTTS)
│   ├── pdf_service.py             # Document processing
│   ├── websocket_service.py       # Real-time communication
│   └── weather_service.py         # Weather integration
├── 📁 static/                      # Frontend assets
│   ├── css/custom.css             # Styling and animations
│   └── js/                        
│       ├── main.js                # Main application logic
│       ├── websocket-client.js    # WebSocket handling
│       └── streaming-audio.js     # Audio processing
├── 📁 templates/                   # HTML templates
│   └── index.html                 # Main application interface
├── 📁 schemas/                     # Data validation
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
└── README.md                      # This documentation
```

## 🔍 Features Deep Dive

### Real-time Voice Processing Pipeline
```
Voice Input → WebSocket Stream → AssemblyAI STT → Gemini AI → Murf TTS → Audio Output
     ↑                                                                         ↓
Turn Detection ← Real-time Transcription → Context Management → Response Streaming
```

### Document Processing Workflow
```
File Upload → Text Extraction → Content Analysis → AI Processing → Formatted Response
     ↑                                                                    ↓
Validation ← Format Detection → Smart Chunking → Context Preservation → User Display
```

### Chat History Management
```
User Message → Session Storage → Local Persistence → Search Indexing → Quick Retrieval
     ↑                                                                      ↓
Auto-save ← Context Maintenance → History Organization → Smart Previews → Sidebar Display
```

## 🎨 UI/UX Features

### Visual Effects
- **Animated Star Field**: 200+ stars with physics-based movement
- **Interactive Orb**: Pulsing voice control with gradient animations
- **Wave Processing**: Multi-colored wave animations during AI thinking
- **Glassmorphism**: Translucent elements with backdrop blur effects
- **Smooth Transitions**: CSS3 animations for all interactions

### Responsive Design
- **Mobile-Optimized**: Touch-friendly controls and responsive layout
- **Tablet Support**: Adaptive sidebar and optimized spacing
- **Desktop Enhanced**: Full-featured experience with keyboard shortcuts
- **Cross-Browser**: Tested on Chrome, Firefox, Safari, and Edge

### Accessibility
- **Keyboard Navigation**: Full keyboard accessibility support
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast**: Readable color schemes and clear indicators
- **Error Handling**: Clear error messages and recovery options

## 🔧 Advanced Configuration

### Environment Variables
```env
# Core Services
ASSEMBLYAI_API_KEY=           # Speech recognition
GEMINI_API_KEY=              # AI conversations
MURF_API_KEY=                # Premium voice synthesis

# Enhanced Features
WEATHER_API_KEY=             # Weather information
OPENWEATHER_API_KEY=         # Alternative weather service

# Application Settings
FLASK_SECRET_KEY=            # Session security
FLASK_ENV=development        # Environment mode
FLASK_DEBUG=True             # Debug mode
MAX_CONTENT_LENGTH=16777216  # 16MB file upload limit
```

### API Configuration Panel
- **Dynamic Key Management**: Add/update API keys without restart
- **Service Status**: Real-time status of all connected services
- **Fallback Configuration**: Automatic fallback when services unavailable
- **Usage Monitoring**: Track API usage and rate limits

## 🧪 Testing & Debugging

### Built-in Testing Tools
- **Component Testing**: Individual service testing interface
- **Error Simulation**: Test fallback scenarios and error handling
- **WebSocket Testing**: Real-time communication testing
- **Audio Processing**: Voice recording and playback testing

### Debugging Features
- **Comprehensive Logging**: Detailed logs for all operations
- **Error Analytics**: Structured error reporting
- **Performance Metrics**: Response times and success rates
- **Browser Console**: Client-side debugging information

## 🚀 Deployment on Replit

### Quick Deploy
1. **Fork this project** on Replit
2. **Set environment variables** in Secrets panel
3. **Click Run** to start the application
4. **Access via provided URL** for public sharing

### Production Configuration
```bash
# Auto-configures for production deployment
python main.py
```

### Environment Variables in Replit
Add these to your Replit Secrets:
- `ASSEMBLYAI_API_KEY`
- `GEMINI_API_KEY`
- `MURF_API_KEY`
- `WEATHER_API_KEY` (optional)

## 🤝 Contributing

### Development Guidelines
1. **Fork the repository** and create feature branch
2. **Follow modular architecture** patterns
3. **Add comprehensive error handling** and logging
4. **Update schemas** for new API endpoints
5. **Test with error simulation** tools
6. **Document new features** in README

### Code Structure
- **Services**: Isolated, testable service modules
- **Schemas**: Pydantic models for validation
- **Error Handling**: Graceful fallbacks and user feedback
- **Logging**: Structured logging for debugging

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AssemblyAI** - Professional speech recognition services
- **Google** - Powerful Gemini language model
- **Murf AI** - High-quality text-to-speech synthesis
- **Bootstrap** - Responsive UI framework
- **Font Awesome** - Beautiful icon library
- **WebSocket** - Real-time communication protocol

## 📞 Support & Troubleshooting

### Common Issues
1. **API Key Errors**: Configure keys in settings panel or `.env` file
2. **Microphone Access**: Ensure browser permissions for microphone
3. **WebSocket Connection**: Check firewall and proxy settings
4. **Audio Playback**: Verify browser audio permissions and settings

### Getting Help
- **Check browser console** for JavaScript errors
- **Review application logs** for service errors
- **Test individual components** using built-in testing tools
- **Verify API key configuration** in settings panel

---

**Built with ❤️ using cutting-edge AI technologies and modern web development practices**

*VoxAura AI - Where conversations meet the future*

**Features:**
✅ Real-time Voice Conversations  
✅ ChatGPT-style Interface  
✅ Document Analysis (PDF/DOC/TXT)  
✅ Chat History & Search  
✅ Multiple AI Personas  
✅ WebSocket Streaming  
✅ Animated UI Effects  
✅ Mobile Responsive  
✅ API Key Management  
✅ Error Handling & Fallbacks  

*Ready to deploy on Replit with one click!*
