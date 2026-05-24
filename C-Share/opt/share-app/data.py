from pathlib import Path
import socket
import pam
import os
import subprocess


def show_error_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {RED}LOG: {RESET}{text}')

def show_success_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {GREEN}LOG: {RESET}{text}')


def popup(header = 'Share', text = 'Hello There!'):
        subprocess.run(["notify-send","-t","4000",header , text])

def verify_pass(name, key):
    try:
        return pam.authenticate(name, key)
    except Exception as e:
        show_error_log(f"Error occurred while verifying password for user {name}: {e}")
        return False

def check():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]

        except Exception:

            ip = "127.0.0.1"
        finally:
            s.close()

        return f"http://{ip}:{PORT}/"

def go_back(data):
    pata = data.split("/")
    pata.pop()
    
    nata = "/".join(pata)
    file = get_files(nata)
    if file == 404:
         return 404
    else:
      dic = {"data":file, "path":nata}
      return dic  

def get_logo(name):     
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
        return 404

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

def take_action(command):
    if command == "lock":
        lock()
    elif command == "off":
        shutdown()
    return

def lock():
    try:
        # XXX Works only on X11 Display server
        subprocess.run(["xdg-screensaver", "lock"])
    except:
        return 404

def shutdown():
    try:
        os._exit(1)
    except:
        return 404

def get_free_port():
    s = socket.socket()
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


PORT = get_free_port()

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
NAME = "Carbon-Share"

path = str(Path.home()) if Path.home() else "/home"

color = "#BEBEBE"

url = check()

previousIP = ""

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
