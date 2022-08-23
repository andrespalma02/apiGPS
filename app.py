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
    json_data = rq.json
    id_lote = json_data["Id"]
    lista_pavos = requests.get(
        url + "list?dbase=PRO_DETALLE_RECEPCION&paramName=Lote" + f"&paramValue={id_lote}").json()
    return {"tabla": lista_pavos}


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
    salida["total_produccion"] = total_produccion * 1.12
    salida["total_desperdicio"] = total_desperdicios * 1.12
    salida["total"] = (total_produccion + total_desperdicios) * 1.12

    return salida


@app.route('/guardar_receta/', methods=['POST'])
def guardar_receta():
    tabla = rq.json["tabla"]
    for item in tabla:
        requests.put(url + "RECETA", json=item, headers=headers)
    return "True"


@app.route('/condimentos/', methods=['POST'])
def condimentos_post():
    tabla_pavos = rq.json["tabla"]
    id_tipo = rq.json["id"]
    ingredientes = {}
    salida = {"tabla": []}
    recetas = requests.get(
        url + "list?dbase=RECETA&paramName=Tipo+de+Receta" + "&paramValue=" + str(id_tipo)).json()
    for pavo in tabla_pavos:
        for item in recetas:
            if item["Tamaño"] == pavo["Producto"]:
                cantidad = int(pavo["Cantidad"])
                if item["Ingrediente"] in ingredientes:
                    ingredientes[item["Ingrediente"]] = ingredientes[item["Ingrediente"]] + (
                            float(item["Cantidad"]) * cantidad)
                else:
                    ingredientes[item["Ingrediente"]] = (float(item["Cantidad"]) * cantidad)
    precios = requests.get(
        url + "list?dbase=item_produccion&paramName=tipo_item" + "&paramValue=insumo").json()
    total_insumos = 0

    for precio in precios:
        nombre_condimento = precio["nombre"]
        if nombre_condimento in ingredientes:
            total_insumos = total_insumos + (ingredientes[nombre_condimento] * float(precio["precio"]))
            salida["tabla"].append({"Condimento": nombre_condimento, "Cantidad": ingredientes[nombre_condimento]})
    salida["total"] = total_insumos * 1.12
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
    salida = {"tabla": []}
    total_pavos = 0
    for pavo in tabla_pavos:
        total_pavos += int(pavo["Cantidad"])
    print(total_pavos)
    precios = requests.get(
        url + "list?dbase=item_produccion&paramName=tipo_item" + "&paramValue=material").json()
    total_materiales = 0

    for precio in precios:
        nombre_material = precio["nombre"]
        salida["tabla"].append({"Material": nombre_material, "Cantidad": total_pavos})
        total_materiales = total_materiales + (total_pavos * float(precio["precio"]))
    salida["total"] = total_materiales * 1.12

    return salida


@app.route('/actualizar_materiales/', methods=['POST'])
def materiales_restar():
    json_data = rq.json
    for item in json_data["tabla"]:
        r = requests.get(url + "Inventario_Insumos_Materiales?paramName=Producto" + "&paramValue=" + item["Material"])
        if "Cantidad" not in r.json():
            cantidad = item["Cantidad"]
            codigo = item["Código"]
            tipo = item["Tipo"] if "Tipo" in item else "insumo"
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
    process_url = f"https://app.flokzu.com/flokzuopenapi/api/{apiKey}/instance?processCode=FINCOSPROD"
    data = {
        "Valor Materia Prima": total * 1.12,
        "Valor Mat. Prima Productos por Recibir": total * 1.12
    }
    print(process_url)
    r = requests.post(process_url, json=data, headers=headers)
    print(r)
    return "R"


@app.route('/total_produccion/', methods=['POST'])
def total_prod():
    json_data = rq.json
    total = 0
    process_url = f"https://app.flokzu.com/flokzuopenapi/api/{apiKey}/instance?processCode=FINCOSPROD"
    data = {
        "Valor Total Producción en Proceso": json_data["total_prod"],
        "Valor Total Materia Prima": json_data["materia_prima"],
        "Valor Total Producción Proceso": json_data["produccion_proceso"],
        "Valor Total Desperdicios": json_data["desperdicios"],
        "Valor Total Producto Terminado": json_data["prod_terminado"],
    }
    print(process_url)
    r = requests.post(process_url, json=data, headers=headers)
    print(r)
    return "R"


@app.route('/total_insumos_recibidos/', methods=['POST'])
def total_ir():
    json_data = rq.json
    total_insumos = 0
    total_mat = 0
    for item in json_data["tabla"]:
        if item["Tipo"] == "insumo":
            total_insumos += float(item["Precio"])
        else:
            total_mat += float(item["Precio"])
    process_url = f"https://app.flokzu.com/flokzuopenapi/api/{apiKey}/instance?processCode=FINCOSPROD"
    data = {
        "Valor Materiales ": total_mat * 1.12,
        "Valor Insumos": total_insumos * 1.12,
        "Valor Materiales por Recibir": total_mat * 1.12,
        "Valor Insumos por Recibir": total_insumos * 1.12

    }
    r = requests.post(process_url, json=data, headers=headers)
    return r


@app.route('/inventario_insumos', methods=['PUT'])
def get_resource():
    json_data = rq.json
    for item in json_data["tabla"]:
        r = requests.get(url + "Inventario_Insumos_Materiales?paramName=C%C3%B3digo" + "&paramValue=" + item["Código"])
        if "Cantidad" not in r.json():
            cantidad = item["Cantidad"]
            codigo = item["Código"]
            tipo = item["Tipo"] if "Tipo" in item else "insumo"
            producto = item["Producto"] if "Producto" in item else "NaN"
            id_item = item["Id"] if "Id" in item else 0
            update = {"Id": id_item, "Código": codigo, "Tipo": tipo, "Producto": producto, "Cantidad": cantidad}
        else:
            cantidad = float(r.json()["Cantidad"])
            cantidad += float(item["Cantidad"])
            id_item = r.json()["Id"]
            update = {"Id": id_item, "Cantidad": cantidad}
        r = requests.put(url + "Inventario_Insumos_Materiales/update?withInsert=true", json=update, headers=headers)
    return r.json()


if __name__ == '__main__':
    app.run()
