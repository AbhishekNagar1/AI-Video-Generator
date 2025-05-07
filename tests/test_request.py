import requests

url = "http://127.0.0.1:8000/generate_video/"
data = {"topic": "Math", "duration": 60, "level": "medium"}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=data, headers=headers)
print(response.json())
