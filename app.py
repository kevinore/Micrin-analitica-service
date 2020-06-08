from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.json_util import dumps
import urllib.parse
from bson import json_util
from flask_cors import CORS
import numpy as np
from sklearn import linear_model
from sklearn.model_selection import train_test_split
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)
CORS(app)

username = urllib.parse.quote_plus('Micirn')
password = urllib.parse.quote_plus('@Micrin')
client = MongoClient("mongodb+srv://%s:%s@analitica-pqz6j.mongodb.net/test?retryWrites=true&w=majority"%(username,password))
db = client.Micrin_analitica

def connexToDB(plato):
    analitica = db.analitica.find({'nombre_plato':plato})
    uni = db.analitica.find({'nombre_plato':plato})

    cod_fechas = []
    for i in analitica:
        dic={'cod_fecha':i['cod_fecha']}
        cod_fechas.append(dic)

    adddate(cod_fechas, db, plato)

    unidades = []
    for x in uni:
        dic={'unidades':x['unidades']}
        unidades.append(dic)

    Xnum=[]
    for n in range(0,len(cod_fechas)):
        num = int(cod_fechas[n]['cod_fecha'])
        Xnum.append(num)

    Ynum=[]
    for n in range(0,len(unidades)):
        num = int(unidades[n]['unidades'])
        Ynum.append(num)
    
    X = np.reshape(Xnum,(-1,1))
    Y = np.reshape(Ynum,(-1,1))

    X_train,X_test,Y_train,Y_test=train_test_split(X,Y, test_size=0.10)
    lr=linear_model.LinearRegression()
    lr.fit(X_train,Y_train)

    Y_pred=lr.predict(X_test)

    a=lr.coef_[0][0]
    b = lr.intercept_[0]
    lr.score(X_train, Y_train)
    y = round(a*118+b)
    return {"plato":plato,"cantidad_plato":y, "precision":lr.score(X_train, Y_train)*100}

def adddate(listnumDB, db, plato):
    for i in range(1, 117):
        if not any(d['cod_fecha'] == str(i) for d in listnumDB):
            #print(plato)
            new_row={'nombre_plato':'xxxxxxx', 'unidades':'0', 'cod_fecha':str(i), 'fecha':'none'}
            #print(new_row)
            db.analitica.insert_one(new_row)

@app.route('/', methods=['GET'])
def index():
    return "Analitica microservices"

@app.route('/analitica', methods=['GET'])
def analitica():
    analitica = list(db.analitica.find({}))
    nombre_plato = []
    probabilidad = []
    for i in range(0, len(analitica)):
        if analitica[i]['nombre_plato'] not in nombre_plato:
            nombre_plato.append(analitica[i]['nombre_plato'])

    for i in range(0,10):
        probabilidad.append(connexToDB(nombre_plato[i]))

    return jsonify(probabilidad)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
