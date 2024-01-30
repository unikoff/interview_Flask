from flask import Flask, jsonify, request
from stun import get_ip_info
from flask_restx import Api, Resource, Namespace, fields

from flask_sqlalchemy import SQLAlchemy
from database import UserDB, WalletDB

from time import time

app = Flask("__name__")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main_db.db'
app.config['SECRET_KEY'] = 'random123124ijasnf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)
db_main = SQLAlchemy(app)
ns = Namespace('api')

user_model1 = api.model('User1', {
        'login': fields.String(),
        'password': fields.String(),
    })

user_model2 = api.model('User2', {
        'login': fields.String(),
        'password': fields.String(),
        'new_login': fields.String(),
        'new_password': fields.String(),
    })

wallet_model1 = api.model('Wallet', {
        'login': fields.String(),
        'password': fields.String(),
        'value': fields.Integer(),
        'wallet1_id': fields.Integer(),
        'wallet2_id': fields.Integer(),
})


class UserModel(db_main.Model):
    __tablename__ = 'users'
    # we call our table in db / называем нашу таблицу в базе данных

    id = db_main.Column(db_main.Integer, primary_key=True)
    login = db_main.Column(db_main.String(), unique=True)
    password = db_main.Column(db_main.String())


class WalletModel(db_main.Model):
    __tablename__ = 'wallets'
    # we call our table in db / называем нашу таблицу в базе данных

    id = db_main.Column(db_main.Integer, primary_key=True)
    userID = db_main.Column(db_main.Integer)
    address = db_main.Column(db_main.String())
    net = db_main.Column(db_main.String())
    value = db_main.Column(db_main.Integer)


db_user = UserDB(db_main, UserModel)
db_wal = WalletDB(db_main, WalletModel)


@api.route("/user")
class User(Resource):
    @ns.expect(user_model1)
    def post(self):
        '''New user'''
        time_start = time()
        data = request.get_json()
        if db_user.new_user(data['login'], data['password']):
            return f'время: {time() - time_start}'
        return 'error'

    @ns.expect(user_model2)
    def patch(self):
        '''Change user'''
        time_start = time()
        data = request.get_json()
        if db_user.update_data(data['login'], data['password'], data['new_login'], data['new_password']):
            return f'время: {time() - time_start}'
        return 'error'

    @ns.expect(user_model1)
    def delete(self):
        '''Delete user'''
        time_start = time()
        data = request.get_json()

        if db_user.delete(data['login'], data['password']):
            return f'время: {time() - time_start}'
        return 'error'


@api.route("/wallet")
class Wallet(Resource):
    @ns.expect(user_model1)
    def post(self):
        '''New wallet'''
        time_start = time()
        time_start = time()
        data = request.get_json()
        userID = db_user.find_user(data['login']).user
        if userID.password == data['password']:
            if db_wal.new_wallet(userID.id, get_ip_info()[1], 'не понял, что за сеть нужна', 0):
                return f'время: {time() - time_start}'
            else:
                return 'error'
        else:
            return 'error password'

        pass

    @ns.expect(wallet_model1)
    def patch(self):
        '''Money transfer'''
        # баланс может уйти в минус, тк на это не было условия. Также для пополнения с ничего, нужен пользователь admin
        time_start = time()
        data = request.get_json()
        user = db_user.find_user(data['login']).user
        if user.password == data['password']:
            if user.id == db_wal.find_wallet(data['wallet2_id']).wallet.userID and db_wal.transfer(data['wallet1_id'], data['wallet2_id'], data['value']):
                return f'время: {time() - time_start}'
            elif data['login'] == 'admin':
                if db_wal.transfer(data['wallet1_id'], data['wallet2_id'], data['value'], admin=True):
                    return f'время: {time() - time_start}'
        return 'error'

    @ns.expect(user_model1)
    def put(self):
        '''Sellect all wallet'''
        # put использовать не корректно, надо было написать новый класс, но пытался быстрее
        data = request.get_json()
        userID = db_user.find_user(data['login']).user
        if userID.password == data['password']:
            data = db_wal.sellect_all(userID.id)
            json = {}
            for i in range(len(data)):
                json.update({data[i].id: {'userID': data[i].userID,
                                          'address': data[i].address,
                                          'net': data[i].net,
                                          'value': data[i].value}
                             })
            return jsonify(json)
        return 'error'


if __name__ == "__main__":
    app.app_context().push()
    db_main.drop_all()
    db_main.create_all()
    app.run(debug=True)