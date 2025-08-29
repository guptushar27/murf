
# Weather Analysis Skill - API Setup Guide

## 🌤️ Overview
This guide will help you set up the enhanced Weather Analysis Skill for your AI voice assistant. The skill provides comprehensive weather reports including current conditions, forecasts, air quality, alerts, and personalized recommendations.

## 🔑 API Key Setup

### Option 1: WeatherAPI.com (Recommended)
**Best for**: Comprehensive data, Indian cities, weather alerts

1. Visit [WeatherAPI.com](https://www.weatherapi.com/signup.aspx)
2. Create a free account
3. Go to your dashboard and copy your API key
4. In Replit Secrets panel, add: `WEATHER_API_KEY=your_key_here`

**Free Tier Limits**: 1 million calls/month, all features included

**Features**:
- ✅ Current weather conditions
- ✅ Hourly forecast (up to 10 days)
- ✅ Daily forecast (up to 10 days) 
- ✅ Air quality data
- ✅ Weather alerts
- ✅ Excellent Indian city coverage
- ✅ Historical weather data

### Option 2: OpenWeatherMap (Backup)
**Best for**: Backup option, global coverage

1. Visit [OpenWeatherMap](https://openweathermap.org/api)
2. Sign up for free account
3. Get your API key from the dashboard
4. In Replit Secrets panel, add: `OPENWEATHER_API_KEY=your_key_here`

**Free Tier Limits**: 1,000 calls/day, 60 calls/minute

## 🌍 Indian Cities Support

The enhanced weather service includes specific support for Indian cities:

### Supported Name Variations
```
Mumbai (Bombay) ✅
Kolkata (Calcutta) ✅  
Chennai (Madras) ✅
Bengaluru (Bangalore) ✅
Pune (Poona) ✅
Hyderabad ✅
Ahmedabad ✅
Surat ✅
Jaipur ✅
Lucknow ✅
Kanpur ✅
Nagpur ✅
Visakhapatnam (Vizag) ✅
Indore ✅
Thane ✅
Bhopal ✅
Patna ✅
Vadodara (Baroda) ✅
Ghaziabad ✅
Ludhiana ✅
Agra ✅
Nashik ✅
Faridabad ✅
Meerut ✅
Rajkot ✅
Kalyan-Dombivli ✅
Vasai-Virar ✅
Varanasi ✅
Srinagar ✅
Dhanbad ✅
```

### Regional Format Support
- "Delhi NCR"
- "Greater Mumbai" 
- "Bangalore Urban"
- "Chennai Metropolitan"

## 📊 Weather Data Structure

### Current Conditions
```json
{
  "temperature": 28,
  "feels_like": 32,
  "condition": "Partly Cloudy",
  "humidity": 65,
  "wind_speed": 12.5,
  "wind_direction": "SW",
  "pressure": 1013,
  "visibility": 10,
  "uv_index": 7,
  "is_day": 1
}
```

### Hourly Forecast (Next 12 Hours)
```json
[
  {
    "time": "02 PM",
    "temperature": 29,
    "feels_like": 33,
    "condition": "Sunny",
    "precipitation_chance": 10,
    "humidity": 60,
    "wind_speed": 15.2
  }
]
```

### Daily Forecast (Next 3 Days)
```json
[
  {
    "date": "Monday, January 20",
    "max_temp": 32,
    "min_temp": 22,
    "condition": "Partly Cloudy",
    "precipitation_chance": 20,
    "humidity": 65,
    "wind_speed": 12.0
  }
]
```

### Air Quality Index
```json
{
  "aqi_value": 2,
  "level": "Moderate",
  "health_advice": "Air quality is acceptable for most people.",
  "pm2_5": 25,
  "pm10": 45,
  "o3": 80,
  "no2": 35
}
```

### Weather Alerts
```json
[
  {
    "title": "High Temperature Warning",
    "severity": "Moderate",
    "description": "Temperatures expected to reach 42°C...",
    "effective": "2025-01-20 10:00",
    "expires": "2025-01-21 18:00",
    "areas": "Mumbai Metropolitan Region"
  }
]
```

## 🎯 Voice Assistant Integration

### Sample Voice Commands
```
"What's the weather in Mumbai?"
"Give me a complete weather report for Delhi"
"Hourly forecast and air quality for Bangalore"
"Weather analysis for Chennai with clothing recommendations"
"Any weather alerts for Jaipur?"
"Detailed weather conditions for outdoor activities in Pune"
```

### Response Examples

**Basic Request**:
```
Input: "Weather in Mumbai"
Output: "Here's your comprehensive weather analysis for Mumbai, Maharashtra in India: Current conditions show 28°C with partly cloudy skies, feeling like 32°C. Humidity at 65% with southwest winds at 12 m/s. Next 12 hours: gradually increasing to 31°C by evening with 20% rain chance. Air quality is moderate - acceptable for most outdoor activities. Recommendations: Light cotton clothing, sunscreen recommended, stay hydrated. Is there anything specific about the weather you'd like me to explain further?"
```

**Pirate Persona**:
```
Input: "Weather forecast for Chennai" (Pirate mode)
Output: "Ahoy! Here be the complete weather treasure map for Chennai, Tamil Nadu in India! Right now, matey, the temperature be 30 degrees with sunny skies, feelin' like 34 degrees on yer weathered skin. The next few hours on the horizon show temperatures risin' to 32 degrees with clear sailin' ahead! Air quality be moderate for breathin', perfect for adventures ashore! Captain's recommendations: Dress light as a feather, don't forget yer sun hat and plenty of water, matey!"
```

## 🚀 Testing Your Setup

### Test Commands in Python
```python
# Test the weather service
from services.weather_service import WeatherService

weather_service = WeatherService()

# Test Indian city
result = weather_service.get_comprehensive_weather_analysis("Mumbai")
print("Mumbai Weather:", result['success'])

# Test with old city name  
result = weather_service.get_comprehensive_weather_analysis("Bombay")
print("Bombay->Mumbai:", result['location_info']['name'])

# Test error handling
result = weather_service.get_comprehensive_weather_analysis("InvalidCity123")
print("Error handling:", result['success'])
```

### Test via Voice Assistant
1. Start your voice assistant
2. Say: "What's the weather in Delhi?"
3. Expected: Full weather analysis with current, hourly, daily, air quality, and recommendations
4. Test error: "Weather in XYZ123" → Should ask for valid location

## 🔧 Troubleshooting

### Common Issues

**Issue**: "Location not found" for valid Indian city
**Solution**: 
- Try major city spelling: "Bengaluru" instead of "Bangalore"  
- Add state: "Jaipur, Rajasthan"
- Check API key is correctly set in Secrets

**Issue**: No weather alerts showing
**Solution**:
- WeatherAPI.com provides better alert coverage for India
- Ensure `alerts=yes` parameter is set in API calls
- Some regions may not have active alerts

**Issue**: Air quality data missing
**Solution**:
- WeatherAPI.com: Ensure `aqi=yes` parameter  
- OpenWeatherMap: Requires separate air pollution API call
- Mock data will be used if real data unavailable

**Issue**: TTS response too long
**Solution**:
- Response automatically truncated at 3000 characters
- Hourly forecast limited to 6 hours for TTS
- Daily forecast limited to 3 days

## 📈 Performance Tips

1. **Cache Results**: Weather data can be cached for 10-15 minutes
2. **Fallback Strategy**: Always have mock data ready for demos
3. **Rate Limits**: Monitor API usage in dashboard
4. **Error Handling**: Always provide helpful error messages
5. **Indian Cities**: Use normalized city names for better recognition

## 🎭 Persona Customization

The weather skill supports different personas:

- **Default**: Professional, clear weather reporting
- **Pirate**: Nautical themed with "Arrr!" and sailing metaphors
- **Custom**: Add your own persona in the `format_weather_analysis_response` method

## 📱 API Rate Limits & Costs

### WeatherAPI.com Free Tier
- 1 million requests/month
- Real-time weather data
- 10-day forecast
- Weather alerts
- Air quality data
- No credit card required

### OpenWeatherMap Free Tier  
- 1,000 requests/day
- 60 requests/minute
- Current weather + 5-day forecast
- Limited air quality calls
- Upgrade required for alerts

Choose WeatherAPI.com for production use with comprehensive Indian weather data and generous free tier limits.
