from urllib.request import Request

import requests
from flask import Flask, request as rq

app = Flask(__name__)
apiKey = "3809ccdc104d405f5387031f81abcf9cadba6f1767fcdff3"
headers = {"Content-Type": "application/json",
           "X-Api-Key": apiKey,
           "X-Username": "bryan.palma02@epn.edu.ec"}
url = f"https://app.flokzu.com/flokzuopenapi/api/{apiKey}/database/Inventario_Desperdicios"

values = """
{
    "Pavitas": "1",
    "Pavos medianos": "3",
    "Pavos grandes": "4",
}"""


@app.route('/inventario_insumos/', methods=['PUT'])
def hello():
    request = Request(f'https://app.flokzu.com/flokzuopenapi/api/{apiKey}/database/Inventario_Desperdicios',
                      data=values,
                      headers=headers)
    request.get_method = lambda: 'PUT'
    print(request.data)


@app.route('/')
def hello():
    return "Hola mundo"


@app.route('/inventario_insumos/', methods=['POST'])
def hello_world():
    status = []
    json_data = rq.json
    for items in json_data["tabla"]:
        r = requests.put(url, data=values, headers=headers)
        status.append(r)
    return status.__str__()


@app.route('/inventario_insumos', methods=['GET'])
def get_resource():
    status = []
    param = rq.args.get("paramName")
    value = rq.args.get("paramValue")
    r = requests.get(url + "?paramName=" + param + "&paramValue=" + value, headers=headers)
    return r.json()


if __name__ == '__main__':
    app.run()
