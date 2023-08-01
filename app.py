from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
from model import nlp_model, generate_quiz_questions

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.before_request
def basic_authentication():
    if request.method.lower() == "options":
        return Response()


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
            data["quiz_questions"] = generate_quiz_questions(result["eng_summary"])

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
