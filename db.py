from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, session
import hashlib, random, string
import json
import random


db = SQLAlchemy()
salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
    reviews: Mapped[str] = mapped_column(db.String, nullable=True)
    favorites: Mapped[str] = mapped_column(db.String, nullable=True)
    businesses: Mapped[str] = mapped_column(db.String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "reviews": self.reviews,
            "favorites": self.favorites,
            "password" : self.password,
            "businesses": self.businesses,
        }

class Business(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    category: Mapped[str] = mapped_column(db.String, nullable=False)
    name: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.String, nullable=False)
    address: Mapped[str] = mapped_column(db.String, nullable=False)
    phone: Mapped[str] = mapped_column(db.String, nullable=False)
    times: Mapped[str] = mapped_column(db.String, nullable=False)
    reviews: Mapped[str] = mapped_column(db.String, nullable=True)
    rating: Mapped[float] = mapped_column(db.Float, nullable=True)
    uniqueId: Mapped[int] = mapped_column(db.String, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "reviews": self.reviews,
            "uniqueId": self.uniqueId,
        }

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    db.init_app(app)

    with app.app_context():
        db.create_all()

def create_user(username, password):
    hashed_password = password#salt + hashlib.sha256(password.encode()).hexdigest()
    new_user = User(username=username, password=hashed_password, reviews="{}", favorites="[]", businesses="[]")
    db.session.add(new_user)
    db.session.commit()
    return new_user.to_dict()

def create_business(owner, category, name, description, address, phone, times):
    rand_id = random.randint(0, 9999) * 100 + random.randint(0, 999999)
    new_business = Business(category=category, name=name, description=description, address=address, phone=phone, times=times, reviews="{}", rating=0, uniqueId=rand_id)
    
    user = User.query.filter_by(username=owner).first()

    business_id_list = json.loads(user.businesses)
    business_id_list.append(rand_id)
    user.businesses = json.dumps(business_id_list)
    
    db.session.add(new_business)
    db.session.commit()

    return user.businesses

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:#salt + hashlib.sha256(password.encode()).hexdigest():
            return user.to_dict()
    return False

def create_review(username, business_name, review_text, rating):
    business = Business.query.filter_by(name=business_name).first()
    user = User.query.filter_by(username=username).first()
    if business:
        business_review_dict = json.loads(business.reviews)
        business_review_dict[username] =  [rating, review_text]
        business.reviews = json.dumps(business_review_dict)
        review_count = len(business_review_dict)-1
        business.rating = (business.rating*review_count + rating) / len(business_review_dict)
        
        user_review_dict = json.loads(user.reviews)
        user_review_dict[business_name] = [rating, review_text]
        user.reviews = json.dumps(user_review_dict)

        db.session.commit()

def query_reviews(business_name=None, username=None):
    if business_name:
        business = Business.query.filter_by(name=business_name).first()
        if business and business.reviews:
            return json.loads(business.reviews)
    if username:
        user = User.query.filter_by(username=username).first()
        if user and user.reviews:
            return json.loads(user.reviews)
    return None

def query_business(id):
    return Business.query.get_or_404(id)

def change_password(username, new_password):
    user = User.query.filter_by(username=username).first()
    if user:
        user.password = new_password#salt + hashlib.sha256(new_password.encode()).hexdigest()
        db.session.commit()
        return user.to_dict()
    return False

def check_username(username):
    user = User.query.filter_by(username=username).first()
    if user:
        return True
    return False


def change_favorite(username, business_name):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.favorites:
            favorites = json.loads(user.favorites)
        else:
            favorites = {}

        if business_name not in favorites:
            favorites.append(business_name)
        else:
            favorites.remove(business_name)

        user.favorites = json.dumps(favorites)
        db.session.commit()
        return favorites
    
    return False

def query_favorites(username):
    user = User.query.filter_by(username=username).first()
    if user and user.favorites:
        return json.loads(user.favorites)
    return False

def delete_business(owner, uid):
    business = Business.query.filter_by(uniqueId=uid).first()

    owner = User.query.filter_by(username=owner).first()
    business_id_list = json.loads(owner.businesses)
    uid = int(uid)
    business_id_list.remove(uid)
    owner.businesses = json.dumps(business_id_list)

    db.session.delete(business)
    db.session.commit()