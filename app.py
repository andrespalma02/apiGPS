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


@app.route('/registro_produccion/', methods=['POST'])
def produccion_post():
    pavos = {}
    json_data = rq.json
    for items in json_data["produccion"]:
        pavos[items["Producto"]] = int(items["Cantidad"]) if "Cantidad" in items else ""
    print(pavos)

    pavos["Identificador"] = json_data["Identificador"] if "Identificador" in json_data else "XXXX1900/01/01"
    pavos["Fecha de registro"] = json_data["Fecha"] if "Fecha" in json_data else "1900/01/01"
    pavos["Retirado"] = 0
    r = requests.put(url + "Inventario_Produccion", json=pavos, headers=headers)
    pavos = {}
    for items in json_data["desperdicio"]:
        if "Cantidad" in items:
            if int(items["Cantidad"]) != 0:
                pavos[items["Producto"]] = int(items["Cantidad"])

    pavos["Identificador"] = json_data["Identificador"] if "Identificador" in json_data else "XXXX1900/01/01"
    pavos["Fecha de registro"] = json_data["Fecha"] if "Fecha" in json_data else "1900/01/01"
    pavos["Retirado"] = 0

    r = requests.put(url + "Inventario_Desperdicios", json=pavos, headers=headers)
    return r.json()


@app.route('/eviscerado/', methods=['POST'])
def eviscerado_get():
    pavos = {"tabla": []}
    json_data = rq.json
    pavos_recepcion = requests.get(
        url + "inventario_de_recepcion?paramName=Identificador" + "&paramValue=" + str(json_data["Id"])).json()
    lista_pavos = requests.get(
        url + "list?dbase=item_produccion&paramName=tipo_item" + "&paramValue=materia+prima").json()
    for datos_pavo in lista_pavos:
        pavo = datos_pavo["nombre"]
        if pavo in pavos_recepcion and pavos_recepcion[pavo] != "0":
            pavos["tabla"].append({"Cantidad": pavos_recepcion[pavo], "Producto": pavo})
    return pavos


@app.route('/condimentado_envasado/', methods=['POST'])
def condimentado_envasado_get():
    json_data = rq.json
    for item in json_data["tabla"]:
        if item["Desperdicio"] == "":
            item["Desperdicio"] = "0"
        else:
            item["Cantidad"] = str(int(item["Cantidad"]) - int(item["Desperdicio"]))
            item["Desperdicio"] = "0"
    print(json_data)

    return json_data


@app.route('/calculo_final/', methods=['POST'])
def calculo_final():
    salida = {}
    desperdicio = {"tabla_desperdicios": []}
    json_data = rq.json
    lista_pavos = requests.get(
        url + "list?dbase=item_produccion&paramName=tipo_item" + "&paramValue=materia+prima").json()

    for item in json_data["tabla_final"]:
        if item["Desperdicio"] == "":
            item["Desperdicio"] = "0"
        else:
            item["Cantidad"] = str(int(item["Cantidad"]) - int(item["Desperdicio"]))
            item["Desperdicio"] = "0"
    pavos_inicio = json_data["tabla_inicio"]

    for i in range(len(pavos_inicio)):
        datos_inicio = pavos_inicio[i]
        datos_final = json_data["tabla_final"][i]
        desperdicio["tabla_desperdicios"].append(
            {"Cantidad": int(datos_inicio["Cantidad"]) - int(datos_final["Cantidad"]),
             "Producto": datos_inicio["Producto"]})
    total_produccion = 0.0
    total_desperdicios = 0.0
    for datos in desperdicio["tabla_desperdicios"]:
        for item in lista_pavos:
            precio = item["precio"]
            nombre = item["nombre"]
            if nombre in datos["Producto"]:
                total_desperdicios = total_desperdicios + (int(datos["Cantidad"]) * float(precio))
    for datos in json_data["tabla_final"]:
        for item in lista_pavos:
            precio = item["precio"]
            nombre = item["nombre"]
            if nombre in datos["Producto"]:
                total_produccion = total_produccion + (int(datos["Cantidad"]) * float(precio))

    salida["desperdicio"] = desperdicio["tabla_desperdicios"]
    salida["produccion"] = json_data["tabla_final"]
    salida["total_produccion"] = total_produccion
    salida["total_desperdicio"] = total_desperdicios
    salida["total"] = total_produccion + total_desperdicios

    return salida


