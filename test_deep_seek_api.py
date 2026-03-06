import requests

# Replace with your actual Deep Seek API key
API_KEY = "YOUR_DEEP_SEEK_API_KEY"

# Example endpoint for Deep Seek API (replace with the correct one if known)
url = "https://api.deepseek.com/v1/test_endpoint"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    print("API Key is valid. Response:")
    print(response.json())
else:
    print(f"Failed to validate API Key. Status Code: {response.status_code}")
    print("Response:", response.text)