from flask import Flask, render_template, request, redirect, url_for, flash,session,jsonify,send_from_directory
from flask_mysqldb import MySQL
import os
import subprocess
import cv2
import threading
import time

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

app = Flask(__name__,static_folder='static', template_folder='templates')
app.secret_key = 'your_secret_key'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysql@1234'
app.config['MYSQL_DB'] = 'edu_bot'

mysql = MySQL(app)

questions_list = [
    {"name": "1. Advance sub array problem", "description": "Find the maximum possible score by choosing a contiguous subarray of size K from an array, where each element is multiplied by its position. Input: N (number of shots), K (size of subarray), array A (distances). Example: 5, 2, [1, 2, 3, 4, 5] → Output: 14."},
    {"name": "2. Ant on Rail", "description": "Determine how many times an ant returns to its starting position after moving right or left based on an array of 1s and -1s. Input: N (number of moves), array A (ant's moves). Example: 5, [1, -1, 1, -1, 1] → Output: 2."},
    {"name": "3. Chocolate Jar", "description": "Calculate the total number of chocolates student A will have after picking chocolates from jars in a repeated order among three students. Input: array (chocolates in jars), N (number of jars). Example: [10, 20, 30], 3 → Output: 21. "},
    {"name": "4. Diwali Contest", "description": "Determine how many problems Max can solve before reaching the party venue, considering travel time and problem-solving time. Input: N (number of problems), P (travel time in minutes). Example: 6, 180 → Output: 4. "},
    {"name": "5. Dog Age", "description": "Calculate a dog's age in human years, given that 1 dog year equals 7 human years. Input: N (dog's age in years). Example: 4 → Output: 28."},
    {"name": "6. Elections", "description": "Find the winning party's number based on the majority of votes in an array, or return -1 if no majority exists. Input: N (number of voters), array A (votes). Example: 6, [1, 1, 2, 2, 2, 3] → Output: 2."},
    {"name": "7. Space Counter", "description": "Count the number of spaces in a given string. Input: string S. Example: hello world hey → Output: 2."},
    {"name": "8. Minimum Array sum", "description": "Perform operations on an array to find the minimum possible sum by updating elements based on their average. Input: N (size of array), array A. Example: 5, [1, 2, 3, 4, 5] → Output: 5."},
    {"name": "9. Math test", "description": "Find the smallest prime number larger than a given integer N. Input: N. Example: 6 → Output: 7."},
    {"name": "10. Magic String", "description": "Determine the minimum steps required to make all characters in a string the same by replacing any letter with another letter in the string. Input: string S. Example: aaabbbccdddd → Output: 8."}
]


@app.route('/')
def home():
    return render_template('index.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Query the database for the user
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()  # Fetch one row

        if user:
            stored_password = user[2]  # Assuming password column is at index 2, adjust as per your database schema
            if password == stored_password:
                # If username and password match, create a session
                session['username'] = username
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect password.', 'danger')
        else:
            flash('User not found.', 'danger')

        cur.close()

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        # Store username and password in the database
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, password))
        mysql.connection.commit()
        cur.close()

        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Learn Python route
