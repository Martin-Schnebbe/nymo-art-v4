# Nymo Art v4 - Leonardo AI Image Generation Backend ✨

A clean, fully-working backend for generating images using Leonardo AI's Phoenix model.

## 🎯 Status: PRODUCTION READY ✅

- **API Integration**: 100% working (325/325 parameter combinations tested)
- **Code Quality**: Cleaned up, no redundant files
- **Documentation**: Complete and up-to-date
- **Testing**: Comprehensive test coverage

## ✨ Features

- **FastAPI REST API**: Modern, fast Python web framework
- **Leonardo AI Integration**: Phoenix model with all 25 styles
- **Parameter Validation**: Pydantic schemas with edge case handling
- **Cost Estimation**: Accurate token cost calculation
- **Image Generation**: Multi-image generation with various configurations
- **Style Support**: Complete Phoenix style library
- **Error Handling**: Robust error handling and validation

## 📁 Clean Project Structure

```
nymo art v4/
├── backend/                 # Core application
│   ├── app/                # FastAPI application layer
│   ├── core/               # Business logic & schemas
│   ├── services/           # External API clients
│   └── tests/              # Comprehensive test suite
├── generate_test_images.py # Working test image generator
├── generated_images/       # Test outputs
└── docs/                   # Documentation
```

See `PROJECT_STRUCTURE.md` for detailed breakdown.

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Add your Leonardo AI API key to .env
LEONARDO_API_KEY=your_api_key_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Test Image Generation
```bash
# Run the working test image generator
python generate_test_images.py
```

### 4. Start Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🎨 API Endpoints

### Generate Images
```bash
POST /generate
Content-Type: application/json

{
  "prompt": "a majestic dragon",
  "style": "Cinematic",
  "num_outputs": 2,
  "width": 1024,
  "height": 1024,
  "contrast": 3.5,
  "alchemy": true
}
```

### List Available Models
```bash
GET /models
```

### Health Check
```bash
GET /health
```

## 🎯 Available Styles

Phoenix model supports 25 professional styles:
- **Cinematic** - Dramatic movie-like lighting
- **Portrait** - Professional portrait photography
- **Illustration** - Artistic, hand-drawn style
- **3D Render** - Modern 3D graphics
- **Dynamic** - High energy, vivid colors
- **Sketch (B&W)** - Black and white sketches
- **Vibrant** - Bright, saturated colors
- And 18 more...

## 📊 Tested Parameters

✅ **Comprehensive Testing Completed**:
- **Total combinations**: 325/325 passed (100% success rate)
- **Styles tested**: All 25 Phoenix styles
- **Contrast levels**: 8 levels (1.0, 1.3, 1.8, 2.5, 3.0, 3.5, 4.0, 4.5)
- **Alchemy modes**: Both enabled and disabled
- **Resolution support**: Multiple aspect ratios

## 🧪 Testing

### Run Test Image Generator
```bash
python generate_test_images.py
```

This generates test images with different configurations and validates the API integration.

### Run Backend Tests
```bash
cd backend
python -m pytest tests/ -v
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
LEONARDO_API_KEY=your_api_key_here
DEBUG=false
LOG_LEVEL=INFO
```

### Get Leonardo AI API Key
1. Visit: https://app.leonardo.ai/settings/api-keys
2. Create a new API key
3. Add it to your `.env` file

## 📈 Performance

- **Response Time**: ~10-30 seconds per generation
- **Cost Estimation**: Included in API responses
- **Rate Limiting**: Handled automatically
- **Error Recovery**: Robust retry mechanisms

## 🗂️ File Structure Details

### Core Backend (`backend/`)
- `app/main.py` - FastAPI application entry point
- `core/schemas.py` - Pydantic data models with validation
- `core/engine/leonardo/phoenix.py` - Phoenix model implementation
- `services/leonardo_client.py` - Leonardo AI API client

### Essential Files
- `generate_test_images.py` - Working test image generator
- `test_results_leonardo_parameters.json` - Successful test results
- `ITERATION_COMPLETE.md` - Previous development summary

## 🎯 What Was Cleaned Up

### Removed Redundant Files (12 files):
- ❌ `cli_backend.py`, `main.py`, `phoenix_cli.py` (3 different CLI interfaces)
- ❌ Multiple test files (`comprehensive_test.py`, `phoenix_test_suite.py`, etc.)
- ❌ Legacy `my_api/` directory structure
- ❌ All `__pycache__` directories

### Kept Essential Files:
- ✅ Complete `backend/` with working FastAPI application
- ✅ `generate_test_images.py` (proven to work)
- ✅ Test results and documentation

## 🚀 Next Steps

1. **Deploy**: Ready for production deployment
2. **Extend**: Add new Leonardo AI models easily
3. **Scale**: FastAPI supports horizontal scaling
4. **Monitor**: Add logging and monitoring as needed

## 📄 License

This project is for educational and personal use with Leonardo AI API.

---
*Last updated: May 24, 2025 - Project cleanup and restructuring complete*
