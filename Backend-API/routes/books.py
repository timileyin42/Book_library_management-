from flask_restful import Resource
from models import Book
from schemas import BookSchema
from app import db

book_schema = BookSchema(many=True)

class BookListResource(Resource):
    def get(self):
        books = Book.query.filter_by(available=True).all()
        return book_schema.dump(books)

    def post(self):
        # Logic to add a book
        pass

class BookResource(Resource):
    def get(self, book_id):
        book = Book.query.get_or_404(book_id)
        return book_schema.dump(book)

    def delete(self, book_id):
        # Logic to remove a book
        pass

class UnavailableBooksResource(Resource):
    def get(self):
        unavailable_books = Book.query.filter_by(available=False).all()
        return book_schema.dump(unavailable_books)

