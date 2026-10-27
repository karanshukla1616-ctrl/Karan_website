from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "karan_savewater_super_secret_key_2010"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Admin Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Custom Videos / Topics Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS custom_videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic_key TEXT NOT NULL,
            title TEXT NOT NULL,
            video_url TEXT NOT NULL
        )
    ''')
    
    # Public Community Board Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS public_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            text TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    
    # Exam Registrations Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exam_registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score TEXT NOT NULL
        )
    ''')
    
    # Default Password '2010'
    cursor.execute('SELECT COUNT(*) FROM admin')
    if cursor.fetchone()[0] == 0:
        default_pass = generate_password_hash('2010')
        cursor.execute('INSERT INTO admin (password_hash) VALUES (?)', (default_pass,))
        
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM custom_videos ORDER BY id DESC')
    videos = cursor.fetchall()
    
    cursor.execute('SELECT * FROM public_posts ORDER BY id DESC')
    posts = cursor.fetchall()
    conn.close()
    
    is_owner = session.get('owner_logged_in', False)
    return render_template('index.html', videos=videos, posts=posts, is_owner=is_owner)

@app.route('/login', methods=['POST'])
def login():
    pin = request.form.get('pin')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password_hash FROM admin WHERE id=1')
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password_hash(row[0], pin):
        session['owner_logged_in'] = True
        flash('Owner Mode Activated Successfully!', 'success')
    else:
        flash('Incorrect PIN!', 'error')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('owner_logged_in', None)
    return redirect(url_for('index'))

@app.route('/add_video', methods=['POST'])
def add_video():
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
        
    topic_key = request.form.get('topic_key')
    title = request.form.get('title')
    video_url = request.form.get('video_url')
    
    if topic_key and title and video_url:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO custom_videos (topic_key, title, video_url) VALUES (?, ?, ?)',
                       (topic_key, title, video_url))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete_video/<int:id>')
def delete_video(id):
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM custom_videos WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/add_post', methods=['POST'])
def add_post():
    author = request.form.get('author') or "अनाम नागरिक"
    text = request.form.get('text')
    
    if text:
        import datetime
        time_str = datetime.datetime.now().strftime('%H:%M')
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO public_posts (author, text, time) VALUES (?, ?, ?)',
                       (author, text, time_str))
        conn.commit()
        conn.close()
    return redirect(url_for('index'))

@app.route('/delete_post/<int:id>')
def delete_post(id):
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM public_posts WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
    @app.route('/edit_video/<int:id>', methods=['POST'])
def edit_video(id):
    if not session.get('owner_logged_in'):
        return redirect(url_for('index'))
    
    new_title = request.form.get('title')
    new_url = request.form.get('video_url')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE custom_videos SET title=?, video_url=? WHERE id=?', (new_title, new_url, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
    
