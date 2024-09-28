import requests

url = "http://127.0.0.1:8001/jobs/"
data = {
    "title": "Software Engineer",
    "location": "New York"
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())
