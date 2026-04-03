from pathlib import Path
import socket
import json
import pam
import subprocess
import platform

PORT = 5000

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"
NAME = "Carbon-Share"

def show_error_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {RED}LOG: {RESET}{text}')

def show_success_log(text):
    print(f'[{GREEN}{NAME}{RESET}] {GREEN}LOG: {RESET}{text}')

def getPass():
            try:
                with open("share.json", "r") as f:
                    return json.load(f)["session"]
            except:
                return None


def getPAIRS():
        try:
                with open("share.json", "r") as f:
                    return json.load(f)["PAIRS"]
        except:
                return []


def addPAIR(nam):
        return
        nam2 = nam.split(" ")
        name = "".join(nam2)
        if name in ALLOWED:
            return
        ALLOWED.append(name)
        data = {
                    "session":password,
                    "PAIRS":ALLOWED
                }
        with open("share.json", "w") as j:
                    return json.dump(data, j)
        return

def popup(header = 'Share', text = 'Hello There!'):
        subprocess.run(["notify-send","-t","2000",header , text])
        

def savePass(key):
            try:
                data = {
                    "session":key,
                    "PAIRS":[]
                }
                with open("share.json", "w") as j:
                    return json.dump(data, j)
                session.clear()
                session["key"] = key
                global password
                password = key
            except:
                return None
            
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
        return f"http://{ip}:{PORT}/"

def verifyPass(name, key):
    try:
        return pam.authenticate(name, key)
    except Exception as e:
        show_error_log(f"Error occurred while verifying password for user {name}: {e}")
        return False

path = str(Path.home()) if Path.home() else "/home"

name  = platform.node()

status = False

color = "#BEBEBE"

password = getPass()

url = check()

previousIP = ""

abouturl = f"{url}About-Share"
