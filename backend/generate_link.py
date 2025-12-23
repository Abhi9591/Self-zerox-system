
import requests

try:
    res = requests.post('http://localhost:8000/api/v1/session/', json={'machine_id': 1})
    if res.ok:
        session_id = res.json()['session_id']
        url = f"http://localhost:8000/mobile/upload.html?session_id={session_id}"
        print("Link generated.")
        with open("mobile_link.txt", "w") as f:
            f.write(url)
    else:
        print(f"Error: {res.text}")
except Exception as e:
    print(f"Failed to connect: {e}")
