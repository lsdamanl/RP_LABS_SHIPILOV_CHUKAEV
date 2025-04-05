import requests
url = 'http://127.0.0.1:5000/number/'
data = {'jsonParam': 5}

response = requests.post(url, json=data)
print(response.json())

response_delete = requests.delete(url)
print("DELETE Response:", response_delete.json())