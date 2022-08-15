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
    pavos["Pavitas"] = pavos.get("Pavitas", 0)
    pavos["Pavos medianos"] = pavos.get("Pavos medianos", 0)
    pavos["Pavos grandes"] = pavos.get("Pavos grandes", 0)
    pavos["Pavos extra grandes"] = pavos.get("Pavos extra grandes", 0)
    pavos["Pavos super extra grandes"] = pavos.get("Pavos super extra grandes", 0)
    pavos["Identificador"] = json_data["Identificador"] if "Identificador" in json_data else "XXXX1900/01/01"
    pavos["Fecha de Recepción"] = json_data["Fecha"] if "Fecha" in json_data else "1900/01/01"
    pavos["Número de Lote"] = json_data["Número de lote"] if "Número de lote" in json_data else "N/D"
    pavos["Peso de Lote"] = json_data["Peso del lote"] if "Peso del lote" in json_data else 0
    pavos["Responsable"] = json_data[
        "Responsable del Control de Calidad"] if "Responsable del Control de Calidad" in json_data else "N/D"
    pavos["Procesado"] = 0

    r = requests.put(url + "inventario_de_recepcion", json=pavos, headers=headers)
    print(url + "inventario_de_recepcion")
    return r.text.__str__()


@app.route('/inventario_insumos', methods=['PUT'])
def get_resource():
    json_data = rq.json
    for item in json_data["tabla"]:
        r = requests.get(url + "Inventario_Insumos_Materiales?paramName=C%C3%B3digo" + "&paramValue=" + item["Código"])
        cantidad = int(r.json()["Cantidad"])
        cantidad += int(item["Cantidad"])
        id_item = r.json()["Id"]
        update = {"Id": id_item, "Cantidad": cantidad}
        r = requests.put(url + "Inventario_Insumos_Materiales/update?withInsert=false", json=update, headers=headers)
    return "true"


if __name__ == '__main__':
    app.run()
