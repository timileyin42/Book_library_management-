from flask_restful import Resource
from models import User
from app import db
from schemas import UserSchema
from werkzeug.exceptions import Conflict, BadRequest
import logging

user_schema = UserSchema()
users_schema = UserSchema(many=True)

logger = logging.getLogger(__name__)

class UserListResource(Resource):
    """Resource to handle user operations."""

    def post(self):
        json_data = request.get_json()
        if not json_data:
            logger.warning("No input data provided for user creation")
            raise BadRequest(description="No input data provided")
        
        # Validate and deserialize input
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            logger.warning(f"Validation error during user creation: {err.messages}")
            raise BadRequest(description=err.messages)
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            logger.warning(f"Attempt to create duplicate user with email: {data['email']}")
            raise Conflict(description="User with this email already exists")
        
        # Create new user
        new_user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        db.session.add(new_user)
        db.session.commit()
        
        logger.info(f"Created new user: {new_user.email} (ID: {new_user.id})")
        return user_schema.dump(new_user), 201

    def get(self):
        """List all enrolled users."""
        users = User.query.all()
        return users_schema.dump(users), 200
