from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask import Flask
bcrypt = Bcrypt()
db = SQLAlchemy()




class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(250), nullable=True)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

class Plant(db.Model):
    __tablename__ = 'plants'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    plant_name = db.Column(db.String(100))
    plant_type = db.Column(db.String(100))
    last_watered = db.Column(db.DateTime)
    sunlight_requirements = db.Column(db.String(50))
    watering_frequency = db.Column(db.String(50))



class FavoritePlant(db.Model):
    __tablename__ = 'favorites'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Fixed table name
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'))
    
    user = db.relationship('User', backref='favorites')  # Relationship with backref
    plant = db.relationship('Plant', backref='favorited_by')  # Relationship with backref


class PlantCare(db.Model):
    __tablename__ = 'plant_care_guides'
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plants.id'))
    care_task = db.Column(db.String(50))
    frequency = db.Column(db.String(50))
    details = db.Column(db.Text)

class PlantDisease(db.Model):
    __tablename__ = 'plant_diseases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    treatment = db.Column(db.Text)

