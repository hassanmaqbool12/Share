import os
import time
import random
import socket
import struct
import threading
import subprocess
from pathlib import Path
from flask_cors import CORS
from flask import Flask, render_template, url_for, redirect, request, session, jsonify, send_file, send_from_directory
import requests
import base64
import bridge

# ----------------------------------------------------
# INITIAL SETUP
# ----------------------------------------------------
app = bridge.start()
data = app.data1
toolBox = app.tools

password = data.getPass()

server = Flask(__name__, template_folder="Templates", static_folder="static")

server.secret_key = "com.carbon.share"

CORS(server, resources={r"/*" :{"origins" : "*"}}, supports_credentials=False , allow_headers="*", expose_headers="*", methods=["GET", "POST", "OPTIONS"])


FILE_ICONS = {
    "mp4": "fas fa-video", "mkv": "fas fa-video", "webm": "fas fa-video", "ogg": "fas fa-video",
    "jpeg": "fas fa-image", "png": "fas fa-image", "gif": "fas fa-image", "jpg": "fas fa-image",
    "mp3": "fas fa-music", "aac": "fas fa-music", "vorbis": "fas fa-music",
    "zip": "fas fa-file-zipper", "7z": "fas fa-file-zipper", "gz": "fas fa-file-zipper", "xz": "fas fa-file-zipper",
    "pdf": "fas fa-file-pdf", "iso": "fab fa-linux", "apk": "fab fa-android", "exe": "fab fa-windows",
    "py": "fab fa-python", "java": "fab fa-java", "cpp": "fas fa-file-code", "js": "fas fa-file-code",
    "css": "fab fa-css", "html": "fab fa-html5", "word": "fas fa-file-word", "powerpoint": "fas fa-file-powerpoint",
    "json": "fas fa-file-lines"
}

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
def getUrl(path_):
    path = "/"+path_.lstrip("/")
    if os.path.isfile(path):
        return jsonify([getLogo(os.path.basename(path)), "/media"+path, os.path.basename(path)])
    else:
        return jsonify(404)

@server.route("/login", methods=["POST"])
def login_route():
    user = request.json
    username = user.get("username")
    userpass = user.get("key")
    if data.verifyPass(username, userpass):
        session["key"] = userpass
        return jsonify(200)
    return jsonify(404)

@server.route("/about")
def about():
    return jsonify({"bio": data.name})


"""@server.route("/request", methods=["POST", "GET"])
def fileRequest():
    try:
        data = request.json
        print(data)
        path = data["path"]
        ip = data["url"]
        name = data["name"]
        handler  = toolBox.confirm()
        def show_and_wait():
            return handler.show_notification(f"{name} wants to Send a File. Please Confirm!")
        thread = threading.Thread(target=show_and_wait)
        thread.start()
        thread.join()
        if handler.response:
            getFile(path, ip, name)
            return jsonify(200)
        
        return jsonify(400)
    except:
        return jsonify(400)

@server.route("/pair/<name>", methods=["POST", "GET"])
def pairRequest(name):
    try:
        if name in data.ALLOWED:
            return jsonify(data.name)
        handler  = toolBox.confirm()
        def show_and_wait():
            return handler.show_notification(f"{name} wants to Pair with you. Please Allow or Deny!")
        thread = threading.Thread(target=show_and_wait)
        thread.start()
        thread.join()
        if handler.response:
            data.addPAIR(name)
            return jsonify({"response":200, "name":data.name})
        
        return jsonify({"response":404})
    except Exception as e:
        return jsonify({"response":404})"""

@server.route("/action/<command>")
def action(command):
    return jsonify(takeAction(command))

@server.route("/back/<path:path_>")
def back(path_):
     path = "/"+path_.lstrip("/")
     return jsonify(goBack(path))

# ----------------------------------------------------
# FILE MANAGEMENT
# ----------------------------------------------------

#@server.route("/path")
#def getpath():
#    return jsonify(data.path)


@server.route("/files/<path:path_>")
def list_files(path_):
    abs_path = os.path.join("/", path_.lstrip("/"))
    files = get_files(abs_path)
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
        f.save(os.path.join(dest, f.filename))
    data.popup(f"File(s) received and saved at {dest}")
    return jsonify("200"), 200

@server.route("/delete/<path:path_>")
def delete_file(path_):
    abs_path = os.path.join("/", path_.lstrip("/"))
    result = safe_delete(abs_path)
    return jsonify(result)

