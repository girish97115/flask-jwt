from run import db
from marshmallow_sqlalchemy import ModelSchema
from passlib.hash import pbkdf2_sha256 as sha256


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)

    def __init__(self, username, password, email, role, phone):
        self.username = username
        self.password = password
        self.email = email
        self.role = role
        self.phone = phone

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def update_db(self):
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

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


class UsersSchema(ModelSchema):
    class Meta:
        model = UserModel


user_schema = UsersSchema()
users_schema = UsersSchema(many=True)
