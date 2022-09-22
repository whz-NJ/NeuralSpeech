# -*- coding: utf-8 -*-
import requests
import json

reqUrl = "http://127.0.0.1:5051/fast_correct"

# 请在此处填写请求方式，如：POST、GET、PUT
requestMethod = "POST"
# 请在此处填写需要的headers
headers = {'Content-Type': 'application/json; charset=UTF-8'}

payload = {
    "text": "好求，乌拉归进求啦！"
}

payload0 = json.dumps(payload, ensure_ascii=False)
print(payload0)
payload = payload0.encode(encoding="UTF-8")

response = requests.request(requestMethod, reqUrl, headers=headers, data=payload, verify=False)
res_json = response.json()
print(res_json)

