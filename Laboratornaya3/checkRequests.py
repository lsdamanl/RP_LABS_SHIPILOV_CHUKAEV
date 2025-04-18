import requests
import random

base_url = 'http://127.0.0.1:5000/number'

# 1. GET
param1 = random.randint(1, 10)
response1 = requests.get(base_url, params={'param': param1}).json()
print("GET response:", response1)

# 2. POST
param2 = random.randint(1, 10)
headers = {'Content-Type': 'application/json'}
response2 = requests.post(base_url, json={'jsonParam': param2}, headers=headers).json()
print("POST response:", response2)

# 3. DELETE
response3 = requests.delete(base_url).json()
print("DELETE response:", response3)

# 4. Вычисление выражения
expr = (f"{response1['random_number']} {response1['operation']} {response2['random_number']} {response2['operation']} "
        f"{response3['random_number']}")
print("Expression:", expr)
result = int(eval(expr))
print("Result:", result)
