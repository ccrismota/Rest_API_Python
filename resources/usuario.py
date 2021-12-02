from flask_restful import Resource, reqparse
from models.usuario import UserModel

class User(Resource):
    
    def get(self, hotel_id):
        user = UserModel.find_user(hotel_id)
        if user:
            return user.json() #json para retornar um objeto
        return {'Mensage': 'User not found.'}, 404 # not found   
        

    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                {'message':'An error ocurred trying to delete User.'},500 #internal server error
            return {'Mensage': 'User Deleted.'}
        return {'Mensage': 'User not found.'}, 404

    