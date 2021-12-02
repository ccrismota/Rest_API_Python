from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from werkzeug.security import safe_str_cmp
from blacklist import BLACKLIST

atributos = reqparse.RequestParser()
atributos.add_argument('login', type=str, required=True, help="The field 'login' can't be left blank.")
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' can't be left blank.")
        


class User(Resource):
    
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json() #json para retornar um objeto
        return {'mensage': 'User not found.'}, 404 # not found   
        
    @jwt_required()
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                {'message':'An error ocurred trying to delete User.'},500 #internal server error
            return {'Mensage': 'User Deleted.'}
        return {'Mensage': 'User not found.'}, 404

class UserRegister(Resource):
#/cadastro
    def post(self):
        dados = atributos.parse_args()

        if UserModel.find_by_login(dados['login']):
            return {"message":"The login '{}' already exists.".format(dados['login'])}
        user = UserModel(**dados) # ou (dados['login'], dados['senha'])
        user.save_user()
        return {'message':'User created Successfully'},201 #created

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and safe_str_cmp(user.senha, dados['senha']):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {'access_token': token_de_acesso},200
        return {'message': 'The Username or password is Incorrect.'}, 401 # Unauthorized

class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt() ['jti'] # JWT Token identifier
        BLACKLIST.add(jwt_id)
        return {'message': 'Logged out successfully'}, 200