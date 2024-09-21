from flask_restful import Resource
from models import Book, User
from app import db
from schemas import BookSchema
from datetime import datetime, timedelta
from werkzeug.exceptions import BadRequest, NotFound, Conflict
from marshmallow import ValidationError
import logging

book_schema = BookSchema()
books_schema = BookSchema(many=True)

logger = logging.getLogger(__name__)

class BookListResource(Resource):
    def get(self):
        publisher = request.args.get('publisher', type=str)
        category = request.args.get('category', type=str)
        
        query = Book.query.filter_by(available=True)
        
        if publisher:
            query = query.filter(Book.publisher.ilike(f"%{publisher}%"))
        if category:
            query = query.filter(Book.category.ilike(f"%{category}%"))
        
        books = query.all()
        logger.info(f"Listed {len(books)} books with filters: publisher={publisher}, category={category}")
        return books_schema.dump(books), 200

class BookResource(Resource):
    def get(self, book_id):
        book = Book.query.filter_by(id=book_id, available=True).first()
        if not book:
            logger.warning(f"Book with ID {book_id} not found or not available")
            raise NotFound(description="Book not found or not available")
        logger.info(f"Retrieved book: {book.title} (ID: {book.id})")
        return book_schema.dump(book), 200

class BookBorrowResource(Resource):
    def post(self, book_id):
        json_data = request.get_json()
        if not json_data:
            logger.warning("No input data provided for borrowing a book")
            raise BadRequest(description="No input data provided")
        
        # Define a BorrowSchema for input validation
        class BorrowSchema(ma.Schema):
            user_id = fields.Str(required=True)
            days = fields.Int(required=True, validate=validate.Range(min=1, max=365))
        
        borrow_schema = BorrowSchema()
        
        # Validate and deserialize input
        try:
            data = borrow_schema.load(json_data)
        except ValidationError as err:
            logger.warning(f"Validation error during book borrowing: {err.messages}")
            raise BadRequest(description=err.messages)
        
        book = Book.query.filter_by(id=book_id, available=True).first()
        if not book:
            logger.warning(f"Attempt to borrow unavailable or non-existent book ID: {book_id}")
            raise Conflict(description="Book not available for borrowing")
        
        user = User.query.filter_by(id=data['user_id']).first()
        if not user:
            logger.warning(f"Attempt to borrow book with invalid user ID: {data['user_id']}")
            raise NotFound(description="User not found")
        
        # Update book status
        book.available = False
        book.borrowed_by = user.id
        book.borrowed_until = datetime.utcnow().date() + timedelta(days=data['days'])
        db.session.commit()
        
        logger.info(f"Book ID {book.id} borrowed by User ID {user.id} until {book.borrowed_until}")
        return {'message': f'Book borrowed until {book.borrowed_until}'}, 200