def track_face():
    global focus_start_time, total_focus_time, tracking_active
    cap = cv2.VideoCapture(0)

    while tracking_active:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) > 0:
            if focus_start_time == 0:
                focus_start_time = time.time()
        else:
            if focus_start_time != 0:
                total_focus_time += time.time() - focus_start_time
                focus_start_time = 0

        # Display the video feed
        cv2.imshow('Focus Tracker', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

@app.route('/learn_python.html')
def learn_python_page():
    global tracking_active, total_focus_time

    if 'username' in session:
        # Check user ID
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM users WHERE username=%s', (username,))
        user_id = cur.fetchone()[0]
        cur.close()

        # Activate face tracking
        tracking_active = True
        tracking_thread = threading.Thread(target=track_face)
        tracking_thread.start()

        # Wait until the user finishes learning
        flash("Face tracking active. Learning time is being tracked.", "info")
        return render_template('learn_python.html', face_tracking=True)

    else:
        # No tracking for unauthenticated users
        flash("You are not logged in. Face tracking disabled.", "warning")
        return render_template('learn_python.html', face_tracking=False)

@app.route('/end_tracking', methods=['POST'])
def end_tracking():
    global tracking_active, total_focus_time
    if 'username' in session:
        username = session['username']
        cur = mysql.connection.cursor()
        cur.execute('SELECT id FROM users WHERE username=%s', (username,))
        user_id = cur.fetchone()[0]

        # Save the total focus time
        cur.execute('INSERT INTO user_focus_time (user_id, time_spent) VALUES (%s, %s)', (user_id, int(total_focus_time)))
        mysql.connection.commit()
        cur.close()

        # Reset tracking variables
        tracking_active = False
        total_focus_time = 0
        return jsonify({'status': 'success', 'message': 'Focus time saved.'})

    return jsonify({'status': 'error', 'message': 'Unauthorized access.'}), 401

# Complete topic route
@app.route('/complete_topic', methods=['POST'])
def complete_topic():
    if 'username' in session:
        username = session['username']
        data = request.json
        topic = data['topic']

        cur = mysql.connection.cursor()

        # Retrieve user id
        cur.execute('SELECT id FROM users WHERE username=%s', (username,))
        user_id = cur.fetchone()

        if user_id:
            user_id = user_id[0]
            # Check if the user already completed this topic
            cur.execute('SELECT * FROM user_topics WHERE user_id=%s AND topic=%s', (user_id, topic))
            result = cur.fetchone()

            if not result:
                # Insert new completed topic for the user
                cur.execute('INSERT INTO user_topics (user_id, topic) VALUES (%s, %s)', (user_id, topic))
                mysql.connection.commit()
                cur.close()
                mysql.connection.close()
                return jsonify({'status': 'success'})
            else:
                cur.close()
                mysql.connection.close()
                return jsonify({'status': 'error', 'message': 'Topic already completed.'}), 400
        else:
            cur.close()
            mysql.connection.close()
            return jsonify({'status': 'error', 'message': 'User not found.'}), 404
    else:
        return jsonify({'status': 'error', 'message': 'Unauthorized access.'}), 401
    


# Serve static files like CodeMirror, CSS, and JavaScript
@app.route('/codemirror-5.65.16/<path:path>')
def serve_codemirror(path):
    return send_from_directory('codemirror-5.65.16', path)

@app.route('/compiler.html')
def show_compiler():
    question_id = request.args.get('question_id', default=None, type=int)
    question = None
    if question_id is not None and 0 <= question_id < len(questions_list):
        question = questions_list[question_id]
    return render_template('compiler.html', question=question)

# Compilation endpoint
@app.route('/compile', methods=['POST'])
def compile_code():
    data = request.json
    code = data.get('code')
    input_data = data.get('input', '')
    lang = data.get('lang', 'python')  # Default to Python if lang is not provided

    try:
        if lang == 'python':
            return compile_python(code, input_data)
        else:
            return jsonify(output='Unsupported language'), 400
    except Exception as e:
        return jsonify(output=f'Server error: {str(e)}'), 500

def compile_python(code, input_data):
    file_path = 'temp.py'
    with open(file_path, 'w') as f:
        f.write(code)

    try:
        run_cmd = ['python', file_path]
        run_process = subprocess.run(run_cmd, input=input_data, capture_output=True, text=True, timeout=10)
        output = run_process.stdout if run_process.returncode == 0 else run_process.stderr
        return jsonify(output=output), 200
    finally:
        os.remove(file_path)

@app.route('/questions.html')
def questions():
    return render_template('questions.html',questions=questions_list)


if __name__ == '__main__':
    app.run(debug=True)
