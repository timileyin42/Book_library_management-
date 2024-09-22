from app import db
import uuid
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    borrowed_books = db.relationship('Book', backref='borrower', lazy=True)
    
    def __repr__(self):
        return f'<User {self.email}>'

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    publisher = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    available = db.Column(db.Boolean, default=True, nullable=False)
    borrowed_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    borrowed_until = db.Column(db.Date, nullable=True)
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'

    def borrow(self, user_id, days):
        """Mark the book as borrowed by a user."""
        self.available = False
        self.borrowed_by = user_id
        self.borrowed_until = datetime.utcnow().date() + timedelta(days=days)
