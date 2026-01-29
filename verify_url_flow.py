import subprocess
import time
import requests
import sys
import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer

# 1. Setup Mock Content Server
class MockContentHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        content = """
        <html>
        <head><title>Test Article</title></head>
        <body>
            <nav>Menu</nav>
            <div class="main-content">
                <h1>我的第一篇文章</h1>
                <p>你好, 我是学生. 这是一个测试.</p>
            </div>
            <footer>Copyright</footer>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

def start_mock_server():
    server = HTTPServer(('localhost', 8002), MockContentHandler)
    server.serve_forever()

def run_verification():
    # Start Mock Content Server in a thread (daemon so it dies with script)
    mock_thread = threading.Thread(target=start_mock_server, daemon=True)
    mock_thread.start()
    print("Mock Content Server started on :8002")

    # Start API Server in subprocess
    print("Starting API server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for API startup
        time.sleep(4)
        
        # Payload pointing to our mock server
        # Note: "这是" is in the text. Our fix from before should handle it.
        # "我的" (My - Unknown/HSK1 depending on dictionary), "第一" (First - HSK2?), "篇" (MW - HSK4?), "文章" (Article - HSK4?)
        # "你好" (HSK1), "我" (HSK1), "是" (HSK1), "学生" (HSK1).
        # "这" (HSK1 - we added it), "是" (HSK1), "一个" (HSK2/4?), "测试" (Test - HSK4+?)
        payload = {
            "url": "http://localhost:8002/test-article"
        }
        
        url = "http://127.0.0.1:8001/api/v1/analyze/url"
        print(f"Sending request to {url} with: {payload}")
        
        response = requests.post(url, json=payload, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            # Verify Scraper worked
            if data['title'] == "Test Article" and data['url'] == payload['url']:
                print("SCRAPER VERIFICATION: PASSED")
            else:
                print("SCRAPER VERIFICATION: FAILED (Title/URL mismatch)")
                return False

            # Verify Analyzer worked (Check for non-zero tokens)
            if data['total_tokens'] > 0:
                print("ANALYZER VERIFICATION: PASSED")
                return True
            else:
                print("ANALYZER VERIFICATION: FAILED (No tokens analyzed)")
                return False
        else:
            print("VERIFICATION FAILED: Non-200 response")
            # print stderr for debug
            # print(proc.stderr.read().decode())
            return False
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        print("Stopping API server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

if __name__ == "__main__":
    success = run_verification()
    if not success:
        sys.exit(1)
