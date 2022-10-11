from datetime import datetime
datetime.utcnow()
# Imported datetime to solve AttributeError: module 'datetime' has no attribute 'utcnow'on the Show class model this error
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
db = SQLAlchemy()
migrate=Migrate(app, db)


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    genres= db.Column(db.String(120))
    website_link= db.Column(db.String(500))
    seeking_talent= db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    #Many to many relationship
    shows = db.relationship('Show', backref=db.backref('venue', lazy=True))
    def __repr__(self):
      return f'< Venue {self.id} {self.name}{self.city}>'

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    ## TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(500))
    seeking_venue= db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    #Many to many relationship
    shows = db.relationship('Show', backref=db.backref('artist', lazy=True))
  
    
# # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer,primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    start_time=db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  
    def __repr__(self):
      return f'< Show{self.id} Artist{self.artist_id} Venue{self.venue_id}>'
      