# ----------------------------------------------------
# CLIPBOARD MANAGEMENT
# ----------------------------------------------------
@server.route("/clipboard/copy", methods=["POST", "GET"])
def copy_clipboard():
    payload = request.get_json()
    text = base64.b64decode(payload.get("data", "")).decode("utf-8")
    return jsonify(write_clipboard(text))

"""
@server.route("/clipboard/copy-pc", methods=["POST", "GET"])
def copy_clipboard_pc():
    payload = request.json
    text = payload["data"]
    return jsonify(write_clipboard(text))

@server.route("/clipboard/paste", methods=["POST", "GET"])
def paste_clipboard():
    try:
        result = subprocess.run(["xclip", "-selection", "clipboard", "-o"], stdout=subprocess.PIPE)
        return jsonify(result.stdout.decode("utf-8"))
    except Exception as e:
        return jsonify(400)"""

# ----------------------------------------------------
# FILE UTILS
# ----------------------------------------------------

def get_content(name ,path):
    data = {
        "name":name,
        "path":path
    }
    #ws.emit("get-path", data)
    return

def getFile(path, ip, name):
    downloadRequest(ip+"download"+path, path)
    return

def downloadRequest(url, pathFile):
    try:
        name = Path(pathFile).name
        path = f"{data.path}/Downloads"
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        savedPath = os.path.join(path, name)
        response = requests.get(url, stream=True)
        if response == 400:
            data.popup("File Rejected by Client!")
            return
        with open(savedPath, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        data.popup(f"File {Path(savedPath).name} Received and Saved")
        return
    except:
        data.popup("Cannot Download File. Reason: Process Terminated")


def goBack(data):
    pata = data.split("/")
    pata.pop()
    
    nata = "/".join(pata)
    file = get_files(nata)
    if file == 404:
         return 404
    else:
      dic = {"data":file, "path":nata}
      return dic  

def getLogo(name):     
    if str(name)[0] == ".":
        return None
    else:
        process = str(name).split(".")
        file =  process[len(process)-1]
        try:
            return FILE_ICONS[file]
        except:
            return "fas fa-file" 

def get_files(path):
    try:
        entries = os.listdir(path)
        output = []

        if not entries:
            return []
        
        for entry in entries:
            if entry.startswith("."):  # skip hidden
                continue
            abs_entry = os.path.join(path, entry)
            if os.path.isdir(abs_entry):
                output.append(["folder", entry])
            else:
                icon = FILE_ICONS.get(entry.split(".")[-1], "fas fa-file")
                output.append([icon, entry])
        output.sort()
        return output
    except Exception:
        return "404"

def safe_delete(path):
    try:
        subprocess.run(["gio", "trash", str(path)], check=False)
        parent = os.path.dirname(path)
        return {"data": get_files(parent), "path": parent}
    except:
        return "400"

def write_clipboard(data_text):
    try:
        subprocess.run(["xclip", "-selection", "clipboard"], input=data_text.encode(), check=True)
        return 200
    except:
        return 400

def takeAction(command):
    if command == "lock":
        lock()
    elif command == "off":
        shutdown()
    else:
       pass 
    return

def lock():
    try:
        subprocess.run(["xdg-screensaver", "lock"])
    except:
        return 404

def shutdown():
    try:
        os._exit(1)
    except:
        return 404

# ----------------------------------------------------
# NETWORK BROADCASTING (UDP)
# ----------------------------------------------------
def broadcast_service():
    MULTICAST_ADDRESS = '224.1.1.1'
    MULTICAST_PORT = 5000
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    ttl = struct.pack('B', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
    while True:
        try:
            message = f"{data.name} and PC and {data.url}"
            sock.sendto(message.encode(), (MULTICAST_ADDRESS, MULTICAST_PORT))
            time.sleep(2)
        except Exception as e:
            print("[Broadcast Error]", e)
            time.sleep(5)

def start_broadcast():
    threading.Thread(target=broadcast_service, daemon=True).start()

# ----------------------------------------------------
# SERVER ENTRY POINTS
# ----------------------------------------------------
def server_on():
    server.run(host="0.0.0.0", port=data.PORT , use_reloader=False, debug=True)

def start_server():
    threading.Thread(target=server_on, daemon=True).start()

def init_server():
    try:
        start_server()
    except Exception as e:
        data.show_error_log(e)
        data.PORT += random.randint(10, 900)
        start_server()


def ofSession(state, key):
    if state is True:
        session["key"] = key
    elif state is False:
        session.clear()
    else:
        return     
    
