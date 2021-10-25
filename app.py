import uuid
from flask import Flask, request, jsonify, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from faker import Faker

app = Flask(__name__)

app.config['SECRET_KEY'] = 'SomeRandomSecretKey'
# database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# creates SQLALCHEMY object
db = SQLAlchemy(app)


# Database ORMs
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(140))
    photo_url = db.Column(db.String(150))


class WatchList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))


class SeenList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    seen = db.Column(db.Integer)


# db.create_all()
#
#
# def dummy_data():
#     fake = Faker()
#     for i in range(10):
#         name = fake.name()
#         url = fake.url()
#         movie = Movie(name=name, photo_url=url)
#         db.session.add(movie)
#         db.session.commit()
#
#         public_id = str(uuid.uuid4())
#         name = fake.name()
#         email = fake.email()
#         password = '1234'
#
#         user = User(public_id=public_id,
#                     name=name, email=email,
#                     password=generate_password_hash(password))
#         db.session.add(user)
#         db.session.commit()


@app.route("/")
def home():
    return "This is a API server , access the routes"


# 1. Authenticating the user using email and password.
@app.route('/user/login', methods=['POST'])
def user_login():
    # creates dictionary of form data
    auth = request.get_json()

    if not auth or not auth['email'] or not auth['password']:
        # returns 401 if any email or / and password is missing
        return make_response('BAD_REQUEST', 400)

    user = User.query.filter_by(email=auth['email']).first()

    if not user:
        # returns 401 if user does not exist
        return make_response('AUTHENTICATION_ERROR', 401)

    if check_password_hash(user.password, auth['password']):
        user_id = user.id
        return make_response(jsonify({'id': user_id}), 200)
    # returns 403 if password is wrong
    return make_response('AUTHENTICATION_ERROR', 401)


# 2. Searching for a movie from a database
@app.route('/user/<movie_name>', methods=['GET'])
def get_movie(movie_name):
    if movie_name:
        return_values = []
        movies = Movie.query.filter_by(name=movie_name).all()
        for movie in movies:
            movie_dict = {'name': movie.name,
                          'profile_pic': movie.photo_url,
                          'id': movie.id}

            return_values.append(movie_dict)

        return make_response(jsonify({'movies': return_values}), 200)


# 3. Add movie to user watchlist.
@app.route('/user/watchlist/<int:user_id>/<int:movie_id>', methods=['POST'])
def add_watchlist(user_id, movie_id):
    if user_id and movie_id:
        watchlist = WatchList(user_id=user_id, movie_id=movie_id)
        db.session.add(watchlist)
        db.session.commit()
        return make_response("Added Movie", 200)


# 4. Marking the movie which is already added to the user watchlist as seen.
@app.route('/user/marking/<int:user_id>/<int:movie_id>', methods=['POST'])
def mark_movie(user_id, movie_id):
    if user_id and movie_id:
        seenlist = SeenList(user_id=user_id, movie_id=movie_id, seen=1)
        db.session.add(seenlist)
        db.session.commit()
        return make_response("Marked", 200)


# 5. Delete movie from user watchlist.
@app.route('/user/<int:user_id>/<int:movie_id>', methods=['DELETE'])
def delete_user_watchlist(user_id, movie_id):
    if user_id and movie_id:
        user_watchlist = WatchList.query.filter(User.id.like(user_id), Movie.id.like(movie_id)).first()
        db.session.delete(user_watchlist)
        db.session.commit()
        return make_response("Deleted", 200)


# 6. Viewing the user watchlist
@app.route('/user/<int:user_id>/watchlist', methods=['GET'])
def get_watchlist(user_id):
    return_values = []
    watchlists = WatchList.query.filter_by(user_id=user_id).all()
    for watchlist in watchlists:
        movie = Movie.query.filter_by(id=watchlist.movie_id).first()
        movie_dict = {'name': movie.name,
                      'profile_pic': movie.photo_url,
                      'movie_id': movie.id}

        return_values.append(movie_dict)
        return make_response(jsonify({'watchlists': return_values}), 200)


if __name__ == '__main__':
    # dummy_data()
    app.run(debug=True, host='0.0.0.0', port=5000)
