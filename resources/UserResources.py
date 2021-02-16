from flask_restful import Resource, reqparse
from models import UserModel
from marshmallow_sqlalchemy import ModelSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify


class UsersSchema(ModelSchema):
    class Meta:
        model = UserModel


user_schema = UsersSchema(only=("id", "name", "password", "email", "phone"))
users_schema = UsersSchema(
    only=("id", "name", "password", "email", "phone"), many=True)

user_parser = reqparse.RequestParser()
user_parser.add_argument(
    'name', help='This field cannot be blank', required=True)
user_parser.add_argument(
    'password', help='This field cannot be blank', required=True)
user_parser.add_argument(
    'email', help='This field cannot be blank', required=True)
user_parser.add_argument(
    'phone', help='This field cannot be blank', required=True)

user_login_parser = reqparse.RequestParser()
user_login_parser.add_argument(
    'name', help='This field cannot be blank', required=True)
user_login_parser.add_argument(
    'password', help='This field cannot be blank', required=True)


user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument('name')
user_put_parser.add_argument('password')
user_put_parser.add_argument('email')
user_put_parser.add_argument('phone')


class UserRegistration(Resource):
    def post(self):
        data = user_parser.parse_args()
        if UserModel.find_by_username(data['name']):
            return {'message': 'User {} already exists'. format(data['name'])}, 409
        # new_user = UserModel(
        #     data['username'], UserModel.generate_hash(data['password']), data["email"], data['phone'])
        new_user = UserModel(
            data['name'], data['password'], data["email"], data['phone'])
        try:
            new_user.save_to_db()
            resp = jsonify(
                {'message': 'User {} was created'.format(data['name'])})
            resp.status_code = 200
            return resp
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogin(Resource):
    def post(self):
        data = user_login_parser.parse_args()
        current_user = UserModel.find_by_username(data['name'])
        if not current_user:
            return {'message': 'User {} doesn\'t exist'.format(data['name'])}, 404

        # if UserModel.verify_hash(data['password'], current_user.password):
        if data['password'] == current_user.password:
            access_token = create_access_token(identity=current_user.id)
            refresh_token = create_refresh_token(identity=current_user.id)
            resp = jsonify(
                {'message': 'Logged in as {}'.format(current_user.name)})

            set_access_cookies(resp, access_token)
            set_refresh_cookies(resp, refresh_token)
            return resp

        else:
            return {'message': 'Wrong credentials'}, 500


class UserLogout(Resource):
    def post(self):
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        resp.status_code = 200
        return resp


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        resp = jsonify({'refresh': True})
        set_access_cookies(resp, access_token)
        resp.status_code = 200
        return resp


class AllUsers(Resource):
    def get(self):
        return UserModel.return_all()

    def delete(self):
        return UserModel.delete_all()


class UserDetails(Resource):
    @jwt_required
    def get(self):
        id = get_jwt_identity()
        current_user = UserModel.query.get(id)
        return user_schema.dump(current_user)

    @jwt_required
    def put(self):
        id = get_jwt_identity()
        current_user = UserModel.query.get(id)
        args = user_put_parser.parse_args()
        if args['name']:
            if UserModel.find_by_username(args['name']):
                return {'message': 'User {} already exists'. format(args['name'])}, 409
            current_user.name = args['name']

        if args['password']:
            current_user.password = UserModel.generate_hash(args['password'])

        if args['email']:
            current_user.email = args['email']

        if args['phone']:
            current_user.phone = args['phone']

        try:
            current_user.update_db()
            return {'message': 'User Details Updated'}, 200
        except:
            return {'message': 'Something went wrong'}, 500


class SecretResource(Resource):
    @jwt_required
    def get(self):
        return {
            'answer': 42
        }


class AdminUser(Resource):
    def get(self, user_id):
        current_user = UserModel.query.get(user_id)
        return user_schema.dump(current_user)

    def put(self, user_id):
        current_user = UserModel.query.get(user_id)
        args = user_put_parser.parse_args()
        if args['username']:
            if UserModel.find_by_username(args['username']):
                return {'message': 'User {} already exists'. format(args['username'])}, 409
            current_user.username = args['username']

        if args['password']:
            current_user.password = UserModel.generate_hash(args['password'])

        if args['email']:
            current_user.email = args['email']

        if args['phone']:
            current_user.phone = args['phone']
        try:
            current_user.update_db()
            return {'message': 'User Details Updated'}, 200
        except:
            return {'message': 'Something went wrong'}, 500
