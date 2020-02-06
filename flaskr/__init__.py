# __init__.py

import os

from flask import Flask

# Application factory:
# 		
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True) 								# Creat Flask instance (with name of Python module, and relative path of config files)
    app.config.from_mapping(															# Some configurations to be used
        SECRET_KEY='dev', 																# 		Key for dev. Obviously not safe
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'), 						# 		SQLite database path
    )

    if test_config is None:																# Overrides config with config from config.py if passed in.
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True) 								# If test_config passed in, then use instead (for testing purposes)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists													# Make sure that instance folder exists because it will be used for SQLite db
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello 													# @ app.route
    @app.route('/hello')																# 		route just so we can see it working
    def hello():																		# 		Creates connection between /hello and the function hello() (So we can display hello world)
        return 'Hello, World!'

    from . import db 																	# Import init_app() function from db.py and call with app as arg
    db.init_app(app)

    from . import auth 																	# Like above, import and register blueprint "auth" with app factory fn
    app.register_blueprint(auth.bp)

    return app