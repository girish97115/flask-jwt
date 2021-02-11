from flask_restful import Resource, reqparse
from models import TeamModel
from marshmallow_sqlalchemy import ModelSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify


class TeamsSchema(ModelSchema):
    class Meta:
        model = TeamModel


user_schema = TeamsSchema()
users_schema = TeamsSchema(many=True)

user_parser = reqparse.RequestParser()
user_parser.add_argument(
    'name', help='This field cannot be blank', required=True)
user_parser.add_argument(
    'description', help='This field cannot be blank', required=True)
