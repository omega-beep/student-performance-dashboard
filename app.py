from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3


app = Flask(__name__)
app.secret_key = "supersecretkey_v2"


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()

    name = data['name']
    marks = int(data['marks'])
    attendance = int(data['attendance'])

    # Grade logic
    if marks >= 85:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 40:
        grade = "C"
    else:
        grade = "Fail"

    status = "Pass" if marks >= 40 else "Fail"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, marks, attendance, status, grade) VALUES (?, ?, ?, ?, ?)",
        (name, marks, attendance, status, grade)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "Student added successfully"})




@app.route('/students')
def students():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])
@app.route('/delete_student/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Student deleted"})
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        try:
            conn = sqlite3.connect('database.db')
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return render_template('signup.html', error="Username already exists")

    return render_template('signup.html')

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current = request.form['current_password']
        new = request.form['new_password']

        conn = sqlite3.connect('database.db')
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (session['user'],)
        ).fetchone()

        if user and check_password_hash(user[2], current):
            new_hash = generate_password_hash(new)
            conn.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_hash, session['user'])
            )
            conn.commit()
            conn.close()
            return redirect(url_for('home'))
        else:
            conn.close()
            return render_template('change_password.html', error="Wrong current password")

    return render_template('change_password.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000)
