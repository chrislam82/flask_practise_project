# auth.py

import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# url_for() and ENDPOINTS:
# 	Generates a URL to a view based on name and arguments
# 		--> Default is same as view function
# 		--> e.g. url_for('register', who='user') to generate url to the view register if it was standalone with the arg of user
# 		--> However, since we are using blueprints, the name of the blueprint is prepended. Here it is 'auth', so to generate a URL to the register view, we use 'auth.register'
# 	Endpoint: endpoint is the name associated with a view
# 		--> So standalone would be 'register' whereas the one we have would be 'auth.register'

# Creates a blueprint called "auth".
# 	It needs to know where it is defined so __name__ is passed in
# 	and all URL's associated with auth will be prepended with '/auth'
bp = Blueprint('auth', __name__, url_prefix='/auth')


# Function that runs before any view functions regardless of URL
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id') 														# Checks if user_id is stored in session

    if user_id is None:
        g.user = None
    else: 																					# If so, fetch data for that user and store in g.user (which lasts for the whole request)
        g.user = get_db().execute( 															
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# View: /register
# 		Returns a HTML form for registering username and password.
# 		After being submitted, it will either return an error message or redirect to auth.login
# Curious... How is request being passed in to the register() fn. Where is it accessing it from. Notice request imported from flask module above
@bp.route('/register', methods=('GET', 'POST')) 											# so when /auth/register called, it calls register() and returns a response
def register():
    if request.method == 'POST': 															# Obvs. POSTso submitting form. Check if valid, if so, redirect to login, else error msg
        username = request.form['username'] 												# request.form works like a dict, mapping username and password from submitted request
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute( 																	# Obv. Run select on db to check that username does not exist yet. Else, error = msg
            'SELECT id FROM user WHERE username = ?', (username,) 							# 	db.execute uses ? as placeholder for user input and tuple to input into ?. Takes care of escaped values to prevent SQL injection attack
        ).fetchone() is not None: 															# 	.fetchone fetches one row of result and returns None if empty
            error = 'User {} is already registered.'.format(username)

        if error is None: 																	# Clearly same as above. Using placeholder ? combined with hash of password and inserting into db
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit() 																	# db.commit() needs to be called to save the changes (if data modified)
            return redirect(url_for('auth.login')) 											# 	url_for() allows us to generate a URL without having to change all of it.

        flash(error) 																		# Else flash(error) and reload to /auth/register.html
 																							# 	flash() stores the error to be rendered in html later (Makes more sense than flashing during response)
    return render_template('auth/register.html') 											# render_template() simply renders a template containing the HTML


# View for login:
# 	Clearly a lot is similar
# 
# Session: used to store data across requests
# 		--> Stored as a cookie on user browser
# 		--> Sent along with new requests once signed in
# 		--> Available with each new request to other views for use
# 		--> Secured with SECRET_KEY from __init__.py app factory so make sure that it is secure (else a user could modify a session)
# 		--> 		SECRET_KEY must be set in __init__.py to enable
# 		https://flask.palletsprojects.com/en/1.1.x/api/#flask.session
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute( 																	# Difference here being to query first and the use of session below
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear() 																# session is a dict that stores data accross requests
            session['user_id'] = user['id'] 												# 		So we store id in a new session (hence session.clear() ) and this data is stored in a cookie that is sent to the browser
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# Logout:
# 		logout by clearing session so that user_id is no longer stored
# 		and load_logged_in_user() will not retrieve data for subsequent requests until logged back in
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# Use a decorator to check if user is logged on before allowing a user to create/edit/detele blog posts
# 		returns a new view wrapped around the original view
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login')) 											# Redirect to login if not logged in

        return view(**kwargs)

    return wrapped_view 																	# Else continue to view as normal


