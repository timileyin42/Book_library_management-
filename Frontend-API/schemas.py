# schemas.py

from marshmallow import fields, validate, ValidationError, validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models import User, Book
from app import ma  # Ensure this import is present

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True  # This allows for foreign key fields to be included

    email = fields.Email(required=True, validate=validate.Length(max=120))

    @validates('email')  # Use the imported validates
    def validate_email(self, value):
        if '@' not in value:
            raise ValidationError('Invalid email format.')

class BookSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        include_fk = True  # This allows for foreign key fields to be included

    title = fields.String(required=True, validate=validate.Length(max=200))
    author = fields.String(required=True, validate=validate.Length(max=100))
    published_date = fields.Date()
    isbn = fields.String(validate=validate.Length(equal=13))  # Assuming ISBN is a 13-digit number

