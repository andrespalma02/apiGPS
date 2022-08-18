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


@app.route('/inventario_recepcion/', methods=['POST'])
def recepcion_post():
    recepcion = {}
    json_data = rq.json
    recepcion["Fecha"] = json_data["Fecha"] if "Fecha" in json_data else "1900/01/01"
    recepcion["Lote"] = json_data["Identificador"] if "Identificador" in json_data else "N/D"
    recepcion["Número de Lote"] = json_data["Número de lote"] if "Número de lote" in json_data else "N/D"
    recepcion["Peso de Lote"] = json_data["Peso del lote"] if "Peso del lote" in json_data else 0
    recepcion["Responsable"] = json_data[
        "Responsable del Control de Calidad"] if "Responsable del Control de Calidad" in json_data else "N/D"
    recepcion["Procesado"] = 0
    requests.put(url + "PRO_RECEPCION_GENERAL", json=recepcion, headers=headers)

    pavos = {}

    for items in json_data["tabla"]:
        print(int(items["Cantidad"]), ", ", items["Producto"])
        pavos["Cantidad"] = int(items["Cantidad"])
        pavos["Producto"] = items["Producto"]
        pavos["Lote"] = recepcion["Lote"]
        requests.put(url + "PRO_DETALLE_RECEPCION", json=pavos, headers=headers)
    return "True"



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
    id_lote=json_data["Id"]
    lista_pavos = requests.get(
        url + "list?dbase=PRO_DETALLE_RECEPCION&paramName=Lote" + f"&paramValue={id_lote}").json()
    return lista_pavos


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


@app.route('/actualizar_insumos/', methods=['POST'])
def insumos_restar():
    json_data = rq.json
    for item in json_data["tabla"]:
        r = requests.get(url + "Inventario_Insumos_Materiales?paramName=Producto" + "&paramValue=" + item["Condimento"])
        if "Cantidad" not in r.json():
            cantidad = item["Cantidad"]
            codigo = item["Código"]
            tipo = item["Tipo"] if "Tipo" in item else "Insumo"
            producto = item["Producto"] if "Producto" in item else "NaN"
            id_item = item["Id"] if "Id" in item else 0
            update = {"Id": id_item, "Código": codigo, "Tipo": tipo, "Producto": producto, "Cantidad": cantidad}
        else:
            cantidad = float(r.json()["Cantidad"])
            cantidad -= float(item["Cantidad"])
            id_item = r.json()["Id"]
            update = {"Id": id_item, "Cantidad": cantidad}
        r = requests.put(url + "Inventario_Insumos_Materiales/update?withInsert=true", json=update, headers=headers)
    return r.json()


@app.route('/materiales/', methods=['POST'])
def materiales_post():
    tabla_pavos = rq.json["tabla"]
    funda_t = funda_m = malla = medidor = rollo = alambre = total = 0
    for pavo in tabla_pavos:
        cantidad = int(pavo["Cantidad"])
        funda_m = funda_m + cantidad
        funda_t = funda_t + cantidad
        malla = malla + cantidad
        medidor = medidor + cantidad
        rollo = rollo + cantidad
        alambre = alambre + cantidad
    datos = {"Funda termoencogible": funda_t, "Funda para menudencias": funda_m, "Malla para agarre": malla,
             "Medidor de cocción": medidor, "Rollo de etiquetas": rollo, "Alambre para empaque": alambre}
    salida = {"tabla": []}
    for material, valor in datos.items():
        precio = \
            requests.get(url + "item_produccion?paramName=nombre" + "&paramValue=" + material.replace(" ", "+")).json()[
                "precio"]
        aux = valor * float(precio)
        total += aux
        salida["tabla"].append({"Material": material, "Cantidad": valor})
    salida["total"] = total

    return salida


@app.route('/actualizar_materiales/', methods=['POST'])
def materiales_restar():
    json_data = rq.json
    for item in json_data["tabla"]:
        r = requests.get(url + "Inventario_Insumos_Materiales?paramName=Producto" + "&paramValue=" + item["Material"])
        if "Cantidad" not in r.json():
            cantidad = item["Cantidad"]
            codigo = item["Código"]
            tipo = item["Tipo"] if "Tipo" in item else "Insumo"
            producto = item["Producto"] if "Producto" in item else "NaN"
            id_item = item["Id"] if "Id" in item else 0
            update = {"Id": id_item, "Código": codigo, "Tipo": tipo, "Producto": producto, "Cantidad": cantidad}
        else:
            cantidad = int(r.json()["Cantidad"])
            cantidad -= int(item["Cantidad"])
            id_item = r.json()["Id"]
            update = {"Id": id_item, "Cantidad": cantidad}
        r = requests.put(url + "Inventario_Insumos_Materiales/update?withInsert=true", json=update, headers=headers)
    return r.json()


@app.route('/total_pavos_recibidos/', methods=['POST'])
def total_pr():
    json_data = rq.json
    total = 0
    for item in json_data["tabla"]:
        total += float(item["Total"])
    return {"total": total}


@app.route('/total_insumos_recibidos/', methods=['POST'])
def total_ir():
    json_data = rq.json
    total = 0
    for item in json_data["tabla"]:
        total += float(item["Total"])
    return {"total": total}


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


if __name__ == '__main__':
    app.run()
