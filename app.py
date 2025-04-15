import threading
from flask import Flask, render_template, request, jsonify, session, send_file, flash, redirect
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os
import json
import subprocess
import time
from flask_socketio import SocketIO, emit
from chatbot.chatbot import get_bot_response

app = Flask(__name__)
socketio = SocketIO(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")



# Secret key for session management
app.secret_key = "supersecretkey123"

# MongoDB Configuration
app.config["MONGO_URI"] = "mongodb+srv://divyanshurajoria1:div4@cluster0.eugyn.mongodb.net/users?retryWrites=true&w=majority"

try:
    mongo = PyMongo(app)
    db = mongo.db.users  
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    db = None  

# Enable Flask session management
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Paths for JSON files
emotion_context_path = "static/emotion_context.json"
music_prompt_path = "static/music_prompt.json"
tune_path = "static/generated_tune.wav"

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=["POST"])
def signup():
    if db is None:
        flash("Database connection error!", "error")
        return redirect("/")

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    if db.find_one({"email": email}):
        flash("Email already exists!", "error")
        return redirect("/")

    hashed_password = generate_password_hash(password)
    db.insert_one({"username": username, "email": email, "password": hashed_password})
    flash("Sign-up successful! Please log in.", "success")
    return redirect("/")

@app.route('/login', methods=["POST"])
def login():
    if db is None:
        flash("Database connection error!", "error")
        return redirect("/")

    email = request.form["email"]
    password = request.form["password"]
    user = db.find_one({"email": email})

    if user and check_password_hash(user["password"], password):
        session["user"] = user["username"]
        flash("Login successful!", "success")
        return redirect("/dashboard")
    else:
        flash("Invalid credentials!", "error")
        return redirect("/")

@app.route('/dashboard')
def dashboard():
    if "user" in session:
        return render_template("dashboard.html", username=session['user'])
    flash("You need to log in first.", "error")
    return redirect("/")

@app.route('/logout')
def logout():
    session.pop("user", None)
    flash("Logged out successfully!", "success")
    return redirect("/")

# 🔹 **Start Emotion & Context Detection**


@app.route('/start_analysis', methods=['GET'])
def http_start_analysis():
    """Start emotion & context detection via HTTP request."""
    socketio.start_background_task(run_full_analysis)
    return jsonify({"message": "Detection started"}), 202

def run_full_analysis():
    """Runs the full pipeline: emotion & context detection → prompt generation → AI tune generation"""
    
    # Step 1: Run emotion & context detection
    socketio.emit("status_update", {"message": "Detecting emotion and context..."}, to='/')
    subprocess.run(["python", "models/emotion_context.py"], check=True)

    # Load detected emotion & context
    with open("static/emotion_context.json", "r") as file:
        emotion_context = json.load(file)
    
    socketio.emit("status_update", {"message": "Emotion & context detected.", "data": emotion_context}, to='/')

    # Step 2: Generate music prompt based on detected data
    socketio.emit("status_update", {"message": "Generating music prompt..."}, to='/')
    subprocess.run(["python", "models/generate_prompt.py"], check=True)

    # Load generated prompt
    with open("static/music_prompt.json", "r") as file:
        music_prompt = json.load(file)

    socketio.emit("status_update", {"message": "Music prompt generated.", "data": music_prompt}, to='/')

    # Step 3: Generate AI-powered tune
    socketio.emit("status_update", {"message": "Generating AI-powered tune..."}, to='/')
    subprocess.run(["python", "models/tune_generation.py"], check=True)

    socketio.emit("status_update", {"message": "Music therapy is ready! You can now play the tune."}, to='/')

# @app.route('/stop_detection', methods=["GET"])
# def stop_detection():
#     """Fetches final results from `static/emotion_context.json` after detection completes"""
#     if "user" not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     try:
#         with open(emotion_context_path, "r") as f:
#             data = json.load(f)
#             return jsonify({"message": "Detection completed!", "emotion": data["emotion"], "context": data["context"]}), 200
#     except Exception as e:
#         return jsonify({"error": f"Failed to read detection results: {e}"}), 500

# 🎵 **Music Therapy Process**
@app.route('/run_music_therapy', methods=["GET"])
def run_music_therapy():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        subprocess.run(["python", "models/generate_prompt.py"], check=True)
        subprocess.run(["python", "models/tune_generation.py"], check=True)

        return jsonify({"message": "Music Therapy Completed!", "tune_file": tune_path}), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Process failed: {e}"}), 500

