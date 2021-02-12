from flask_restful import Resource, reqparse
from models import TeamModel, UserModel, TaskModel
from marshmallow_sqlalchemy import ModelSchema
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity, get_raw_jwt, set_access_cookies, set_refresh_cookies, unset_jwt_cookies)
from flask import jsonify


class TasksSchema(ModelSchema):
    class Meta:
        include_fk = True
        model = TaskModel


task_schema = TasksSchema(
    only=("id", "title", "description", "status", "priority", "reporter_id", "assigne_id"))
tasks_schema = TasksSchema(
    only=("id", "title", "description", "status", "priority", "reporter_id", "assigne_id"), many=True)

task_parser = reqparse.RequestParser()
task_parser.add_argument(
    'title', help='This field cannot be blank', required=True)
task_parser.add_argument('description')
task_parser.add_argument(
    'status', help='This field cannot be blank', required=True)
task_parser.add_argument(
    'priority', help='This field cannot be blank', required=True)
task_parser.add_argument(
    'assigne_id', help='This field cannot be blank', required=True)

task_put_parser = reqparse.RequestParser()
task_put_parser.add_argument('title')
task_put_parser.add_argument('description')
task_put_parser.add_argument('status')
task_put_parser.add_argument('priority')
task_put_parser.add_argument('assigne_id')


class CreateTask(Resource):

    @jwt_required
    def post(self, team_id):
        current_user = get_jwt_identity()
        data = task_parser.parse_args()
        if TaskModel.find_by_title(data['title']):
            return {'message': 'Task {} already exists'. format(data['title'])}, 409

        new_task = TaskModel(
            data['title'], data['status'], data["priority"], current_user, data['assigne_id'])
        if data['description']:
            new_task.description = data['description']
        new_task.team_id = team_id

        try:
            new_task.save_to_db()
            resp = jsonify(
                {'message': 'Task {} was created'.format(data['title'])})
            resp.status_code = 200
            return resp
        except:
            return {'message': 'Something went wrong'}, 500


class TaskDetails(Resource):
    @jwt_required
    def get(self, task_id):
        task = TaskModel.query.get(task_id)
        return task_schema.dump(task)

    @jwt_required
    def put(self, task_id):
        task = TaskModel.query.get(task_id)
        args = task_put_parser.parse_args()
        if args['title']:
            if TaskModel.find_by_title(args['title']):
                return {'message': 'Task with Name {} already exists'. format(args['name'])}, 409
            task.title = args['title']

        if args['description']:
            task.description = args['description']

        if args['status']:
            task.status = args['status']

        if args['priority']:
            task.status = args['priority']

        try:
            task.update_db()
            return {'message': 'User Details Updated'}, 200
        except:
            return {'message': 'Something went wrong'}, 500