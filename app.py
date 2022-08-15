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
def recepcion_post():
    pavos = {}
    json_data = rq.json
    for items in json_data["tabla"]:
        pavos[items["Producto"]] = int(items["Cantidad"])
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
    print(r.json())
    return r.json()


@app.route('/inventario_recepcion/', methods=['GET'])
def recepcion_get():
    pavos = {"tabla": []}
    json_data = rq.json
    r = requests.get(url + "inventario_de_recepcion?paramName=Identificador" + "&paramValue=" + json_data["Id"]).json()
    pavos["tabla"].append({"Cantidad": r["Pavitas"], "Producto": "Pavitas"}) if "Pavitas" in r else ""
    pavos["tabla"].append(
        {"Cantidad": r["Pavos medianos"], "Producto": "Pavos medianos"}) if "Pavos medianos" in r else ""
    pavos["tabla"].append({"Cantidad": r["Pavos grandes"], "Producto": "Pavos grandes"}) if "Pavos grandes" in r else ""
    pavos["tabla"].append(
        {"Cantidad": r["Pavos extra grandes"], "Producto": "Pavos extra grandes"}) if "Pavos extra grandes" in r else ""
    pavos["tabla"].append({"Cantidad": r["Pavos super extra grandes"],
                           "Producto": "Pavos super extra grandes"}) if "Pavos super extra grandes" in r else ""
    return pavos


@app.route('/insumos/', methods=['POST'])
def receta_post():
    json_data = rq.json
    r = requests.get(url + "list?dbase=Recetas&paramName=Id" + "&paramValue=" + str(json_data["id"])).json()
    sal = 0
    especias = 0
    salsa = 0
    acido = 0
    pimienta = 0
    conservante = 0
    for item in json_data["tabla"]:
        for receta in r:
            if item["Producto"] == receta["Tamaño receta"]:
                cantidad= float(item["Cantidad Eviscerada"])
                sal += float(receta["Sal"]) * cantidad
                especias += float(receta["Especias aromáticas"]) * cantidad
                salsa += float(receta["Salsa de soya"]) * cantidad
                acido += float(receta["Acido cítrico"]) * cantidad
                pimienta += float(receta["Pimienta"]) * cantidad
                conservante += float(receta["Conservante"]) * cantidad

    total = 0
    aux = sal * float(
        requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + "Sal").json()["precio"])
    total += aux
    aux = especias * float(
        requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + "Especias aromáticas").json()[
            "precio"])
    total += aux
    aux = salsa * float(
        requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + "Salsa de soya").json()["precio"])
    total += aux
    aux = acido * float(
        requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + "Acido Cítrico").json()["precio"])
    total += aux
    aux = pimienta * float(
        requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + "Pimienta").json()["precio"])
    total += aux
    aux = conservante * float(
        requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + "Conservante+para+pavo").json()["precio"])
    total += aux

    datos = {"sal": sal, "especias": especias, "salsa": salsa, "acido": acido, "pimienta": pimienta,
             "conservante": conservante, "total": total}

    return datos


@app.route('/inventario_insumos', methods=['PUT'])
def get_resource():
    json_data = rq.json
    for item in json_data["tabla"]:
        r = requests.get(url + "Inventario_Insumos_Materiales?paramName=C%C3%B3digo" + "&paramValue=" + item["Código"])
        if "Cantidad" not in r.json():
            cantidad = item["Cantidad"]
            codigo = item["Código"]
            tipo = item["Tipo"] if "Tipo" in item else "Insumo"
            producto = item["Producto"] if "Producto" in item else "NaN"
            id_item = item["Id"] if "Id" in item else 0
            update = {"Id": id_item, "Código": codigo, "Tipo": tipo, "Producto": producto, "Cantidad": cantidad}
        else:
            cantidad = int(r.json()["Cantidad"])
            cantidad += int(item["Cantidad"])
            id_item = r.json()["Id"]
            update = {"Id": id_item, "Cantidad": cantidad}
        r = requests.put(url + "Inventario_Insumos_Materiales/update?withInsert=true", json=update, headers=headers)
    return r.json()


@app.route('/sample', methods=['GET'])
def get_sample():
    json_data = rq.args
    if json_data.get("ID") == "1":
        tabla = {
            "tabla": [
                {
                    "Cantidad": "20",
                    "Producto": "Pavitas"
                },
                {
                    "Cantidad": "5",
                    "Producto": "Pavos medianos"
                },
                {
                    "Cantidad": "0",
                    "Producto": "Pavos grandes"
                },
                {
                    "Cantidad": "0",
                    "Producto": "Pavos extra grandes"
                },
                {
                    "Cantidad": "0",
                    "Producto": "Pavos super extra grandes"
                }
            ]
        }
    else:
        tabla = {"tabla": [{"Cantidad": "0", "Producto": "Nada"}]}
    return tabla


if __name__ == '__main__':
    app.run()
