from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
import sqlite3
from markupsafe import escape

from datetime import datetime, timedelta

exercises_dict = {
    'Bench Press': 'Chest',
    'Incline Bench Press': 'Chest',
    'Chest Fly': 'Chest',
    'Squat': 'Legs',
    'Lunge': 'Legs',
    'Leg Press': 'Legs',
    'Pull-Up': 'Back',
    'Deadlift': 'Back',
    'Barbell Row': 'Back',
    'Shoulder Press': 'Shoulders',
    'Lateral Raise': 'Shoulders',
    'Arnold Press': 'Shoulders',
    'Bicep Curl': 'Arms',
    'Tricep Extension': 'Arms',
    'Hammer Curl': 'Arms'
}  # make createworkout.html pull from here

app = Flask(__name__)
#permanent = True
#session.permanent_session_lifetime = timedelta(hours = 24)


with sqlite3.connect('login.db') as db:
    db.execute("PRAGMA foreign_keys = ON")


@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html')
    return redirect(url_for('login'))


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/add', methods=['POST'])  # updated add for new database schema
def add():
    if request.form['password'] != request.form['psw-repeat']:
        flash("Passwords ")
        return redirect(url_for('login'))  #
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        try:
            cursor.execute("""
                INSERT INTO User (Name, Email, Password, Height, Weight, Age, Sex)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form['username'],
                request.form['email'],
                request.form['password'],  # we shoud encrypt
                request.form.get('height', None),
                request.form.get('weight', None),
                request.form.get('age', None),
                request.form.get('sex', None),

            ))
            db.commit()
            flash(f"User '{request.form['username']}' added successfully!")
            return redirect(url_for('home'))
        except Exception as e:  # let them kno its taken

            flash("An error occurred.")
            return redirect(url_for('login'))


@app.route('/verify', methods=['POST'])
def verify():
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM User WHERE Name=? AND Password=?",
                       (request.form['username'], request.form['password']))
        result = cursor.fetchall()
        if len(result) == 0:
            return 'Username or password not recognized.'
        else:
            session.permanent = True
            session['username'] = request.form['username']
            #get email also unless we force usernames to be unique
            return redirect(url_for('home'))


@app.route('/un')
def un():
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in.'


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/create_workout')
def createworkout():
    if 'username' not in session:  # ion my testing just becuase theres a username in session inst very good security, change
        return redirect(url_for('login'))
    return render_template('create_workout.html')


@app.route('/my_workouts')
def myworkouts():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('my_workouts.html')


@app.route('/weight-log')
def weight_log():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('weight_log.html')


@app.route('/muscleusage', methods=['POST'])
def muscleusage():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']

    conn = sqlite3.connect('login.db')
    cursor = conn.cursor()

    cursor.execute("SELECT User_ID FROM User WHERE Name = ?", (username,))
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]

    cursor.execute("SELECT * FROM User_Body WHERE User_ID = ?", (user_id,))
    user_body = cursor.fetchone()

    if not user_body:
        cursor.execute("""
            INSERT OR IGNORE INTO User_Body (User_ID, Shoulders_Percent, Back_Percent, Arms_Percent, Legs_Percent, Chest_Percent, Last_Reset)
            VALUES (?, 0, 0, 0, 0, 0, DATE('now'))
        """, (user_id,))
        conn.commit()

    cursor.execute("""
        SELECT Shoulders_Percent, Back_Percent, Arms_Percent, Legs_Percent, Chest_Percent 
        FROM User_Body WHERE User_ID = ?
    """, (user_id,))
    data = cursor.fetchone()

    conn.close()

    if not data:
        return jsonify({"shoulders": 0, "back": 0, "arms": 0, "legs": 0, "chest": 0})

    return jsonify({
        "shoulders": data[0],
        "back": data[1],
        "arms": data[2],
        "legs": data[3],
        "chest": data[4]
    })


## api section, mabe seperate file .
@app.route('/create-workout/submit', methods=['POST'])
def create_workout_submit():
    if 'username' not in session:
        return redirect(url_for('login'))
    print("session useranem:" + session['username'])

    username = session['username']
    with sqlite3.connect(
            'login.db') as db:  # we need to connect with foregn keeys enabled always, FIXES BUG WHERE STUFF DOESNT AUTOINCREMENT
        cursor = db.cursor()
        cursor.execute("SELECT User_ID FROM User WHERE Name = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return "User not found", 404

        user_id = user[0]

        cursor.execute("""
            INSERT INTO Workouts (User_ID, Date, Field) VALUES (?, DATE('now'), 'General')
        """, (user_id,))
        workout_id = cursor.lastrowid
        exercises = zip(
            request.form.getlist('name[]'),
            request.form.getlist('sets[]'),
            request.form.getlist('reps[]'),
            request.form.getlist('weight[]')
        )

        for name, sets, reps, weight in exercises:
            cursor.execute("""
                INSERT INTO Exercise (Workout_ID, Exercise_Name, No_Sets, No_Reps_Per_Set, Weight)
                VALUES (?, ?, ?, ?, ?) 
            """, (workout_id, name, sets, reps, weight))  #question mark is %s

            # now udate user percents

            cursor.execute("SELECT * FROM User_Body WHERE User_ID = ?", (user_id,))
            user_body = cursor.fetchone()
            muscleused = exercises_dict[name]
            print(muscleused)

            amnttoadd = (int(sets) / 12) * 100
            cursor.execute(f"""
            UPDATE User_Body SET {muscleused}_Percent = {muscleused}_Percent + ?
            where User_ID = ?
            """, (amnttoadd, user_id))

        db.commit()

    return redirect(url_for('myworkouts'))


@app.route('/workout/<workout_id>')
def workout_detail(workout_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT User_ID FROM User WHERE Name = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return "User not found", 404
        user_id = user[0]

        cursor.execute("""
            SELECT 
                Exercise.Exercise_Name,
                Exercise.No_Sets,
                Exercise.No_Reps_Per_Set,
                Exercise.Weight
            FROM Workouts
            JOIN Exercise ON Workouts.Workout_ID = Exercise.Workout_ID
            WHERE Workouts.Workout_ID = ? AND Workouts.User_ID = ?
        """, (workout_id, user_id))
        exercises = cursor.fetchall()

    return render_template('workoutindividual.html', workout_id=workout_id, exercises=exercises)


@app.route('/api/get-workouts', methods=['GET'])
def get_workouts_api():
    if 'username' not in session:
        return {"message": "Unauthorized"}, 401

    username = session['username']

    with sqlite3.connect('login.db') as db:

        cursor = db.cursor()

        cursor.execute("SELECT User_ID FROM User WHERE Name = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return {"message": "User not found"}, 404
        user_id = user[0]

        cursor.execute("""
            SELECT 
                Workouts.Workout_ID,
                Workouts.Date, 
                Exercise.Exercise_Name, 
                Exercise.No_Sets, 
                Exercise.No_Reps_Per_Set, 
                Exercise.Weight
            FROM Workouts
            JOIN Exercise ON Workouts.Workout_ID = Exercise.Workout_ID
            WHERE Workouts.User_ID = ?
            ORDER BY Workouts.Date DESC
        """, (user_id,))
        workouts = cursor.fetchall()
    formatworkouts = [
        {
            "workout_id": row[0],
            "date": row[1],
            "exercise": row[2],
            "sets": row[3],
            "reps": row[4],
            "weight": row[5]
        }
        for row in workouts
    ]

    return {"workouts": formatworkouts}, 200


@app.route('/api/get-weight-log', methods=['GET'])
def get_weight_log():
    if 'username' not in session:
        return 401

    username = session['username']  # needs work when we imlement better security / hashing

    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()
        cursor.execute("SELECT User_ID FROM User WHERE Name = ?", (username,))
        user = cursor.fetchone()  # to get the first row, but since user is unique it doesn't matter, but kinda safer
        if not user:
            return 404
        print(user)  # debuig
        user_id = user[0]

        cursor.execute("SELECT Date, Weight FROM WeightLog WHERE User_ID = ? ORDER BY Date ASC", (user_id,))
        weight_data = cursor.fetchall()

    formatted_data = [{"date": row[0], "weight": row[1]} for row in weight_data]
    print(formatted_data)
    return {"weight_log": formatted_data}, 200


# format to render with html.

@app.route('/api/add-weight', methods=['POST'])
def add_weight():
    if 'username' not in session:
        return {"message": "unauthorized"}, 401

    username = session['username']
    weight = request.get_json().get('weight')

    try:
        weight = float(weight)  # check number put in try becuase cuasaing errors
    except ValueError:
        return {"message": "didnt enter"}, 400

    with sqlite3.connect('login.db') as db:
        cursor = db.cursor()

        cursor.execute("SELECT User_ID FROM User WHERE Name = ?", (username,))
        user = cursor.fetchone()
        if not user:
            return {"message": "user not found"}, 404

        user_id = user[0]

        cursor.execute("INSERT INTO WeightLog (User_ID, Weight, Date) VALUES (?, ?, DATE('now'))", (user_id, weight))
        db.commit()

    return {"message": " successful"}, 201


app.secret_key = 'the random string'
app.run(port=5021, debug=True)
