
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, flash, url_for, Response


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "fi2191"
DATABASE_PASSWRD = "4327"
DATABASE_HOST = "34.28.53.86" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://fi2191:4327@34.28.53.86/project1"

app.config['SECRET_KEY'] = 'lookasecretkey'

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)


# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
	create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	"""
	res = conn.execute(text(create_table_command))
	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
	conn.commit()


@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
@app.route('/index')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	#print(request.args)
	return render_template("index.html")



# Adds new user to the DB system
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
	if request.method == 'GET':
		return render_template("sign-up.html")
	elif request.method == 'POST':
		username = request.form.get('username')
		account_type = request.form.get('account_type')
		# a = g.conn.execute(text(f'SELECT * FROM MOVIE WHERE'))
		cursor = g.conn.execute(text(f"SELECT * FROM USERS WHERE USER_NAME = '{username}'"))
		print("cursor: ", cursor)
		users = [i for i in cursor]
		print("users: ", users)
		if len(users) != 0:
			print("username exits")
			# flash("Username already exists.")
			return render_template("signup_fail.html")
		else:
			g.conn.execute(text(f"INSERT INTO USERS(USER_NAME, ACCOUNT_TYPE) VALUES ('{username}', '{account_type}')"))
			g.conn.commit()
			flash("Account successfully created.")
			return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template("login.html")
	elif request.method == 'POST':
		username = request.form.get('username')
		account_type = request.form.get('account_type')
		cursor = g.conn.execute(text(f"SELECT * FROM USERS WHERE USER_NAME = '{username}' AND ACCOUNT_TYPE = '{account_type}'"))
		users = [i for i in cursor]
		print("users: ", users)
		if len(users) != 0:
			return redirect(url_for('index'))
		else:
			return render_template("login_fail.html")


@app.route('/movie_results', methods=['GET'])
def get_movies():
	print("Arguments: ", request.args)
	print("Genre args: ", request.args.get('genre'))
	print("Language args: ", request.args.get('language'))

	genre = request.args.get("genre")
	language = request.args.get("language")
	movie_name = request.args.get("movie_name")


	if(genre != "" and language != ""  and movie_name != "" ):
		print("genre: ", genre, "language: ", language, "movie_name: ", movie_name)
		cursor = g.conn.execute(text(f"SELECT * FROM MOVIE where LANGUAGE = '{language}' AND GENRE = '{genre}' AND MOVIE_NAME = '{movie_name}'"))
	elif(genre != "" and language != ""):
		print("genre: ", genre, "language: ", language)
		cursor = g.conn.execute(text(f"SELECT * FROM MOVIE where LANGUAGE = '{language}' AND GENRE = '{genre}'"))
	elif(genre != ""):
		print("genre: ", genre)
		cursor = g.conn.execute(text(f"SELECT * FROM MOVIE where GENRE = '{genre}'"))
	elif(language != ""):
		print("language: ", language)
		cursor = g.conn.execute(text(f"SELECT * FROM MOVIE where LANGUAGE = '{language}'"))
	elif(movie_name != ""):
		print("movie_name: ", movie_name)
		cursor = g.conn.execute(text(f"SELECT * FROM MOVIE where MOVIE_NAME = '{movie_name}'"))
	else:
		print("all")
		cursor = g.conn.execute(text("SELECT * FROM MOVIE"))

	movies = []
	for movie_name in cursor:
		movies.append(movie_name)
	print(movies)
	context = dict(data = movies)
	return render_template("moviesearch_results.html", **context)



@app.route('/movies', methods=['GET'])
def movies_homepage():
	return render_template("movies.html")

@app.route('/songs', methods=['GET'])
def songs_homepage():
	return render_template("songs.html")

@app.route('/song_results', methods=['GET'])
def get_songs():
	song_name = request.args.get("song_name")
	language = request.args.get("language")
	singer = request.args.get("singer")

	if(song_name != ""):
		cursor = g.conn.execute(text(f"select s.song_name, m.MOVIE_NAME, s.SONG_LANGUAGE  from movie as m join (select * from songs where song_name = '{song_name}') as s on m.movie_id = s.movie_id"))
	elif (singer != ""):
		cursor = g.conn.execute(text(f"select s.song_name, m.MOVIE_NAME, s.SONG_LANGUAGE  from movie as m join (select * from SONGS where SONG_ID in (select SONG_ID from SUNG_BY where singer_id in (select SINGER_ID from SINGER where singer_name = '{singer}'))) as s on s.movie_id = m.movie_id"))
	elif (language != ""):
		cursor = g.conn.execute(text(f"select s.song_name, m.MOVIE_NAME, s.SONG_LANGUAGE  from movie as m join (select * from songs where song_language = '{language}') as s on m.movie_id = s.movie_id"))
	else:
		cursor = g.conn.execute(text("SELECT * FROM SONGS"))

	songs = []
	for row in cursor:
		songs.append(row)
	print("Songs: ", songs)
	context = dict(data = songs)
	return render_template("songsearch_results.html", **context)		

@app.route('/trending', methods=['GET'])
def get_trending_movies():
	cursor = g.conn.execute(text("SELECT m.MOVIE_NAME, p.purchases FROM MOVIE as m JOIN (select movie_id, count(*) as purchases from RATES group by movie_id order by purchases desc) as p on p.movie_id = m.movie_id order by p.purchases desc"))

	trending_movies = []
	for row in cursor:
		trending_movies.append(row)
	print("Trending movies: ", trending_movies)
	context = dict(data = trending_movies)
	return render_template("trending.html", **context)	


@app.route('/highlyrated', methods=['GET'])
def get_highlyrated():
	cursor = g.conn.execute(text("select m.MOVIE_NAME, avg(r.RATINGS) as avg_rating from MOVIE as m join REVIEW_RATINGS as r on m.movie_id = r.movie_id group by m.movie_id order by avg_rating desc"))

	highlyrated_movies = []
	for row in cursor:
		highlyrated_movies.append(row)
	print("High rated movies: ", highlyrated_movies)
	context = dict(data = highlyrated_movies)
	return render_template("highlyrated.html", **context) 

@app.route('/movieinfo_results', methods=['GET'])
def get_movieinfo():
	moviename = request.args.get("movie_name")

	cursor = g.conn.execute(text(f"select ACTOR_NAME from ACTOR where ACTOR_ID in (select r.ACTOR_ID from (select * from MOVIE where MOVIE_NAME = '{moviename}') as m JOIN ROLE_PLAYED as r on m.movie_id = r.movie_id)"))
	actors = [i for i in cursor]
	print("Actors: ", actors)

	cursor = g.conn.execute(text(f"select mm.avg_rating from (select m.MOVIE_NAME, avg(r.RATINGS) as avg_rating from MOVIE as m join REVIEW_RATINGS as r on m.movie_id = r.movie_id group by m.movie_id order by avg_rating desc) as mm where mm.MOVIE_NAME = '{moviename}' "))
	rating = [i for i in cursor]
	print("Rating: ", rating)

	cursor = g.conn.execute(text(f"select movie_name, language, director, genre from MOVIE where MOVIE_NAME = '{moviename}'"))
	movie_info = []
	for row in cursor:
		movie_info.append(row)

	context = dict(actors = actors, rate = rating, movie_info = movie_info)
	print(context)
	return render_template("movieinfo_results.html", **context) 


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
