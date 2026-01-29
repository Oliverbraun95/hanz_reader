import subprocess
import time
import requests
import sys
import os

def run_verification():
    # Start the server
    # We use subprocess.Popen to run it in background
    print("Starting server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.getcwd()
    )
    
    try:
        # Wait for startup
        time.sleep(3)
        
        # Define test payload
        payload = {
            "content": "你好, 我是学生.",
            "target_level": "HSK2"
        }
        
        print(f"Sending request to http://127.0.0.1:8001/api/v1/analyze with: {payload}")
        response = requests.post("http://127.0.0.1:8001/api/v1/analyze", json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            if data['difficulty_score'] == "A1" and data['total_tokens'] > 0:
                print("VERIFICATION PASSED")
                return True
            else:
                print("VERIFICATION FAILED: Unexpected data")
                return False
        else:
            print("VERIFICATION FAILED: Non-200 response")
            return False
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        print("Stopping server...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

if __name__ == "__main__":
    success = run_verification()
    if not success:
        sys.exit(1)
