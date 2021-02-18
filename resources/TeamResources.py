from flask_restful import Resource, reqparse
from models import TeamModel, UserModel, TaskModel
from marshmallow_sqlalchemy import ModelSchema
import marshmallow.fields as fields
from marshmallow_sqlalchemy.fields import Nested
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify
from run import mail
from flask_mail import Message


class UsersSchema(ModelSchema):
    class Meta:
        model = UserModel


user_schema = UsersSchema(only=("id", "name", "password", "email", "phone"))
users_schema = UsersSchema(
    only=("id", "name", "password", "email", "phone"), many=True)


class TasksPutSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = TaskModel


task_get_schema = TasksPutSchema(
    only=("id", "title", "description", "status", "priority", "reporter_id", "assigne_id", "planneddate"))
tasks_get_schema = TasksPutSchema(
    only=("id", "title", "description", "status", "priority", "reporter_id", "assigne_id", "planneddate"), many=True)


class TasksSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = TaskModel


task_schema = TasksSchema(
    only=("id", "title", "description", "status", "priority", "reporter_id", "assigne_id", "planneddate"))
tasks_schema = TasksSchema(
    only=("id", "title", "description", "status", "priority", "reporter_id", "assigne_id", "planneddate"), many=True)


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

task_sort_param_parser = reqparse.RequestParser()
task_sort_param_parser.add_argument(
    'type', help='type of sort("priority" , "assigne_id", "planneddate") should not be empty', required=True)
task_sort_param_parser.add_argument('id')


class UserTeams(Resource):
    @ jwt_required
    def get(self):
        id = get_jwt_identity()
        current_user = UserModel.query.get(id)
        user_teams = current_user.teams
        return teams_schema.dump(user_teams)


class TeamDetails(Resource):
    @ jwt_required
    def get(self, team_id):
        team = TeamModel.query.get(team_id)
        response = {'id': team_id, 'name': team.name,
                    'description': team.description, 'members': users_schema.dump(team.members)}

        task_list = []
        tasks = TaskModel.query.filter_by(team_id=team_id)
        for task in tasks:
            task_list.append(task.id)
        response['tasks'] = task_list

        lists = []

        todo = {'name': 'Todo'}
        todotasks = tasks_schema.dump(
            TaskModel.query.filter_by(status='Todo', team_id=team_id))
        for task in todotasks:
            if task['assigne_id']:
                task['assigne_id'] = user_schema.dump(
                    UserModel.query.get(task['assigne_id']))
        todo['tasks'] = todotasks
        lists.append(todo)

        InProgess = {'name': 'InProgress'}
        InProgesstasks = tasks_schema.dump(
            TaskModel.query.filter_by(status='InProgress', team_id=team_id))
        for task in InProgesstasks:
            if task['assigne_id']:
                task['assigne_id'] = user_schema.dump(
                    UserModel.query.get(task['assigne_id']))
        InProgess['tasks'] = InProgesstasks
        lists.append(InProgess)

        Completed = {'name': 'Completed'}
        Completedtasks = tasks_schema.dump(
            TaskModel.query.filter_by(status='Completed', team_id=team_id))
        for task in Completedtasks:
            if task['assigne_id']:
                task['assigne_id'] = user_schema.dump(
                    UserModel.query.get(task['assigne_id']))
        Completed['tasks'] = Completedtasks
        lists.append(Completed)

        response['lists'] = lists
        return jsonify(response)

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


