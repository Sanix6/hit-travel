import requests

url = "https://onesignal.com/api/v1/players"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "os_v2_app_zxjk5s4cardeba4wg2r4knqbpgts3nfbm4ruabupbgraluhlhg2fwfoxhuhyd3emhm2mwixxny2d6vexkjcpwpsp63zdeu5atvmrkli",
}

payload = {
    "app_id": "cdd2aecb-8204-4640-8396-36a3c5360179",
    "device_type": 1,      
    "identifier": "kylychbekow@gmail.com",
}

response = requests.post(url, headers=headers, json=payload)
print(response.json())
