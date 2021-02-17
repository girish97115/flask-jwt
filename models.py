from run import db, admin
from marshmallow_sqlalchemy import ModelSchema
from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy.sql import func


userteam = db.Table('userteam',
                    db.Column('user_id', db.Integer, db.ForeignKey(
                        'users.id')),
                    db.Column('team_id', db.Integer, db.ForeignKey(
                        'teams.id'))
                    )


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False, default='user')
    phone = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), onupdate=func.now())
    assigned_issues = db.relationship(
        "TaskModel", backref='assigne', lazy='dynamic', foreign_keys='TaskModel.assigne_id')
    reporter_issues = db.relationship(
        "TaskModel", backref='reporter', lazy='dynamic', foreign_keys='TaskModel.reporter_id')
    documents = db.relationship(
        "DocumentModel", backref='uploader', lazy='dynamic', foreign_keys='DocumentModel.uploader_id')
    teams = db.relationship('TeamModel', secondary=userteam,
                            backref=db.backref('members', lazy='dynamic'))

    def __repr__(self):
        return '<User model {}, {}>'.format(self.id, self.name)

    def __init__(self, username, password, email, phone):
        self.name = username
        self.password = password
        self.email = email
        self.phone = phone

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(name=username).first()

    @classmethod
    def return_all(cls):
        users = cls.query.all()
        return users_schema.dump(users)

    @classmethod
    def delete_all(cls):
        try:
            num_rows_deleted = db.session.query(cls).delete()
            db.session.commit()
            return {'message': '{} row(s) deleted'.format(num_rows_deleted)}
        except:
            return {'message': 'Something went wrong'}

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, hash):
        return sha256.verify(password, hash)


class TeamModel(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(129))
    tasks = db.relationship("TaskModel", backref='team')
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return '<Team model {}, {}>'.format(self.id, self.name)

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(name=username).first()


class TaskModel(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String())
    status = db.Column(db.String(120), nullable=False)
    priority = db.Column(db.String(120), nullable=False)
    planneddate = db.Column(db.Date())
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigne_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    documents = db.relationship(
        "DocumentModel", backref='task', lazy='dynamic', foreign_keys='DocumentModel.task_id')
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return '<Task model {}, {}>'.format(self.id, self.title)

    def __init__(self, title, status, priority):
        self.title = title
        self.status = status
        self.priority = priority

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    @classmethod
    def find_by_title(cls, title):
        return cls.query.filter_by(title=title).first()


class DocumentModel(db.Model):
    __tablename__ = 'document'

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    name = db.Column(db.String(120), unique=True, nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return '<Document model {}, {}>'.format(self.id, self.name)

    def __init__(self, name):
        self.name = name

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

class InviteModel(db.Model):
    __tablename__ = 'invite'

    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(120), nullable=False)
    team_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return '<Invite model {}, {}>'.format(self.id, self.mail)

    def __init__(self, mail, team_id):
        self.mail = mail
        self.team_id = team_id

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()


class UsersSchema(ModelSchema):
    class Meta:
        model = UserModel


user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