@app.route('/play_tune', methods=["GET"])
def play_tune():
    if os.path.exists(tune_path):
        return send_file(tune_path)
    else:
        return jsonify({"error": "Tune file not found"}), 404

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get("message", "")
    bot_response = get_bot_response(user_message)
    return jsonify({"response": bot_response})



if __name__ == "__main__":
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)

# import threading
# from flask import Flask, render_template, request, jsonify, session, send_file, flash, redirect
# from flask_pymongo import PyMongo
# from werkzeug.security import generate_password_hash, check_password_hash
# from flask_session import Session
# import os
# import json
# import subprocess
# import time
# from flask_socketio import SocketIO
# from chatbot.chatbot import get_bot_response

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# # Secret key for session management
# app.secret_key = "supersecretkey123"

# # MongoDB Configuration
# app.config["MONGO_URI"] = "mongodb+srv://divyanshurajoria1:div4@cluster0.eugyn.mongodb.net/users?retryWrites=true&w=majority"

# try:
#     mongo = PyMongo(app)
#     db = mongo.db.users  
# except Exception as e:
#     print(f"MongoDB connection failed: {e}")
#     db = None  

# # Enable Flask session management
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # Paths for JSON files
# emotion_context_path = "static/emotion_context.json"
# music_prompt_path = "static/music_prompt.json"
# tune_path = "static/generated_tune.wav"

# @app.route('/')
# def home():
#     return render_template("index.html")

# @app.route('/signup', methods=["POST"])
# def signup():
#     if db is None:
#         return jsonify({"error": "Database connection error!"}), 500

#     username = request.form["username"]
#     email = request.form["email"]
#     password = request.form["password"]

#     if db.find_one({"email": email}):
#         return jsonify({"error": "Email already exists!"}), 400

#     hashed_password = generate_password_hash(password)
#     db.insert_one({"username": username, "email": email, "password": hashed_password})
#     return jsonify({"message": "Sign-up successful! Please log in."}), 201

# @app.route('/login', methods=["POST"])
# def login():
#     if db is None:
#         return jsonify({"error": "Database connection error!"}), 500

#     email = request.form["email"]
#     password = request.form["password"]
#     user = db.find_one({"email": email})

#     if user and check_password_hash(user["password"], password):
#         session["user"] = user["username"]
#         return jsonify({"message": "Login successful!"}), 200
#     else:
#         return jsonify({"error": "Invalid credentials!"}), 401

# @app.route('/dashboard')
# def dashboard():
#     if "user" in session:
#         return render_template("dashboard.html", username=session['user'])
#     return redirect("/")

# @app.route('/logout')
# def logout():
#     session.pop("user", None)
#     return jsonify({"message": "Logged out successfully!"}), 200

# # 🔹 Emotion & Context Detection
# @app.route("/start_analysis", methods=["GET"])
# def start_analysis():
#     """Trigger emotion & context detection asynchronously."""
#     if "user" not in session:
#         return jsonify({"error": "Unauthorized"}), 401

#     # Start detection in the background
#     socketio.start_background_task(target=start_detection_process)

#     # Return response immediately to avoid WSGI issues
#     return jsonify({"message": "Detection started, check results later!"}), 202

# def start_detection_process():
#     socketio.emit("start_detection")
#     timeout = 35
#     while timeout > 0:
#         if os.path.exists(emotion_context_path):
#             try:
#                 with open(emotion_context_path, "r") as f:
#                     data = json.load(f)
#                     socketio.emit("detection_result", data)
#                     return
#             except Exception:
#                 pass
#         time.sleep(1)
#         timeout -= 1
#     socketio.emit("detection_result", {"error": "Detection timeout!"})

# @app.route('/run_music_therapy', methods=["GET"])
# def run_music_therapy():
#     if "user" not in session:
#         return jsonify({"error": "Unauthorized"}), 401
    
#     try:
#         subprocess.run(["python", "models/generate_prompt.py"], check=True)
#         subprocess.run(["python", "models/tune_generation.py"], check=True)
#         return jsonify({"message": "Music Therapy Completed!", "tune_file": tune_path}), 200
#     except subprocess.CalledProcessError as e:
#         return jsonify({"error": f"Process failed: {e}"}), 500

# @app.route('/play_tune', methods=["GET"])
# def play_tune():
#     if os.path.exists(tune_path):
#         return send_file(tune_path)
#     else:
#         return jsonify({"error": "Tune file not found"}), 404

# @app.route('/chat', methods=['POST'])
# def chat():
#     user_message = request.json.get("message", "")
#     bot_response = get_bot_response(user_message)
#     return jsonify({"response": bot_response})

# if __name__ == "__main__":
#     socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
