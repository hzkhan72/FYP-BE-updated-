from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
from model import nlp_model, generate_quiz_questions, gen_quiz
from flask_mysqldb import MySQL
import os

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MYSQL_HOST'] = 'sql6.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql6635952'
app.config['MYSQL_PASSWORD'] = 'KwbjuFXVt8'
app.config['MYSQL_DB'] = 'sql6635952'

mysql = MySQL(app)

upload_folder = os.path.join('static', 'uploads')
app.config['UPLOAD'] = upload_folder

def build_response(body):
    response = jsonify(body)
    return response


@app.before_request
def basic_authentication():
    if request.method.lower() == "options":
        return Response()

@app.route("/signup", methods =['GET'],strict_slashes=False)
@cross_origin(supports_credentials=True)
def signUp():
    response = request.json
    Fname = request.args.get("Fname", None)
    Lname = request.args.get("Lname", None)
    Email = request.args.get("Email", None)
    password = request.args.get("password", None)
    
    print(response)
    data={}
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Email FROM User WHERE Email = %s" , (Email,))
    userDb = list(cursor.fetchall())
    mysql.connection.commit()
    cursor.close()
    ifUserExists = len(userDb) > 0
    if (ifUserExists):
        data['status'] = False
        data['message'] = "User already Exists"
        return build_response(data)
    
    cursor = mysql.connection.cursor()
    cursor.execute(''' INSERT INTO User VALUES(%s,%s,%s,%s)''', (Fname, Lname, Email, password,))
    mysql.connection.commit()
    cursor.close()
    data['status'] = True
    data['message'] = "Signup Successfull"
    return build_response(data)

@app.route("/signin", methods =['GET'])
@cross_origin(supports_credentials=True)

def signIn():
    data = {}
    response = request.json
    Email = request.args.get("Email", None)
    password = request.args.get("password", None)
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Email FROM User WHERE Email = %s" , (Email,))
    userDb = list(cursor.fetchall())
    mysql.connection.commit()
    cursor.close()
    ifUserExists = len(userDb) > 0
    if (not ifUserExists):
        data['status'] = False
        data['message'] = "User Does not exists"
        return build_response(data)
    
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT password FROM User WHERE Email = %s" , (Email,))
    userDb = list(cursor.fetchall())
    print(password)
    isPassCorrect =  userDb[0][0] == password
    mysql.connection.commit()
    cursor.close()
    if (not isPassCorrect):
        data['status'] = False
        data['message'] = "Incorrect Password"
        return build_response(data)

    data['status'] = True
    data['message'] = "Login Successfull"

    return build_response(data)





@app.route("/api/", methods=["GET"], strict_slashes=False)
@cross_origin(supports_credentials=True)
def respond():
    # Retrieve the video_id from url parameter
    vid_url = request.args.get("video_url", None)

    if "youtube.com" in vid_url:
        try:
            video_id = vid_url.split("=")[1]
            try:
                video_id = video_id.split("&")[0]
            except:
                video_id = "False"
        except:
            video_id = "False"
    elif "youtu.be" in vid_url:
        try:
            video_id = vid_url.split("/")[3]
        except:
            video_id = "False"
    else:
        video_id = "False"

    body = {}
    data = {}

    if not video_id:
        data["message"] = "Failed"
        data["error"] = "no video id found, please provide a valid video id."
    elif str(video_id) == "False":
        data["message"] = "Failed"
        data["error"] = "video id invalid, please provide a valid video id."
    else:
        result = nlp_model(video_id)
        if result == "0":
            data["message"] = "Failed"
            data["error"] = "API's not able to retrieve Video Transcript."
        else:
            data["message"] = "Success"
            data["id"] = video_id
            data["result"] = result
            data["quiz_questions"] = gen_quiz(result["eng_summary"])

    body["data"] = data

    return build_response(body)


@app.route("/")
def index():
    body = {}
    body["message"] = "Success"
    body["data"] = "Welcome to YTS API."
    return build_response(body)


def build_response(body):
    response = jsonify(body)
    return response


if __name__ == "__main__":
    app.run(threaded=True, debug=True)
