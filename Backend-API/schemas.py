# backend_api/schemas.py

from app import ma
from models import User, Book
from marshmallow import fields, validate, ValidationError, validates
import re

class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing User model data."""
    
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        fields = ('id', 'email', 'first_name', 'last_name', 'borrowed_books')

    email = fields.Email(required=True, validate=validate.Length(max=120))
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))

    @validates('email')
    def validate_email(self, value):
        """Additional email format validation."""
        email_regex = r'^\S+@\S+\.\S+$'
        if not re.match(email_regex, value):
            raise ValidationError('Invalid email format.')

class BookSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing Book model data."""
    
    class Meta:
        model = Book
        include_fk = True
        load_instance = True
        fields = ('id', 'title', 'author', 'publisher', 'category', 'available', 'borrowed_by', 'borrowed_until')

    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    author = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    publisher = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    available = fields.Boolean(required=True)
    borrowed_by = fields.Int(allow_none=True)  # Assuming user IDs are integers
    borrowed_until = fields.Date(allow_none=True)

