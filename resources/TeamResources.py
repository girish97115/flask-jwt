from flask_restful import Resource, reqparse
from models import TeamModel, UserModel
from marshmallow_sqlalchemy import ModelSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify


class TeamsSchema(ModelSchema):
    class Meta:
        model = TeamModel


team_schema = TeamsSchema(only=("id", "name", "description", "tasks"))
teams_schema = TeamsSchema(only=("id", "name", "description"), many=True)

team_parser = reqparse.RequestParser()
team_parser.add_argument(
    'name', help='This field cannot be blank', required=True)
team_parser.add_argument(
    'description', help='This field cannot be blank', required=True)

team_put_parser = reqparse.RequestParser()
team_put_parser.add_argument('name')
team_put_parser.add_argument('description')


class UserTeams(Resource):
    @jwt_required
    def get(self):
        id = get_jwt_identity()
        current_user = UserModel.query.get(id)
        user_teams = current_user.teams
        return teams_schema.dump(user_teams)


class TeamDetails(Resource):
    @jwt_required
    def get(self, team_id):
        team = TeamModel.query.get(team_id)
        return team_schema.dump(team)

    @jwt_required
    def put(self, team_id):
        team = TeamModel.query.get(team_id)
        args = team_put_parser.parse_args()
        if args['name']:
            if TeamModel.find_by_username(args['name']):
                return {'message': 'Team with Name {} already exists'. format(args['name'])}, 409
            team.name = args['name']

        if args['description']:
            team.description = args['description']

        try:
            team.update_db()
            return {'message': 'User Details Updated'}, 200
        except:
            return {'message': 'Something went wrong'}, 500
