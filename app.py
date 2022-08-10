from flask import Flask, request
import requests

app = Flask(__name__)
apiKey = "3809ccdc104d405f5387031f81abcf9cadba6f1767fcdff3"
headers = {"Content-Type": "application/json",
           "X-Api-Key": apiKey,
           "X-Username": "bryan.palma02@epn.edu.ec"}


@app.route('/inventario_insumos', methods=['POST'])
def hello_world():
    json_data = request.form
    tabla=json_data["tabla"]
    for item in tabla:
        requests.put(f"https://app.flokzu.com/flokzuopenapi/api/{apiKey}/database"
                     "/PRO_Inventario_Insumos_Materiales", json_data, "", headers)
    return 0


if __name__ == '__main__':
    app.run()
