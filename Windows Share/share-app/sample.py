import subprocess
import tkinter as tk
import threading
from tkinter import ttk
from tkinter import messagebox
from PIL import ImageTk
import os
import socket
import base64
import time
import sys
from flask import Flask, jsonify, render_template, request, send_from_directory, send_file
import qrcode
import pyperclip

sysPath = subprocess.run(["echo", "%USERPROFILE%"])
path =  sysPath if sysPath else "C:\\"

format = {
    "mp4":"fas fa-video", "mkv":"fas fa-video", "webm":"fas fa-video", "ogg":"fas fa-video",
    "jpeg":"fas fa-image", "png":"fas fa-image", "gif":"fas fa-image", "jpg":"fas fa-image",
     "mp3":"fas fa-music", "aac":"fas fa-music", "vorbis":"fas fa-music",
     "zip":"fas fa-file-zipper",
     "pdf":"fas fa-file-pdf",
     "iso":"fab fa-linux",
     "apk":"fab fa-android",
     "exe":"fab fa-windows",
     "py":"fab fa-python",
     "java":"fab fa-java",
     "cpp":"fas fa-file-code",
     "js":"fas fa-file-code",
     "css":"fab fa-css",
     "html":"fab fa-html5",
     "word":"fas fa-file-word",
     "powerpoint":"fas fa-file-powerpoint",
     "json":"fas fa-file-lines",
     "7z":"fas fa-file-zipper"
     }

server = Flask(__name__, template_folder="Templates")

@server.route("/")
def index():
    return render_template("greet.html", data=path)

@server.route("/media/<path:path_>")
def media(path_):
    path = "/"+path_.lstrip("/")
    return send_file(path, as_attachment=False)

@server.route("/action/<path:path_>")
def action(path_):
    return jsonify(sysAction(path_))

@server.route("/command/<path:path_>")
def command(path_):
    return jsonify(runCommand(path_))

@server.route("/clipboard", methods=["POST"])
def clipboad():
    payload = request.get_json()
    data = payload.get("data", "")
    text = base64.b64decode(data).decode("utf-8") 
    return jsonify(addText(text))
    
@server.route("/url/<path:path_>")
def getUrl(path_):
    path = "/"+path_.lstrip("/")
    if os.path.isfile(path):
        return jsonify([getLogo(os.path.basename(path)), "/media"+path, os.path.basename(path)])
    else:
        return jsonify(404)

@server.route("/delete/<path:path_>")
def delete(path_):
    path = "/"+path_.lstrip("/")
    data = deleteFile(path)
    return jsonify(data)

@server.route("/files/<path:path_>")
def files(path_):
     path = "/"+path_.lstrip("/")
     data = getFiles("/"+path)
     return jsonify(data)

@server.route("/back/<path:path_>")
def back(path_):
     path = "/"+path_.lstrip("/")
     return jsonify(goBack(path))

@server.route("/download/<path:path_>")
def download(path_):
     path = "/"+path_.lstrip("/")
     if os.path.isfile(path):
          dir = os.path.dirname(path)
          name = os.path.basename(path)
          return send_from_directory(dir, name, as_attachment=True)
     return "404"

@server.route("/upload", methods=["POST"])
def receive():
     files = request.files.getlist("files[]")
     path = request.form["path"]
     for file in files:
        file.save(f"{path}/{file.filename}")
     return "200"

def serverun():
    server.run(port=5000, host="0.0.0.0")
    print(server.static_folder)

thread = threading.Thread(target=serverun)
thread.daemon = True
thread.start()

def popup(text):
    messagebox.showinfo("Share", text)
    
def error(a):
    messagebox.showerror("Share", a) 

def addText(data):
    try:
         pyperclip.copy(data)
         return 200
    except:
        error("ClipBoard Error!")
        return 404

def runCommand(text):
    if text.split() in ["rm", "rf"]:
        return 404
    try:
        return subprocess.run(text, capture_output=True, text=True, shell=True).stdout
    except Exception as e:
        return str(e)

def lock():
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    except:
        subprocess.run(["xdg-screensaver", "lock"])
    finally:
        return 404

def restart():
    try:
        subprocess.run(["shutdown", "/r", "/t", "0"])
    except:
        return 404

def shutdown():
    try:
        subprocess.run(["shutdown", "/s", "/t", "0"])
    except:
        return 404

def sysAction(name):
    if name == "off":
        return shutdown()
    elif name == "lock":
        return lock()
    elif name == "restart":
        return restart()
    else:
        return 404


def deleteFile(path):
     try:
        os.remove(path)
        dic = goBack(path)
        return dic
     except:
        return "400"

def goBack(data):
    pata = data.split("/")
    pata.pop()
    
    nata = "/".join(pata)
    file = getFiles(nata)
    if file == "404":
         return "404"
    else:
      dic = {"data":file, "path":nata}
      return dic  

def getFiles(path):
     try:
        files = os.listdir(path)
        data = []
        if files:
              for file in files:
                  try:
                      if str(file)[0] == ".":
                        pass
                      else:
                        os.listdir(path+"/"+file)
                        data.append(["folder", file])
                  except:
                      logo = getLogo(file)
                      if logo != None:
                         data.append([logo, file])    
        else:
              return "404"
        return data
     except:
        return "404"

def getLogo(name):     
    if str(name)[0] == ".":
        return None
    else:
        process = str(name).split(".")
        file =  process[len(process)-1]
        try:
            return format[file]
        except:
            return "fas fa-file"  

def check():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]

    except Exception as e:

        ip = "127.0.0.1"
    finally:
        s.close()

    s.close()
    port = "5000"
    return f"http://{ip}:{port}/"

url = check()
previousIP = ""

def getQR(url):
    qr = qrcode.QRCode()
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    tkimg = ImageTk.PhotoImage(img)
    return tkimg

app = tk.Tk(className="share")

def closeApp():
    root.destroy()
    sys.exit()

app.title("Share")
label = tk.Label(app)
textIP = tk.Label(app, text="jhkchufial")
back = ttk.Button(app, text="Close", width=40, command=closeApp)
label.pack()
textIP.pack()
back.pack()

def updateIP(url):
    img = getQR(url)
    textIP.config(text=f"Current IP: {url}")
    label.config(image=img)
    label.image = img

updateIP(url)

def ipChange():
    global previousIP
    while True:
        new_url = check()
        if previousIP != new_url:
            previousIP = new_url
            updateIP(new_url)
        time.sleep(1)

thread1 = threading.Thread(target=ipChange)
thread1.daemon = True
thread1.start()

app.mainloop()
