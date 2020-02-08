

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute( 															# ORDER BY desc so most recent blog posts first and matching user.id to post.user_id
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)


# Works just like register in auth execept inserting a post into POST table in db
@bp.route('/create', methods=('GET', 'POST'))
@login_required																		# login_required wrapper in auth.py is used to check if user is logged in before allowing someone to create a post
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))   									# At the end, redirect to blog.index

    return render_template('blog/create.html')


# Function used by both update/delete posts 
# 		Self explanatory check if post with post.id id exists
# 		if check_author, then check if post auther = user, else they are trying to edit/delete something which isnt theirs
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))  		# 404 Not Found

    if check_author and post['author_id'] != g.user['id']:			# 403 Forbidden
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST')) 				# Make sure input is an int (int:id) (Else, it would be treated as a string) where id is post id
@login_required
def update(id): 													# Hence we pass id as int as arg into update()
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


# Part of update.html
# 		Only POST since no associated html template (just a button)
# 			Prety simple, check that user is logged in and that post belongs to user
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index')) 							# And redirect to index once deleted