class TeamDetailsSort(Resource):
    @jwt_required
    def post(self, team_id):
        team = TeamModel.query.get(team_id)
        args = task_sort_param_parser.parse_args()
        response = {'id': team_id, 'name': team.name,
                    'description': team.description, 'members': users_schema.dump(team.members)}

        task_list = []
        tasks = TaskModel.query.filter_by(team_id=team_id)
        for task in tasks:
            task_list.append(task.id)
        response['tasks'] = task_list

        lists = []

        if args['type'] == "priority":

            todo = {'name': 'Todo'}
            todotasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Todo', priority='Major', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Todo', priority='Normal', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Todo', priority='Minor', team_id=team_id))
            for task in todotasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            todo['tasks'] = todotasks
            lists.append(todo)

            InProgess = {'name': 'InProgress'}
            InProgesstasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='InProgress', priority='Major', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='InProgress', priority='Normal', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='InProgress', priority='Minor', team_id=team_id))
            for task in InProgesstasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            InProgess['tasks'] = InProgesstasks
            lists.append(InProgess)

            Completed = {'name': 'Completed'}
            Completedtasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Completed', priority='Major', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Completed', priority='Normal', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Completed', priority='Minor', team_id=team_id))
            for task in Completedtasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            Completed['tasks'] = Completedtasks
            lists.append(Completed)

        if args['type'] == "planneddate":

            todo = {'name': 'Todo'}
            todotasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Todo', team_id=team_id).order_by('planneddate')[::-1])
            for task in todotasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            todo['tasks'] = todotasks
            lists.append(todo)

            InProgess = {'name': 'InProgress'}
            InProgesstasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='InProgress', team_id=team_id).order_by('planneddate')[::-1])
            for task in InProgesstasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            InProgess['tasks'] = InProgesstasks
            lists.append(InProgess)

            Completed = {'name': 'Completed'}
            Completedtasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Completed', team_id=team_id).order_by('planneddate')[::-1])
            for task in Completedtasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            Completed['tasks'] = Completedtasks
            lists.append(Completed)

        if args['type'] == "assigne_id":
            assigne_id = args['id']
            todo = {'name': 'Todo'}
            todotasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Todo', team_id=team_id, assigne_id=assigne_id))
            for task in todotasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            todo['tasks'] = todotasks
            lists.append(todo)

            InProgess = {'name': 'InProgress'}
            InProgesstasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='InProgress', team_id=team_id, assigne_id=assigne_id))
            for task in InProgesstasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            InProgess['tasks'] = InProgesstasks
            lists.append(InProgess)

            Completed = {'name': 'Completed'}
            Completedtasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Completed', team_id=team_id, assigne_id=assigne_id))
            for task in Completedtasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            Completed['tasks'] = Completedtasks
            lists.append(Completed)

        response['lists'] = lists
        return jsonify(response)


class AdminUserTeams(Resource):
    def get(self, user_id):

        current_user = UserModel.query.get(user_id)
        user_teams = current_user.teams
        return teams_schema.dump(user_teams)


class AdminTeamDetails(Resource):
    def get(self, team_id):
        team = TeamModel.query.get(team_id)
        response = {'id': team_id, 'name': team.name,
                    'description': team.description, 'members': users_schema.dump(team.members)}

        task_list = []
        tasks = TaskModel.query.filter_by(team_id=team_id)
        for task in tasks:
            task_list.append(task.id)
        response['tasks'] = task_list

        lists = []

        todo = {'name': 'Todo'}
        todotasks = tasks_schema.dump(
            TaskModel.query.filter_by(status='Todo', team_id=team_id))
        for task in todotasks:
            if task['assigne_id']:
                task['assigne_id'] = user_schema.dump(
                    UserModel.query.get(task['assigne_id']))
        todo['tasks'] = todotasks
        lists.append(todo)

        InProgess = {'name': 'InProgress'}
        InProgesstasks = tasks_schema.dump(
            TaskModel.query.filter_by(status='InProgress', team_id=team_id))
        for task in InProgesstasks:
            if task['assigne_id']:
                task['assigne_id'] = user_schema.dump(
                    UserModel.query.get(task['assigne_id']))
        InProgess['tasks'] = InProgesstasks
        lists.append(InProgess)

        Completed = {'name': 'Completed'}
        Completedtasks = tasks_schema.dump(
            TaskModel.query.filter_by(status='Completed', team_id=team_id))
        for task in Completedtasks:
            if task['assigne_id']:
                task['assigne_id'] = user_schema.dump(
                    UserModel.query.get(task['assigne_id']))
        Completed['tasks'] = Completedtasks
        lists.append(Completed)

        response['lists'] = lists
        return jsonify(response)

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


