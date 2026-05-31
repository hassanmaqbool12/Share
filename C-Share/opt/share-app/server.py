import os
from flask import Flask, render_template, request, session, jsonify, send_file, send_from_directory
import base64
import bridge

# ----------------------------------------------------
# INITIAL SETUP
# ----------------------------------------------------
data = bridge.data_module

server = Flask(__name__, template_folder="Templates", static_folder="static")

server.secret_key = "com.carbon.share"

@server.before_request
def check_session():
    if request.endpoint is None:
        return

    allowed = ['index', 'login_route', 'static']

    if "key" not in session and request.endpoint not in allowed:
        data.popup("Carbon-Share: Warning" ,'Unauthorized request has been detected!')
        return jsonify({"error": "unauthorized"}), 403

# ----------------------------------------------------
# ROUTES
# ---------------------------------------------------

@server.route("/", methods=["GET"])
def index():
    if "key" not in session:
        return render_template("login.html")
    return render_template("greet.html", data=data.path)

@server.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return jsonify(200)

@server.route("/url/<path:path_>")
def get_url(path_):
    path = "/"+path_.lstrip("/")
    if os.path.isfile(path):
        return jsonify([data.get_logo(os.path.basename(path)), "/media"+path, os.path.basename(path)])
    else:
        return jsonify(404)

@server.route("/login", methods=["POST"])
def login_route():
    user = request.json

    if user:
        username = user.get("username")
        userpass = user.get("key")
        if data.verify_pass(username, userpass):
            session["key"] = userpass
            return jsonify(200)
        
    return jsonify(404)

@server.route("/action/<command>")
def action(command):
    return jsonify(data.take_action(command))

@server.route("/back/<path:path_>")
def back(path_):
     path = "/"+path_.lstrip("/")
     return jsonify(data.go_back(path))


@server.route("/files/<path:path_>")
def list_files(path_):
    abs_path = os.path.join("/", path_.lstrip("/"))
    files = data.get_files(abs_path)
    return jsonify(files)

@server.route("/media/<path:path_>")
def serve_media(path_):
    abs_path = os.path.join("/", path_.lstrip("/"))
    return send_file(abs_path, as_attachment=False)

@server.route("/download/<path:path_>")
def download_file(path_):
    abs_path = os.path.join("/", path_.lstrip("/"))
    if os.path.isfile(abs_path):
        dir = os.path.dirname(abs_path)
        name = os.path.basename(abs_path)
        response = send_from_directory(dir, name, as_attachment=True)
        return response
    return jsonify({"response":404})

@server.route("/upload", methods=["POST", "GET", "OPTIONS"])
def upload_files():
    if request.method == "OPTIONS":
        return "", 200
    
    files = request.files.getlist("files[]")
    dest = request.form["path"]
    for f in files:

        if dest and f.filename:
            f.save(os.path.join(dest, f.filename))

    data.popup(f"File(s) received and saved at {dest}")
    return jsonify("200"), 200

@server.route("/delete/<path:path_>")
def delete_file(path_):
    abs_path = os.path.join("/", path_.lstrip("/"))
    result = data.safe_delete(abs_path)
    return jsonify(result)

@server.route("/clipboard/copy", methods=["POST"])
def copy_clipboard():
    payload = request.get_json()
    text = base64.b64decode(payload.get("data", "")).decode("utf-8")
    return jsonify(data.write_clipboard(text))



# SERVER ENTRY POINTS
def server_on():

    # Turn OFF the Flask default logs
    import logging
    logging.getLogger('werkzeug').disabled = True
    logging.getLogger('flask.app').disabled = True

    # INIT the server
    server.run(host="0.0.0.0", port=data.PORT , use_reloader=False, debug=False)

def init_server():
    data.show_success_log('Server Started')
    server_on() 
