# frontend_api/routes/books.py

from flask import request, jsonify
from flask_restful import Resource
from models import Book, User
from app import db
from schemas import BookSchema
from marshmallow import ValidationError
from datetime import datetime, timedelta
import os
import requests

book_schema = BookSchema()
books_schema = BookSchema(many=True)

class BookListResource(Resource):
    """Resource to handle book operations."""

    def get(self):
        """List all available books."""
        books = Book.query.filter_by(available=True).all()
        return books_schema.dump(books), 200

    def post(self):
        """Add a new book to the catalogue."""
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        # Validate and deserialize input
        try:
            data = book_schema.load(json_data)
        except ValidationError as err:
            return {"message": err.messages}, 400

        # Create new book
        book = Book(**data)
        db.session.add(book)
        db.session.commit()

        # Notify Backend API about the new book (if needed)
        backend_api_url = os.getenv('BACKEND_API_URL', 'http://backend_api:8001/books/update')
        try:
            requests.post(backend_api_url, json=book_schema.dump(book))
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to notify Backend API: {e}")

        return book_schema.dump(book), 201

class BookResource(Resource):
    """Resource for a single book."""

    def get(self, book_id):
        """Retrieve a single book by ID."""
        book = Book.query.get_or_404(book_id)
        return book_schema.dump(book), 200

    def delete(self, book_id):
        """Remove a book from the catalogue."""
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted successfully"}, 204

class BookBorrowResource(Resource):
    """Resource for borrowing a book."""

    def post(self, book_id):
        """Borrow a book."""
        book = Book.query.get_or_404(book_id)
        if not book.available:
            return {"message": "Book not available for borrowing"}, 400

        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        user_id = json_data.get('user_id')
        days = json_data.get('days', 14)  # Default to 14 days if not specified

        if not user_id:
            return {"message": "User ID is required"}, 400

        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return {"message": "User not found"}, 404

        # Update book status
        book.available = False
        book.borrowed_by = user.id
        book.borrowed_until = datetime.utcnow().date() + timedelta(days=days)
        db.session.commit()

        # Notify Backend API about the borrowing event (if needed)
        backend_api_url = os.getenv('BACKEND_API_URL', 'http://backend_api:8001/books/update')
        try:
            requests.post(backend_api_url, json=book_schema.dump(book))
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to notify Backend API: {e}")

        return {"message": f"Book borrowed until {book.borrowed_until}"}, 200

class BookUpdateResource(Resource):
    """Resource to handle book updates from the Backend API."""

    def post(self):
        """Receive updates about books."""
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data provided"}, 400

        # Validate and deserialize input
        try:
            data = book_schema.load(json_data)
        except ValidationError as err:
            return {"message": err.messages}, 400

        # Update or add the book in the frontend database
        book = Book.query.get(data['id'])
        if book:
            # Update existing book
            book.title = data['title']
            book.author = data['author']
            book.publisher = data['publisher']
            book.category = data['category']
            book.available = data['available']
            book.borrowed_by = data.get('borrowed_by')
            book.borrowed_until = data.get('borrowed_until')
        else:
            # Add new book
            new_book = Book(**data)
            db.session.add(new_book)

        db.session.commit()
        return {"message": "Book updated successfully"}, 200

