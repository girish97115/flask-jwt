from flask_restful import Resource, reqparse
from models import InviteModel, TeamModel
from marshmallow_sqlalchemy import ModelSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify
from run import mail
from flask_mail import Message

invite_parser = reqparse.RequestParser()
invite_parser.add_argument(
    'email', help='This field cannot be blank', required=True)
invite_parser.add_argument(
    'team_id', help='This field cannot be blank', required=True)


class InviteSchema(ModelSchema):
    class Meta:
        model = InviteModel


invite_schema = InviteSchema(
    only=("email", "team_id"))
invites_schema = InviteSchema(
    only=("email", "team_id"), many=True)


class AdminSendInvite(Resource):
    def post(self):
        args = invite_parser.parse_args()
        invite = InviteModel(args['email'], args['team_id'])
        team = TeamModel.query.get(args['team_id'])
        invite.save_to_db()
        try:
            msg = Message("Alert From Taskify",
                          sender="Taskify@gmail.com",
                          recipients=[args['email']])
            msg.body = "You have been invited to team {} , please sign in to taskify and start Collaborating".format(
                team.name)
            mail.send(msg)
            return invite_schema.dump(invite)
        except Exception as e:
            return {'message': 'Something went wrong'}, 500
