#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import Venue, Artist, Show, db , app
import collections
collections.Callable = collections.abc.Callable
import sys
from flask_wtf.csrf import CSRFProtect
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#


moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#csrf = CSRFProtect(app), keep getting errors, still working on it
#embedded the csrf token in the corresponding html pages as hidden


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
      
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
# TypeError: Parser must be a string or character stream, not datetime, to fix this error included the 
# if isinstance(value,str) to use Show.start_time as a parameter in def show()
def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
      date = value    
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
# TODO: replace with real venues data.
# num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  #first search to get the cities and states
  first_search= Venue.query.distinct(Venue.city,Venue.state).all()#using order_by isnt listing unique values
  now=datetime.now()
  for venue in first_search:
    #data.append({"city":venue.city,"state":venue.state}),appending to data initially results  a display with a quotation, and redundent venues
    ##we get the inital output :New York, NY,San Francisco, CA
    #second search to filter venues according to their state and city
    second_search = Venue.query.filter_by(state=venue.state).filter_by(city=venue.city).all()
    venues = []
    #setting the venues to empty list value out of the for loop results in redundent venues output
    for value in second_search:
      #fetching upcoming shows by comparing to current time    
      num_upcoming_shows=len(Show.query.filter(Show.start_time >now).all())    
      venues.append({
        "id": value.id,
        "name": value.name, 
        "num_upcoming_shows":num_upcoming_shows})
    data.append({"city": venue.city,"state": venue.state, "venues": venues })
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # same function used in search_artist,had to included the search_term definition in the funtion inorder to work 
  # from the search_venues.html we could utilize the 'count' to display the number of items found 
  search_term=request.form.get('search_term', '')
  result=Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response={'data':result,'count':len(result)}
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue= Venue.query.get(venue_id)
  now=datetime.now()
  upcoming_show_query=db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show. start_time>now).all()   
  past_show_query=db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show. start_time<now).all()
  upcoming_shows=[]
  past_shows=[]
  data=[]
  for show in upcoming_show_query:
    upcoming_shows.append({
    "artist_id":show.artist_id,
    "artist_name":show.artist.name,
    "artist_image_link":show.artist.image_link,
    "start_time":format_datetime(str(show.start_time))   
  })
  for show in past_show_query:   
    past_shows.append({
        "artist_id":show.artist_id,
        "artist_name":show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time":format_datetime(str(show.start_time))   
    }) 
  venue.genres=list(venue.genres.replace('}'," ").replace("{"," ").split(","))   
  data={
    "id":venue.id,
    "name":venue.name,
    "genres":venue.genres,                                                                   
    "address":venue.address,
    "city":venue.city,
    "state":venue.state,
    "phone":venue.phone,
    "website":venue.website_link,
    "facebook_link":venue.facebook_link,
    "seeking_talent":venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link":venue.image_link,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows),
    "upcoming_shows":upcoming_shows,
    "past_shows":past_shows
  }  
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form =VenueForm(meta={'csrf': False})
  if form.validate_on_submit():
    try:
      new_venue =Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=" ".join(form.genres.data),
        address=form.address.data,
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        seeking_description=form.seeking_description.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data)
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully added!')
    except:  
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be added.')
      db.session.rollback()
      print(form.errors)
    finally:
      db.session.close() 
  else:     
      for field, message in form.errors.items():
          flash(field + ' - ' + str(message), 'danger')
      return render_template('forms/new_venue.html', form=form)    
      
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
   try:
      Venue.query.filter_by(Venue.id==venue_id).delete()
      db.session.commit()
      flash('Selected venue deleted')
   except:
      db.session.rollback()
      flash('An error occurred. can not delete selected venue' )
   finally:
      db.session.close()
   return render_template('pages/home.html')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  #order_by parameter can be added to display artist values according to their ID or name or any other attribute
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # same function used in search_venue()
  # from the search_venues.html we could utilize the 'count' to display the number of items found 
  search_term=request.form.get('search_term', '')
  result=Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={'data':result,'count':len(result)}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist= Artist.query.get(artist_id)
  now=datetime.now()
  upcoming_show_query=db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>now).all()   
  past_show_query=db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time<now).all()
  upcoming_shows=[]
  past_shows=[]
  data=[]
  for show in upcoming_show_query:
    upcoming_shows.append({
    "venue_id":show.venue_id,
    "venue_name":show.venue.name,
    "venue_image_link":show.venue.image_link,
    "start_time":format_datetime(str(show.start_time))   
      })
  for show in past_show_query:
    past_shows.append({
            "venue_id":show.venue_id,
            "venue_name":show.venue.name,
            "venue_image_link":show.venue.image_link,
            "start_time":format_datetime(str(show.start_time))    
          }) 
  artist.genres=list(artist.genres.replace('}'," ").replace("{"," ").split(","))   #to solve the issue with genres display
  data={
    "id":artist.id,
    "name":artist.name,
    "genres":artist.genres,                                                                   
    "city":artist.city,
    "state":artist.state,
    "phone":artist.phone,
    "website":artist.website_link,
    "facebook_link":artist.facebook_link,
    "seeking_venue":artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link":artist.image_link,
    "past_shows_count":len(past_shows),
    "upcoming_shows_count":len(upcoming_shows),
    "upcoming_shows":upcoming_shows,
    "past_shows":past_shows
  }  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  ##utilized form.populate_obj(venue_id), but I noticed that I have to fetch genres separately
  artist= Artist.query.get_or_404(artist_id)
  form =ArtistForm(obj=artist)
  form.genres.data=artist.genres
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id): 
  artist= Artist.query.get_or_404(artist_id)
  form = ArtistForm(meta={'csrf': False})
  if form.validate_on_submit():
    try: 
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website_link = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        db.session.commit()
        flash('Artist' + " " + request.form['name'] + ' was successfully updated!')
    except:
        flash('An error occurred. Artist' + request.form['name'] + ' could not be edited.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()  
  else:   
      for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger')
      return render_template('forms/edit_artist.html', form=form, artist=artist)    
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  #utilize form.populate_obj(venue_id), but I noticed that I have to fetch genres separately
  venue= Venue.query.get_or_404(venue_id)
  form=VenueForm(obj=venue)
  form.genres.data=venue.genres
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue= Venue.query.get_or_404(venue_id)
  form = VenueForm(meta={'csrf': False})
  if form.validate_on_submit():
    venue.name=form.name.data
    venue.genres=form.genres.data
    venue.address=form.address.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.phone=form.phone.data
    venue.website_link=form.website_link.data
    venue.facebook_link=form.facebook_link.data
    venue.seeking_talent=form.seeking_talent.data
    venue.seeking_description=form.seeking_description.data
    venue.image_link=form.image_link.data
    try:
        db.session.commit()
        flash('Venue' + " " + request.form['name'] + ' was successfully updated!')
    except:
        flash('An error occurred. Venue' + request.form['name'] + ' could not be edited.')
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close() 
  else:
      for field, message in form.errors.items():
        flash(field + ' - ' + str(message), 'danger') 
      return render_template('forms/edit_venue.html', form=form, venue=venue)               
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form =ArtistForm(meta={'csrf': False})
  if form.validate_on_submit():
    try:
      new_artist =Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        genres=" ".join(form.genres.data),
        image_link=form.image_link.data,
        facebook_link=form.facebook_link.data,
        seeking_description=form.seeking_description.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data)
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist' + " " + request.form['name'] + ' was successfully added!')
    except:  
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be added.')
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()   
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_artist.html', form=form)    
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by(Show.start_time).all()
  data = []
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": show.start_time
    })
 
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead 
  form = ShowForm(meta={'csrf': False})
  if form.validate_on_submit():
    try:
      new_show= Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
      )
      db.session.add(new_show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
    # TODO: on unsuccessful db insert, flash an error instead.
    # included the print(sys.exc_info()), to read errors on the terminal
      db.session.rollback()
      flash('An error occurred. Show could not be listed.')
      print(sys.exc_info())
    finally:
      db.session.rollback()
  else:
    for field, message in form.errors.items():
      flash(field + ' - ' + str(message), 'danger')
    return render_template('forms/new_show.html', form=form)      
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
# Default port:
if __name__ == '__main__':
    app.run()
#db.create_all(), included initially to create the classes Venue and Artist, after that used migration to make changes accordingly
# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
