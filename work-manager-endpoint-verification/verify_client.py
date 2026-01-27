import requests

url = "https://work-manager-endpoint-verification.onrender.com/verify"

payload = {
    "device_id": "TEST-DEVICE-001",
    "fingerprint": "abc123"
}

r = requests.post(url, json=payload, timeout=15)
print(r.status_code, r.json())
