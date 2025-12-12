import urllib.request
import urllib.error
import time
import json
from errors import generate_error

WEBHOOK_URL = "http://localhost:5678/webhook/incident/log"

def send_error(error_payload):
    try:
        data = json.dumps(error_payload).encode('utf-8')
        req = urllib.request.Request(WEBHOOK_URL, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            print(f"Sent error {error_payload['request_id']}: {response.status} {response.reason}")
    except urllib.error.URLError as e:
        print(f"Failed to send error: {e}")

def main():
    print(f"Starting fake error simulator... Targeting {WEBHOOK_URL}")
    while True:
        try:
            error = generate_error()
            print(json.dumps(error))
            send_error(error)
        except Exception as e:
            # Fallback in case of generator error
            print(f"Error generating fake error: {e}")
        
        # Simulating 30 seconds interval
        time.sleep(30)

if __name__ == "__main__":
    main()
