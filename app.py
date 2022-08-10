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
    json_data = rq.json
    for items in json_data["tabla"]:
        r = requests.put(url + "Inventario_Desperdicios", data=items, headers=headers)
        print(r.status_code)
    return "listo"


if __name__ == '__main__':
    app.run()
