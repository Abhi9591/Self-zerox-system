
import requests
import uuid

# debug_upload.py
BASE_URL = "http://localhost:8000"

def test_upload():
    # 1. Create Session
    print("1. Creating Session...")
    try:
        res = requests.post(f"{BASE_URL}/api/v1/session/", json={"machine_id": 1})
        if not res.ok:
            print(f"Create Session Failed: {res.text}")
            return
        session_data = res.json()
        session_id = session_data['session_id']
        print(f"Session Created: {session_id}")
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    filename = "test.pdf"
    object_name = f"{session_id}/{filename}"
    
    # 2. Upload Flow
    upload_url = f"{BASE_URL}/api/v1/storage/upload/{object_name}"
    print(f"2. Testing Upload URL: {upload_url}")
    
    try:
        data = b"%PDF-1.4 test content"
        res = requests.put(upload_url, data=data)
        
        if res.ok:
            print("Upload SUCCESS")
            
            # 3. Finalize
            print("3. Finalizing...")
            finalize_url = f"{BASE_URL}/api/v1/session/{session_id}/uploaded"
            fin_res = requests.post(finalize_url, params={"key": object_name})
            
            print(f"Finalize Status: {fin_res.status_code}", flush=True)
            print(f"Finalize Body: {fin_res.text}", flush=True)
            
        else:
            print(f"Upload FAILED: {res.text}", flush=True)
    except Exception as e:
        print(f"Exception: {e}", flush=True)

if __name__ == "__main__":
    test_upload()
