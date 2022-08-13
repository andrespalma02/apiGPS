import requests
from flask import Flask, request as rq

app = Flask(__name__)
apiKey = "3809ccdc104d405f5387031f81abcf9cadba6f1767fcdff3"
headers = {"Content-Type": "application/json",
           "X-Api-Key": apiKey,
           "X-Username": "bryan.palma02@epn.edu.ec"}
url = f"https://app.flokzu.com/flokzuopenapi/api/{apiKey}/database/"


@app.route('/')
def hello():
    return "Hola mundo"


@app.route('/inventario_insumos/', methods=['POST'])
def hello_world():
    status = []
    json_data = rq.json
    for items in json_data["tabla"]:
        r = requests.put(url + "Inventario_Desperdicios", json=items, headers=headers)
        status.append(r.text)
    return status.__str__()


@app.route('/inventario_recepcion/', methods=['POST'])
def recepcion():
    pavos = {}
    json_data = rq.json
    for items in json_data["tabla"]:
        pavos[items["Nombre"]] = int(items["Cantidad"])
    pavos["Fecha de Recepción"] = json_data["Fecha de Recepción"]
    print(pavos)
    r = requests.put(url + "inventario_de_recepcion", json=pavos, headers=headers)
    print(url + "inventario_de_recepcion")
    return r.text.__str__()


@app.route('/inventario_insumos', methods=['GET'])
def get_resource():
    param = rq.args.get("paramName")
    value = rq.args.get("paramValue")
    r = requests.get(url + "?paramName=" + param + "&paramValue=" + value, headers=headers)
    return r.json()


if __name__ == '__main__':
    app.run()
