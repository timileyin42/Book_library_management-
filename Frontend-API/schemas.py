# frontend_api/schemas.py

from app import ma
from models import User, Book
from marshmallow import fields, validate

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
    borrowed_by = fields.Str(allow_none=True)  # Can be None if the book is not borrowed
    borrowed_until = fields.Date(allow_none=True)  # Can be None if the book is available

