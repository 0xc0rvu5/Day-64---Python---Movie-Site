import os
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, validators
from wtforms.validators import DataRequired
from tmdbv3api import TMDb
from tmdbv3api import Movie as MovieAPI


#initialize global variables
SECRET_KEY = os.urandom(32)
APP = Flask(__name__, template_folder='templates', static_folder='static')
APP.config['SECRET_KEY'] = SECRET_KEY
APP.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
TMDB_API_KEY = os.getenv('MOVIESDB_V3')
TMDB = TMDb()
TMDB.api_key = TMDB_API_KEY
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


#initiate bootstrap functionality
Bootstrap(APP)


#initiate sqlalchemy database functionality
db = SQLAlchemy(APP)


with APP.app_context():
    class Movie(db.Model):
        '''Generate a movie database.'''
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        title = db.Column(db.String(250), unique=True, nullable=False)
        year = db.Column(db.Integer, unique=True)
        description = db.Column(db.String(250), nullable=False)
        rating = db.Column(db.Float)
        ranking = db.Column(db.Integer)
        review = db.Column(db.String(250))
        url = db.Column(db.String(250), nullable=False)


        # Optional: this will allow each book object to be identified by its title when printed.
        def __repr__(self):
            return f'<Book {self.title}>'
    
    # create database
    # db.create_all()

    # # create column
    # new_movie = Movie(
    # title="Phone Booth",
    # year=2002,
    # description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
    # rating=7,
    # ranking=10,
    # review="My favourite character was the caller.",
    # url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
    # )
    # db.session.add(new_movie)
    # db.session.commit()


class MovieUpdate(FlaskForm):
    '''Genreate a movie update form.'''
    new_rating = FloatField('New Rating', validators=[DataRequired(), validators.NumberRange(min=0, max=10)])
    new_review = StringField('New Review', validators=[DataRequired()])
    submit = SubmitField('Update')

class MovieAdd(FlaskForm):
    '''Genreate a movie creation form.'''
    add_movie = StringField('Add Movie', validators=[DataRequired()])
    submit = SubmitField('Submit')



@APP.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()

    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i

    return render_template("index.html", movies=all_movies)

@APP.route('/add', methods=['GET', 'POST'])
def add():
    form = MovieAdd()
    movie = MovieAPI()

    if form.validate_on_submit:
        movie_title = form.add_movie.data

        if movie_title:
            search = movie.search(str(movie_title))
            #get all titles for searched movies 
            titles = [movies.title for movies in search]
            #get all ids for searched movies
            ids = [movies.id for movies in search]
            #get all release dates for searched movies
            release_dates = [movie.details(movies.id).release_date for movies in search]
            #copy all non-duplicate movie titles and release_dates into a prettified display
            final = []
            for title, release_date in zip(titles, release_dates):
                if title and release_date:
                    final.append(f'{title} - {release_date}')
            return render_template('select.html', final=final, ids=ids, zip=zip)

    return render_template('add.html', form=form)


@APP.route('/find')
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie = MovieAPI()
        m = movie.details(movie_api_id)
        new_movie = Movie(
            title=m.title,
            year=m.release_date.split('-')[0],
            description=m.overview,
            rating=m.vote_average,
            url=f'{MOVIE_DB_IMAGE_URL}{m.poster_path}',
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))


@APP.route('/edit', methods=['GET', 'POST'])
def edit():
    form = MovieUpdate()
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)

    if request.method == 'GET':
        form.new_rating.data = movie_selected.rating
        form.new_review.data = movie_selected.review

    if form.validate_on_submit():
        movie_selected.rating = form.new_rating.data
        movie_selected.review = form.new_review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('edit.html', form=form, movie=movie_selected)

@APP.route('/delete', methods=['GET', 'POST'])
def delete():
    movie_id = request.args.get('id')
    #delete record by id
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    APP.run(debug=True)