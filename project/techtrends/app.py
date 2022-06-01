from mimetypes import MimeTypes
from multiprocessing import connection
import sqlite3
from connection_count import *

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, Response
from werkzeug.exceptions import abort


# Global list containing all active connections
GLOBAL_DB_CONNECTIONS = []
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    GLOBAL_DB_CONNECTIONS.append(connection)
    connection.row_factory = sqlite3.Row
    return connection

# Wrapper above closing connection to modify the global list
def close_connection(connection):
    connection.close()
    GLOBAL_DB_CONNECTIONS.remove(connection)
    return

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    close_connection(connection)
    return post

# Function to get amounts of rows in DB
def get_post_count():
    connection = get_db_connection()
    count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    close_connection(connection)
    return count

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'
# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    close_connection(connection)
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      return render_template('404.html'), 404
    else:
      return render_template('post.html', post=post)

# Health checks route
@app.route('/healthz')
def health_check():
    return "{'result': 'OK - Healthy'}", 200

# Route for metrics
@app.route('/metrics')
def metrics():
    post_count = get_post_count()
    json_dict = {'db_connections': len(GLOBAL_DB_CONNECTIONS),'post_count': post_count}
    return str(json_dict), 200

# Define the About Us page
@app.route('/about')
def about():
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            close_connection(connection)

            return redirect(url_for('index'))

    return render_template('create.html')

# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
