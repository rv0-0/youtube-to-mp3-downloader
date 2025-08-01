"""
Comprehensive test script for YouTube to MP3 FastAPI endpoints
Tests all API functionality including downloads, file management, and task monitoring
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional
import tempfile

class YouTubeAPI_Tester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        self.downloaded_files = []
        self.task_ids = []
        
        # Test URLs (using short, copyright-free videos)
        self.test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (short)
            "https://www.youtube.com/watch?v=jNQXAC9IVRw"   # Me at the zoo (first YouTube video)
        ]
    
    def log_test(self, test_name: str, success: bool, details: str = "", response: Optional[requests.Response] = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if response:
            result["status_code"] = response.status_code
            result["response_time"] = response.elapsed.total_seconds()
        
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      └─ {details}")
        if response:
            print(f"      └─ Status: {response.status_code}, Time: {response.elapsed.total_seconds():.2f}s")
    
    def test_server_health(self):
        """Test GET /health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Health Check", 
                    True, 
                    f"Server is healthy. Active downloads: {data.get('active_downloads', 0)}", 
                    response
                )
                return True
            else:
                self.log_test("Health Check", False, f"Unexpected status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_test("Health Check", False, f"Connection failed: {str(e)}")
            return False
    
    def test_root_endpoint(self):
        """Test GET / endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Root Endpoint", 
                    True, 
                    f"API version: {data.get('version', 'Unknown')}", 
                    response
                )
                return True
            else:
                self.log_test("Root Endpoint", False, f"Status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_test("Root Endpoint", False, f"Error: {str(e)}")
            return False
    
    def test_video_info(self):
        """Test GET /info endpoint"""
        try:
            url = self.test_urls[0]
            response = self.session.get(f"{self.base_url}/info", params={"url": url})
            
            if response.status_code == 200:
                data = response.json()
                title = data.get('title', 'Unknown')
                uploader = data.get('uploader', 'Unknown')
                self.log_test(
                    "Video Info", 
                    True, 
                    f"Title: {title[:50]}... | Uploader: {uploader}", 
                    response
                )
                return True
            else:
                self.log_test("Video Info", False, f"Status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_test("Video Info", False, f"Error: {str(e)}")
            return False
    
    def test_single_download(self):
        """Test POST /download endpoint"""
        try:
            payload = {
                "url": self.test_urls[0],
                "quality": 192,
                "mode": "basic",
                "output_dir": "downloads"
            }
            
            response = self.session.post(
                f"{self.base_url}/download",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                self.task_ids.append(task_id)
                self.log_test(
                    "Single Download", 
                    True, 
                    f"Task started: {task_id[:8]}...", 
                    response
                )
                return task_id
            else:
                self.log_test("Single Download", False, f"Status code: {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_test("Single Download", False, f"Error: {str(e)}")
            return None
    
    def test_batch_download(self):
        """Test POST /batch-download endpoint"""
        try:
            payload = {
                "urls": self.test_urls,
                "quality": 128,
                "mode": "basic",
                "max_workers": 2,
                "output_dir": "downloads"
            }
            
            response = self.session.post(
                f"{self.base_url}/batch-download",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                task_id = data.get('task_id')
                self.task_ids.append(task_id)
                self.log_test(
                    "Batch Download", 
                    True, 
                    f"Batch task started: {task_id[:8]}... for {len(self.test_urls)} videos", 
                    response
                )
                return task_id
            else:
                self.log_test("Batch Download", False, f"Status code: {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_test("Batch Download", False, f"Error: {str(e)}")
            return None
    
    def test_task_status(self, task_id: str):
        """Test GET /status/{task_id} endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/status/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', 'unknown')
                progress = data.get('progress', 0)
                self.log_test(
                    "Task Status", 
                    True, 
                    f"Task {task_id[:8]}... | Status: {status} | Progress: {progress:.1f}%", 
                    response
                )
                return data
            elif response.status_code == 404:
                self.log_test("Task Status", False, "Task not found", response)
                return None
            else:
                self.log_test("Task Status", False, f"Status code: {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_test("Task Status", False, f"Error: {str(e)}")
            return None
    
    def test_all_tasks(self):
        """Test GET /tasks endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/tasks")
            
            if response.status_code == 200:
                data = response.json()
                total_tasks = data.get('total', 0)
                active_tasks = data.get('active', 0)
                completed_tasks = data.get('completed', 0)
                self.log_test(
                    "All Tasks", 
                    True, 
                    f"Total: {total_tasks} | Active: {active_tasks} | Completed: {completed_tasks}", 
                    response
                )
                return data
            else:
                self.log_test("All Tasks", False, f"Status code: {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_test("All Tasks", False, f"Error: {str(e)}")
            return None
    
    def test_list_files(self):
        """Test GET /files endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/files")
            
            if response.status_code == 200:
                data = response.json()
                files = data.get('files', [])
                total_files = data.get('total', 0)
                
                if files:
                    self.downloaded_files.extend([f['filename'] for f in files])
                
                self.log_test(
                    "List Files", 
                    True, 
                    f"Found {total_files} MP3 files", 
                    response
                )
                return files
            else:
                self.log_test("List Files", False, f"Status code: {response.status_code}", response)
                return None
                
        except Exception as e:
            self.log_test("List Files", False, f"Error: {str(e)}")
            return None
    
    def test_download_file(self, filename: str):
        """Test GET /download-file/{filename} endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/download-file/{filename}")
            
            if response.status_code == 200:
                # Check if it's actually an MP3 file
                content_type = response.headers.get('content-type', '')
                content_length = len(response.content)
                
                self.log_test(
                    "Download File", 
                    True, 
                    f"Downloaded {filename} | Size: {content_length} bytes | Type: {content_type}", 
                    response
                )
                return True
            elif response.status_code == 404:
                self.log_test("Download File", False, f"File not found: {filename}", response)
                return False
            else:
                self.log_test("Download File", False, f"Status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_test("Download File", False, f"Error: {str(e)}")
            return False
    
    def test_upload_urls(self):
        """Test POST /upload-urls endpoint"""
        try:
            # Create a temporary file with URLs
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write('\n'.join(self.test_urls))
                temp_filename = f.name
            
            # Upload the file
            with open(temp_filename, 'rb') as f:
                files = {'file': ('test_urls.txt', f, 'text/plain')}
                response = self.session.post(f"{self.base_url}/upload-urls", files=files)
            
            # Cleanup
            os.unlink(temp_filename)
            
            if response.status_code == 200:
                data = response.json()
                urls_found = data.get('urls_found', 0)
                self.log_test(
                    "Upload URLs", 
                    True, 
                    f"Uploaded file with {urls_found} URLs", 
                    response
                )
                return True
            else:
                self.log_test("Upload URLs", False, f"Status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_test("Upload URLs", False, f"Error: {str(e)}")
            return False
    
    def test_delete_file(self, filename: str):
        """Test DELETE /files/{filename} endpoint"""
        try:
            response = self.session.delete(f"{self.base_url}/files/{filename}")
            
            if response.status_code == 200:
                self.log_test(
                    "Delete File", 
                    True, 
                    f"Successfully deleted {filename}", 
                    response
                )
                return True
            elif response.status_code == 404:
                self.log_test("Delete File", False, f"File not found: {filename}", response)
                return False
            else:
                self.log_test("Delete File", False, f"Status code: {response.status_code}", response)
                return False
                
        except Exception as e:
            self.log_test("Delete File", False, f"Error: {str(e)}")
            return False
    
    def wait_for_downloads(self, max_wait_time: int = 180):
        """Wait for downloads to complete"""
        print(f"\n⏳ Waiting for downloads to complete (max {max_wait_time} seconds)...")
        
        start_time = time.time()
        completed_tasks = set()
        
        while time.time() - start_time < max_wait_time:
            all_done = True
            
            for task_id in self.task_ids:
                if task_id in completed_tasks:
                    continue
                
                status_data = self.test_task_status(task_id)
                if status_data:
                    status = status_data.get('status')
                    if status in ['completed', 'failed']:
                        completed_tasks.add(task_id)
                        print(f"   └─ Task {task_id[:8]}... {status}")
                    else:
                        all_done = False
            
            if all_done:
                print("✅ All downloads completed!")
                break
            
            time.sleep(5)  # Wait 5 seconds before checking again
        
        if not all_done:
            print("⚠️  Some downloads may still be in progress")
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🧪 Starting YouTube to MP3 API Tests")
        print("=" * 50)
        
        # Basic connectivity tests
        print("\n📡 Testing Basic Connectivity...")
        if not self.test_server_health():
            print("❌ Server is not responding. Please start the API server first.")
            return False
        
        self.test_root_endpoint()
        self.test_video_info()
        
        # Download tests
        print("\n⬇️  Testing Download Endpoints...")
        single_task = self.test_single_download()
        batch_task = self.test_batch_download()
        
        # Wait a bit for tasks to start
        time.sleep(2)
        
        # Task monitoring tests
        print("\n📊 Testing Task Monitoring...")
        if single_task:
            self.test_task_status(single_task)
        self.test_all_tasks()
        
        # File upload test
        print("\n📤 Testing File Upload...")
        self.test_upload_urls()
        
        # Wait for downloads to complete
        if self.task_ids:
            self.wait_for_downloads()
        
        # File management tests
        print("\n📁 Testing File Management...")
        files = self.test_list_files()
        
        if files and len(files) > 0:
            # Test downloading the first file
            first_file = files[0]['filename']
            self.test_download_file(first_file)
            
            # Test deleting a file (if we have multiple files)
            if len(files) > 1:
                file_to_delete = files[-1]['filename']
                self.test_delete_file(file_to_delete)
        
        # Final status check
        print("\n🔍 Final Status Check...")
        self.test_all_tasks()
        
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📋 TEST SUMMARY")
        print("=" * 50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"   └─ {result['test']}: {result['details']}")
        
        print("\n🏆 Test Results:")
        for result in self.test_results:
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {result['test']}")
        
        # Save detailed results to file
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n💾 Detailed results saved to: test_results.json")


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test YouTube to MP3 API endpoints')
    parser.add_argument('--url', default='http://localhost:8000', help='API base URL')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only (no downloads)')
    
    args = parser.parse_args()
    
    tester = YouTubeAPI_Tester(args.url)
    
    if args.quick:
        print("🏃 Running quick tests (no downloads)...")
        tester.test_server_health()
        tester.test_root_endpoint()
        tester.test_video_info()
        tester.test_list_files()
        tester.test_upload_urls()
        tester.print_summary()
    else:
        tester.run_all_tests()


if __name__ == "__main__":
    main()
