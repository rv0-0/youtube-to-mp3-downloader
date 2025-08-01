# 🧪 **YouTube to MP3 Test Suite Guide**

This project includes a comprehensive test suite to validate all functionality!

## 🚀 **Quick Start Testing**

### Option 1: Interactive Test Menu
```cmd
run_all_tests.bat
```
Choose from:
1. **Unit Tests Only** (Fast - 30 seconds)
2. **API Tests Only** (Requires running server)
3. **Full Test Suite** (Unit + API tests)
4. **Quick API Tests** (No downloads)

### Option 2: Individual Test Scripts
```cmd
# Unit tests only
python test_units.py

# Full API tests (requires server running)
python test_api.py

# Quick API tests (no downloads)
python test_api.py --quick
```

## 🔬 **Unit Tests** (`test_units.py`)

Tests core functionality without requiring the API server:

### Test Categories:
- **✅ Import Tests**: Verify all modules can be imported
- **✅ Initialization Tests**: Test downloader class creation
- **✅ Validation Tests**: URL, quality, worker count validation
- **✅ Helper Tests**: Progress calculation, file formatting
- **✅ Configuration Tests**: Parameter validation

### Sample Output:
```
🧪 Running Unit Tests
==================================================
test_advanced_downloader_import ... ok
test_smart_downloader_initialization ... ok
test_url_validation ... ok
test_quality_validation ... ok
...
Tests Run: 14
✅ Passed: 14
Success Rate: 100.0%
```

## 📡 **API Tests** (`test_api.py`)

Tests all REST API endpoints with real functionality:

### Test Categories:
- **🌐 Connectivity**: Health check, root endpoint
- **📊 Info Retrieval**: Video information without downloading
- **⬇️ Downloads**: Single and batch downloads
- **📈 Monitoring**: Task status and progress tracking
- **📁 File Management**: List, download, delete files
- **📤 Upload**: URL file upload functionality

### Test Flow:
1. **Server Health Check** - Verify API is running
2. **Video Info Test** - Get metadata without downloading
3. **Single Download** - Test basic download functionality
4. **Batch Download** - Test multiple video downloads
5. **Progress Monitoring** - Track download status
6. **File Operations** - List, download, delete files
7. **Upload Testing** - Test URL file upload

### Sample Output:
```
🧪 Starting YouTube to MP3 API Tests
==================================================
📡 Testing Basic Connectivity...
✅ PASS | Health Check
      └─ Server is healthy. Active downloads: 0
      └─ Status: 200, Time: 0.05s

⬇️ Testing Download Endpoints...
✅ PASS | Single Download
      └─ Task started: a1b2c3d4...
      └─ Status: 200, Time: 0.12s

⏳ Waiting for downloads to complete...
   └─ Task a1b2c3d4... completed

📁 Testing File Management...
✅ PASS | List Files
      └─ Found 2 MP3 files
      └─ Status: 200, Time: 0.03s

📋 TEST SUMMARY
Total Tests: 12
✅ Passed: 12
Success Rate: 100.0%
```

## 🎯 **Test Modes**

### 1. Quick Tests (`--quick` flag)
- **Duration**: ~30 seconds
- **Coverage**: Connectivity, info retrieval, file management
- **No Downloads**: Safe for rapid testing
- **Perfect for**: Development, CI/CD pipelines

### 2. Full Tests (default)
- **Duration**: 3-5 minutes
- **Coverage**: All endpoints including real downloads
- **Complete validation**: End-to-end functionality
- **Perfect for**: Release validation, thorough testing

## 📊 **Test Results**

### JSON Export
All API tests export detailed results to `test_results.json`:
```json
{
  "test": "Single Download",
  "success": true,
  "details": "Task started: a1b2c3d4...",
  "status_code": 200,
  "response_time": 0.12,
  "timestamp": "2025-08-01 15:30:45"
}
```

### Console Output
Real-time test progress with:
- ✅ Pass/❌ Fail indicators
- Detailed error messages
- Response times and status codes
- Progress summaries

## 🔧 **Advanced Usage**

### Custom API URL
```cmd
python test_api.py --url http://custom-host:8000
```

### Verbose Unit Tests
```cmd
python test_units.py --verbose
```

### CI/CD Integration
```bash
# Exit code 0 = success, 1 = failure
python test_units.py
echo $?  # Check exit code

python test_api.py --quick
echo $?  # Check exit code
```

## ⚠️ **Prerequisites**

### For Unit Tests:
- ✅ Python virtual environment activated
- ✅ Core modules (youtube_to_mp3*.py) present

### For API Tests:
- ✅ FastAPI server running (`start_api_server.bat`)
- ✅ All dependencies installed
- ✅ Internet connection (for real downloads in full mode)

## 🎉 **Test Coverage Summary**

### ✅ **What's Tested:**
- All 11 REST API endpoints
- All 3 download modes (basic, advanced, smart)
- File upload/download/delete operations
- Task creation and monitoring
- Progress tracking and status updates
- Error handling and edge cases
- URL and parameter validation
- Configuration validation

### 🎯 **Quality Metrics:**
- **Unit Tests**: 100% success rate
- **API Coverage**: All endpoints tested
- **Error Handling**: Comprehensive validation
- **Performance**: Response time monitoring
- **Reliability**: Automatic cleanup and retry logic

## 🚀 **Next Steps**

After running tests:
1. **✅ All Pass**: Your setup is perfect!
2. **❌ Failures**: Check error messages and fix issues
3. **🔧 Development**: Use quick tests during development
4. **📦 Deployment**: Run full test suite before releases

The test suite ensures your YouTube to MP3 API is robust, reliable, and ready for production! 🎊
