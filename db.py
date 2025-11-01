from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import hashlib, random, string

db = SQLAlchemy()
salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class User(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String, nullable=False)
    reviews: Mapped[str] = mapped_column(db.String, nullable=True)
    favorites: Mapped[str] = mapped_column(db.String, nullable=True)
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "reviews": self.reviews,
            "favorites": self.favorites
        }

class Buisness(db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    category: Mapped[str] = mapped_column(db.String, nullable=False)
    name: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(db.String, nullable=False)
    address: Mapped[str] = mapped_column(db.String, nullable=False)
    phone: Mapped[str] = mapped_column(db.String, nullable=False)
    times: Mapped[str] = mapped_column(db.String, nullable=False)
    reviews: Mapped[str] = mapped_column(db.String, nullable=True)
    rating: Mapped[float] = mapped_column(db.Float, nullable=True)

def init_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    db.init_app(app)

    with app.app_context():
        db.create_all()

def create_user(username, password):
    hashed_password = password#salt + hashlib.sha256(password.encode()).hexdigest()
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    print(username, password)

def create_buisness(category, name, description, address, phone, times):
    new_buisness = Buisness(category=category, name=name, description=description, address=address, phone=phone, times=times)
    db.session.add(new_buisness)
    db.session.commit()

def login_user(username, password):
    user = User.query.filter_by(username=username).first()
    if user:
        if user.password == password:#salt + hashlib.sha256(password.encode()).hexdigest():
            print(username, password)#salt + hashlib.sha256(password.encode()).hexdigest())
            return user.to_dict()
    return False

def create_review(username, buisness_name, review_text, rating):
    buisness = Buisness.query.filter_by(name=buisness_name).first()
    user = User.query.filter_by(username=username).first()
    if buisness:
        if buisness.reviews:
            buisness.reviews += f";{username}:{review_text}:{rating}"
        else:
            buisness.reviews = f"{username}:{review_text}:{rating}"
        db.session.commit()