@app.route('/insumos/', methods=['POST'])
def receta_post():
    tabla_pavos = rq.json["tabla"]
    id_tipo = rq.json["id"]
    sal = especias = salsa = acido = pimienta = conservante = total = 0
    recetas = requests.get(
        url + "list?dbase=Recetas&paramName=Tipo+de+receta" + "&paramValue=" + str(id_tipo)).json()
    for receta in recetas:
        for pavo in tabla_pavos:
            if pavo["Producto"] == receta["Tamaño receta"]:
                cantidad = int(pavo["Cantidad"])
                sal = sal + (float(receta["Sal"]) * cantidad)
                acido = acido + (float(receta["Acido cítrico"]) * cantidad)
                conservante = conservante + (float(receta["Conservante"]) * cantidad)
                pimienta = pimienta + (float(receta["Pimienta"]) * cantidad)
                salsa = salsa + (float(receta["Salsa de soya"]) * cantidad)
                especias = especias + (float(receta["Especias aromáticas"]) * cantidad)
    datos = {"Sal": sal, "Especias aromáticas": especias, "Salsa de soya": salsa, "Acido Cítrico": acido,
             "Pimienta": pimienta,
             "Conservante+para+pavo": conservante}
    salida = {"tabla": []}
    for especia, valor in datos.items():
        aux = valor * float(
            requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + especia).json()["precio"])
        total += aux
        if especia == "Conservante+para+pavo":
            salida["tabla"].append({"Condimento": "Conservante para pavo", "Cantidad": valor})
        else:
            salida["tabla"].append({"Condimento": especia, "Cantidad": valor})
    salida["total"] = total

    return salida



@app.route('/materiales/', methods=['POST'])
def materiales_post():
    tabla_pavos = rq.json["tabla"]
    id_tipo = rq.json["id"]
    sal = especias = salsa = acido = pimienta = conservante = total = 0
    recetas = requests.get(
        url + "list?dbase=Recetas&paramName=Tipo+de+receta" + "&paramValue=" + str(id_tipo)).json()
    for receta in recetas:
        for pavo in tabla_pavos:
            if pavo["Producto"] == receta["Tamaño receta"]:
                cantidad = int(pavo["Cantidad"])
                sal = sal + (float(receta["Sal"]) * cantidad)
                acido = acido + (float(receta["Acido cítrico"]) * cantidad)
                conservante = conservante + (float(receta["Conservante"]) * cantidad)
                pimienta = pimienta + (float(receta["Pimienta"]) * cantidad)
                salsa = salsa + (float(receta["Salsa de soya"]) * cantidad)
                especias = especias + (float(receta["Especias aromáticas"]) * cantidad)
    datos = {"Sal": sal, "Especias aromáticas": especias, "Salsa de soya": salsa, "Acido Cítrico": acido,
             "Pimienta": pimienta,
             "Conservante+para+pavo": conservante}
    salida = {"tabla": []}
    for especia, valor in datos.items():
        aux = valor * float(
            requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + especia).json()["precio"])
        total += aux
        if especia == "Conservante+para+pavo":
            salida["tabla"].append({"Condimento": "Conservante para pavo", "Cantidad": valor})
        else:
            salida["tabla"].append({"Condimento": especia, "Cantidad": valor})
    salida["total"] = total

    return salida

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
                    "Producto": "Pavita"
                },
                {
                    "Cantidad": "5",
                    "Producto": "Pavo Mediano"
                },
                {
                    "Cantidad": "0",
                    "Producto": "Pavo grandes"
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