class AdminTeamDetailsSort(Resource):
    def post(self, team_id):
        team = TeamModel.query.get(team_id)
        args = task_sort_param_parser.parse_args()
        response = {'id': team_id, 'name': team.name,
                    'description': team.description, 'members': users_schema.dump(team.members)}

        task_list = []
        tasks = TaskModel.query.filter_by(team_id=team_id)
        for task in tasks:
            task_list.append(task.id)
        response['tasks'] = task_list

        lists = []

        if args['type'] == "priority":

            todo = {'name': 'Todo'}
            todotasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Todo', priority='Major', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Todo', priority='Normal', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Todo', priority='Minor', team_id=team_id))
            for task in todotasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            todo['tasks'] = todotasks
            lists.append(todo)

            InProgess = {'name': 'InProgress'}
            InProgesstasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='InProgress', priority='Major', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='InProgress', priority='Normal', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='InProgress', priority='Minor', team_id=team_id))
            for task in InProgesstasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            InProgess['tasks'] = InProgesstasks
            lists.append(InProgess)

            Completed = {'name': 'Completed'}
            Completedtasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Completed', priority='Major', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Completed', priority='Normal', team_id=team_id)) + tasks_schema.dump(TaskModel.query.filter_by(status='Completed', priority='Minor', team_id=team_id))
            for task in Completedtasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            Completed['tasks'] = Completedtasks
            lists.append(Completed)

        if args['type'] == "planneddate":

            todo = {'name': 'Todo'}
            todotasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Todo', team_id=team_id).order_by('planneddate')[::-1])
            for task in todotasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            todo['tasks'] = todotasks
            lists.append(todo)

            InProgess = {'name': 'InProgress'}
            InProgesstasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='InProgress', team_id=team_id).order_by('planneddate')[::-1])
            for task in InProgesstasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            InProgess['tasks'] = InProgesstasks
            lists.append(InProgess)

            Completed = {'name': 'Completed'}
            Completedtasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Completed', team_id=team_id).order_by('planneddate')[::-1])
            for task in Completedtasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            Completed['tasks'] = Completedtasks
            lists.append(Completed)

        if args['type'] == "assigne_id":
            assigne_id = args['id']
            todo = {'name': 'Todo'}
            todotasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Todo', team_id=team_id, assigne_id=assigne_id))
            for task in todotasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            todo['tasks'] = todotasks
            lists.append(todo)

            InProgess = {'name': 'InProgress'}
            InProgesstasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='InProgress', team_id=team_id, assigne_id=assigne_id))
            for task in InProgesstasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            InProgess['tasks'] = InProgesstasks
            lists.append(InProgess)

            Completed = {'name': 'Completed'}
            Completedtasks = tasks_schema.dump(
                TaskModel.query.filter_by(status='Completed', team_id=team_id, assigne_id=assigne_id))
            for task in Completedtasks:
                if task['assigne_id']:
                    task['assigne_id'] = user_schema.dump(
                        UserModel.query.get(task['assigne_id']))
            Completed['tasks'] = Completedtasks
            lists.append(Completed)

        response['lists'] = lists
        return jsonify(response)


class AdminAddMemberToTeam(Resource):
    def post(self, team_id, user_id):
        user = UserModel.query.get(user_id)
        team = TeamModel.query.get(team_id)

        team.members.append(user)
        team.update_db()

        try:
            msg = Message("Alert From Taskify",
                          sender="Taskify@gmail.com",
                          recipients=[user.email])
            msg.body = "You have been added to team {} , please sign in to taskify and start Collaborating".format(
                team.name)
            mail.send(msg)
            return {"message": "added user {} to team {}, Mail Sent".format(user.name, team.name)}
        except Exception as e:
            return "added user {} to team {}, Mail Failed".format(user.name, team.name)
