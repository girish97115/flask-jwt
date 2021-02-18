from flask_restful import Resource, reqparse
from models import InviteModel, TeamModel, UserModel
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
    only=("mail", "team_id", "id"))
invites_schema = InviteSchema(
    only=("mail", "team_id", "id"), many=True)


class AdminSendInvite(Resource):
    def post(self):
        args = invite_parser.parse_args()
        user = UserModel.query.filter_by(email=args['email']).first()
        print(user)
        if user:
            team = TeamModel.query.get(args['team_id'])
            try:
                if team in user.teams:
                    return {'message': 'User Already in team {}'.format(team.name)}
                user.teams.append(team)
                user.save_to_db
                msg = Message("Alert From Taskify",
                              sender="Taskify@gmail.com",
                              recipients=[args['email']])
                msg.body = "You have been added to team {} , please sign in to taskify and start Collaborating, https://taskify-initial.herokuapp.com/login".format(
                    team.name)
                mail.send(msg)
                return {'message': 'User Added to the team'}
            except Exception as e:
                return {'message1': str(e)}, 500

        else:
            invite = InviteModel(args['email'], args['team_id'])
            team = TeamModel.query.get(args['team_id'])
            invite.save_to_db()
            try:
                msg = Message("Alert From Taskify",
                              sender="Taskify@gmail.com",
                              recipients=[args['email']])
                msg.body = "You have been invited to team {} , please sign up to taskify and start Collaborating, https://taskify-initial.herokuapp.com/register/{}".format(
                    team.name, invite.id)
                mail.send(msg)
                return invite_schema.dump(invite)
            except Exception as e:
                return {'message2': str(e)}, 500
