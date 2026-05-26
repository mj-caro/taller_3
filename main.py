from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

#os.environ para despliegue. Descomente cuando ya probó todo local.
client = MongoClient(os.environ["MONGO_URI"])

# client = MongoClient("mongodb://<usuario>:<contraseña>@157.253.236.88:8087")

db = client["ISIS2304A14202610"]


@app.get("/")
def inicio():
    return {"estado": "API funcionando correctamente"}

@app.get('/bares/{bar_id}/comentarios')
def get_comentarios(bar_id: int):
    comentarios = list(db["comentarios"].find({"bar_id": bar_id}, {"_id": 0}))  
    return comentarios

@app.post('/bares/{bar_id}/comentarios')
def post_comentario(bar_id: int, datos: dict):
    datos['bar_id'] = bar_id
    datos['fecha']  = datetime.now().isoformat()

    db["comentarios"].insert_one(datos)
    
    return {'mensaje': 'Comentario guardado'}


@app.get('/bares/{bar_id}/eventos')
def get_eventos(bar_id: int):
    eventos = list(db["eventos"].find({"bar_id": bar_id}, {"_id": 0}))  
    return eventos




@app.post('/bares/{bar_id}/eventos')
def post_eventos(bar_id: int, datos: dict):
    datos['bar_id'] = bar_id
    datos['fecha_creacion'] = datetime.now().isoformat()
    db["eventos"].insert_one(datos)
    datos.pop('_id', None)  # quita el _id que mongo agrega
    return {'mensaje': 'Evento guardado'}


@app.get("/rfc1/top-hoteles")
def rfc1_top_hoteles():
    pipeline = [
        {"$group": {
            "_id": "$hotel_id",
            "calificacionPromedio": {"$avg": "$calificacion"},
            "totalReseñas": {"$sum": 1}
        }},
        {"$sort": {"calificacionPromedio": -1}},
        {"$limit": 10},
        {"$lookup": {
            "from": "hoteles",
            "localField": "_id",
            "foreignField": "_id",
            "as": "hotel"
        }},
        {"$project": {
            "nombreHotel": {"$arrayElemAt": ["$hotel.nombre", 0]},
            "ciudad": {"$arrayElemAt": ["$hotel.ciudad", 0]},
            "calificacionPromedio": 1,
            "totalReseñas": 1
        }}
    ]
    resultado = list(db["reseñas"].aggregate(pipeline))
    return resultado