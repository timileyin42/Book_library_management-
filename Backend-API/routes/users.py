from flask_restful import Resource
from models import User
from schemas import UserSchema
from app import db

user_schema = UserSchema(many=True)

class UserListResource(Resource):
    def get(self):
        users = User.query.all()
        return user_schema.dump(users)

class UserBorrowedBooksResource(Resource):
    def get(self):
        users_with_books = User.query.filter(User.borrowed_books.any()).all()
        return user_schema.dump(users_with_books)

