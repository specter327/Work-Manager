import requests

url = "https://work-manager-endpoint-verification.onrender.com/verify"

for device in ["TEST-DEVICE-001", "TEST-DEVICE-002", "UNKNOWN"]:
    r = requests.post(url, json={"device_id": device}, timeout=120)
    print(device, r.json())