from sqlite3.dbapi2 import Cursor
from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3 as sql

def normalize_path_params(cidade = None, 
                          estrelas_min = 0, 
                          estrelas_max = 0, 
                          diaria_min = 0, 
                          diaria_max = 10000, 
                          limit = 50, 
                          offset = 0, **dados):
    if cidade:
        return {
            'estrelas_min': estrelas_min,
            'estrelas_max': estrelas_max,
            'diaria_min': diaria_min,
            'diaria_max': diaria_max,
            'cidade': cidade,
            'limit': limit,
            'offset': offset }
    return {
        'estrelas_min': estrelas_min,
        'estrelas_max': estrelas_max,
        'diaria_min': diaria_min,
        'diaria_max': diaria_max,
        'limit': limit,
        'offset': offset 
    }    
    


#path /hoteis?cidade=rio de janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str)
path_params.add_argument('estrelas_min',type=float)
path_params.add_argument('estrelas_max',type=float)
path_params.add_argument('diaria_min',type=float)
path_params.add_argument('diaria_max',type=float)
path_params.add_argument('limit',type=float)
path_params.add_argument('offset',type=float)

class Hoteis(Resource):
    def get(self):
        connection = sql.connect('banco.db')
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave: dados[chave] for chave in dados if dados[chave] is not None}
        paramentros = normalize_path_params(**dados_validos)

        if not paramentros.get('cidade'):
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas >= ? and estrelas <= ?) \
            and (diaria >= ? and diaria <= ?) \
            LIMIT ? OFFSET ?"
            tupla = tuple([paramentros[chave] for chave in paramentros])
            resultado = cursor.execute(consulta, tupla)
        else:
            consulta = "SELECT * FROM hoteis \
            WHERE (estrelas >= ? and estrelas <= ?) \
            and (diaria >= ? and diaria <= ?) \
            and cidade = ? LIMIT ? OFFSET ?"
            tupla = tuple([paramentros[chave] for chave in paramentros])
            resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for linha in resultado:
            hoteis.append({
                'hotel_id': linha[0],
                'nome': linha[1],
                'estrelas': linha[2],
                'diaria': linha[3],
                'cidade': linha[4]
            })

        return {'hoteis': hoteis} #{'hoteis': [hotel.json() for hotel in HotelModel.query.all()]} #SELECT * FROM hoteis

class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="the field 'nome' can't be left blank")
    atributos.add_argument('estrelas', type=float,  required=True, help="the field 'estrelas' can't be left blank")
    atributos.add_argument('diaria')
    atributos.add_argument('cidade')
  
    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json() #json para retornar um objeto
        return {'Mensage': 'hotel not found.'}, 404 # not found   
        
    @jwt_required()
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400

        dados = Hotel.atributos.parse_args() #neste caso acesso a classe para n??o precisar usar copiar os argumentos
        hotel = HotelModel(hotel_id, **dados) #Essa sintaxe "**dados" permite que todos oss dados sejam desempacotados
        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal erro ocurred trying to save hotel.'},500 #internal server error
        return hotel.json()

    # O PUT altera se o hotel_id existe, caso contrario, ele cria.
    @jwt_required()
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()        
        hotel_encontrado = HotelModel.find_hotel(hotel_id)
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200 #ok
        hotel = HotelModel(hotel_id, **dados) 
        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal erro ocurred trying to save hotel.'},500 #internal server error
        return hotel.json(), 201 #created

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                {'message':'An error ocurred trying to delete hotel.'},500 #internal server error
            return {'Mensage': 'Hotel Deleted.'}
        return {'Mensage': 'Hotel not found.'}, 404

   