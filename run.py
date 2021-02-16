from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from flask_cors import CORS
from flask_mail import Mail, Message

app = Flask(__name__)
api = Api(app)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'some-secret-string'
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True

jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate()
CORS(app)
migrate.init_app(app, db)
admin = Admin(app)
mail = Mail(app)


@app.before_first_request
def create_tables():
    db.create_all()


import views
import models
from resources import UserResources, TeamResources, TaskResources


admin.add_view(ModelView(models.UserModel, db.session))
admin.add_view(ModelView(models.TeamModel, db.session))
admin.add_view(ModelView(models.TaskModel, db.session))
admin.add_view(ModelView(models.DocumentModel, db.session))

api.add_resource(UserResources.UserRegistration, '/registration')
api.add_resource(UserResources.UserLogin, '/login')
api.add_resource(UserResources.UserLogout, '/logout')
api.add_resource(UserResources.TokenRefresh, '/token/refresh')

api.add_resource(UserResources.UserDetails, '/user')
api.add_resource(UserResources.SecretResource, '/secret')

api.add_resource(TeamResources.UserTeams, '/teams')
api.add_resource(TeamResources.TeamDetails, '/team/<int:team_id>')
api.add_resource(TeamResources.TeamDetailsSort,
                 '/team/<int:team_id>/sort')

api.add_resource(TaskResources.CreateTask, '/createtask/<int:team_id>')
api.add_resource(TaskResources.TaskDetails, '/task/<int:task_id>')


# for admin use
api.add_resource(UserResources.AllUsers, '/users')
api.add_resource(UserResources.AdminUser, '/admin/user/<int:user_id>')

api.add_resource(TeamResources.AdminUserTeams, '/admin/<int:user_id>/teams')
api.add_resource(TeamResources.AdminTeamDetails, '/admin/team/<int:team_id>')
api.add_resource(TeamResources.AdminTeamDetailsSort,
                 '/admin/team/<int:team_id>/sort')
api.add_resource(TeamResources.AdminAddMemberToTeam,
                 '/admin/addmember/<int:team_id>/<int:user_id>')

api.add_resource(TaskResources.AdminCreateTask,
                 '/admin/createtask/<int:team_id>')
api.add_resource(TaskResources.AdminTaskDetails, '/admin/task/<int:task_id>')


if __name__ == '__main__':
    app.run()
