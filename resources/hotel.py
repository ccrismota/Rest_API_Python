from flask_restful import Resource, reqparse
from models.hotel import HotelModel

hoteis = [
    {
        'hotel_id':'alpha',
        'nome': 'Alpha Hotel',
        'estrelas': 4.3,
        'diaria': 420.34,
        'cidade': 'Rio de Janeiro'
    },
    {
        'hotel_id':'bravo',
        'nome': 'Alpha Bravo',
        'estrelas': 4.3,
        'diaria': 480.34,
        'cidade': 'San francisco'
    },
    {
        'hotel_id':'mega',
        'nome': 'Alpha Mega',
        'estrelas': 4.3,
        'diaria': 320.30,
        'cidade': 'Santa catarina'
    },
]
 
class Hoteis(Resource):
    def get(self):
        return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]} #SELECT * FROM hoteis

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
        

    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400

        dados = Hotel.atributos.parse_args() #neste caso acesso a classe para não precisar usar copiar os argumentos
        hotel = HotelModel(hotel_id, **dados) #Essa sintaxe "**dados" permite que todos oss dados sejam desempacotados
        try:
            hotel.save_hotel()
        except:
            return {'message':'An internal erro ocurred trying to save hotel.'},500 #internal server error
        return hotel.json()

    # O PUT altera se o hotel_id existe, caso contrario, ele cria.
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


    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                {'message':'An error ocurred trying to delete hotel.'},500 #internal server error
            return {'Mensage': 'Hotel Deleted.'}
        return {'Mensage': 'Hotel not found.'}, 404

    #necessario definir uma variavel global, para que o python entenda que
    #estamos falando da mesma lista de hoteis