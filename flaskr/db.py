# db.py
#   Store users and posts on blog
# 


import sqlite3												# Using python3 sqlite3 module (built into python with downside of slowing down for large apps due to sequential processing for concurrent requests)

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
	if 'db' not in g:										# g is special object for each request used to store data that might be used by a function. can be reused instead of recreating a new connection if get_db() called again
		g.db = sqlite3.connect( 							# Points to db pointed to by Flask App (From __init__.py)
			current_app.config['DATABASE'], 				# current_app is object that points to Flask app when handling requests
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row 						# Treat rows like dicts (so we can access columns by name)

	return g.db


def close_db(e=None): 										# Checks if connection has been created by checking if db in g and closes it if so
	db = g.pop('db', None)

	if db is not None:
		db.close()


def init_db():
    db = get_db() 											# Get db connection which is used to execute commands

    with current_app.open_resource('schema.sql') as f:   	# open_resource (relative to flaskr package)
        db.executescript(f.read().decode('utf8'))

# Need to register close_db() and init_db_command() with app instance. Since it is app factory, instance is unavailable
def init_app(app): 											# Instead, init_app takes the app as arg and registers for it
    app.teardown_appcontext(close_db) 						# teardown_appcontext() tells Flask to call close_db when cleaning up after returning a response
    app.cli.add_command(init_db_command) 					# app.cli.add_command() adds a command that can be called with "flask" command


@click.command('init-db') 									# Defines command line command (init-db) which calls init_db() and shows a message to indicate success
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db() 												# 		which calls init_db()
    click.echo('Initialized the database.') 				# 		And shows a message to indicate success

    