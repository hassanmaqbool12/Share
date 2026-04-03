import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import threading
import requests
import server
import bridge
import socket
import struct
import json
import sys
import os

app = bridge.start()
data = app.data1

def filter(text):
     edit = text.split(" ")
     return "".join(edit)

class microApp:
    
    IP = ""

    def __init__(self):
        self.window = Gtk.Window(title="Share - Online Devices")
        self.window.set_default_size(340, 220)
        self.window.set_resizable(False)
        self.window.connect("destroy", self.stop)

        self.css = b"""
         #semibox {
          margin:5px;
          margin-bottom:10px
         }
        
         #semibt, #semibt3, #errorbt {
         background-color:transparent;
         border:none
         }

         #send {
          margin-left:80px;
          background-color:transparent;
          border:none
         }

         #semilb,  #errorld {
          margin-top:3px
         }

         #semibt2 {
          background-color:transparent;
          border:none
         }

         #pairbt {
          margin-left:70px;
          background-color:transparent;
          border:none

         }

         #semibt8 {
          background-color:transparent;
          border:none;
          margin-left:150px
         }
        
        """

        self.styler = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.styler.load_from_data(self.css)

        # Create a scrolled window
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_hexpand(True)
        self.scrolled_window.set_vexpand(True)

        # Create a box to hold the widgets
        self.box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=5,
            expand=True,
            halign=Gtk.Align.CENTER,
            valign=Gtk.Align.CENTER
        )

        self.spinner = Gtk.Spinner() 
        self.spinner.start()
        self.box.pack_start(self.spinner,False, False, 0)
        self.scrolled_window.add(self.box)

        # Add the scrolled window and button to the window
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.pack_start(self.scrolled_window, True, True, 0)
        self.window.add(main_box)

        self.window.connect("destroy", self.stop)

    def run(self, url):
        print("[RUNNING MICRO APP]")
        self.scan()
        self.path = url
        self.window.show_all()
        Gtk.main()
    
    def stop(self, widget):
         self.window.destroy()
         os._exit(1)
    
    def scan(self):
         thread = threading.Thread(target=self.scanOn)  
         thread.daemon = True    
         thread.start()

    def askFile(self, widget, url):
        global IP
        IP = url
        print(IP)
        thread = threading.Thread(target=self.sendRequest)
        thread.daemon = True
        thread.start()
        return
             

    def sendRequest(self):
             client = requests.post(f"{IP}request", headers={'Content-Type': 'application/json'}, data=json.dumps({"path":self.path, "url":data.url, "name":data.name}))
             print(client.json())
             if client.json() == 200:
                  data.popup("Request Accepted. Sending File")
             else:
                  data.popup("File Rejected by other Side")
             return

    def scanOn(self):
        dataIP = self.scanDev()
        if dataIP and dataIP != [] and len(dataIP) != 0:
             print("DATA IP", dataIP)
             bio = self.getBio(dataIP)
             if bio and bio != []:
                  self.addWidget(bio)
        else:
             self.spinner.stop()
             self.error()
             return
        
    def clear(self):
         for child in self.scrolled_window.get_children():
              self.scrolled_window.remove(child)



    def error(self):
          self.clear()
          errorbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,halign=Gtk.Align.CENTER,valign=Gtk.Align.CENTER, spacing=8)
          icon = Gtk.Button()
          icon.set_name("errorbt")
          symbol = "face-confused-symbolic"
          bticon = Gtk.Image.new_from_icon_name(symbol, Gtk.IconSize.BUTTON)
          bticon.set_pixel_size(40)
          name = Gtk.Label(label="No Devices found!")
          name.set_name("errorlb")

          icon.add(bticon)
          errorbox.pack_start(icon, True, True, 0)
          errorbox.pack_start(name, False, False,10)

          errorbox.set_valign(Gtk.Align.CENTER)
          self.scrolled_window.add(errorbox)
          self.window.show_all()
          print("[ADDED]")
     
    def sendFile(self, widget, url):
        global IP
        IP = url
        thread = threading.Thread(target=self.sendMSG)
        thread.start()
        return
        
    def sendMSG(self):
          code = f"download {IP} {data.url}download{self.path} {data.name}"
          server.askDown(code)
          return

    def addWidget(self, info):
         for i in range(len(info)):
               name = info[i][0].split(" ")
               if "".join(name) in data.ALLOWED:

                    self.scrolled_window.remove(self.box)
                    self.semibox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL,halign=Gtk.Align.START,valign=Gtk.Align.CENTER)
                    icon = Gtk.Button()
                    symbol = "phone" if info[i][1] == " Android " else "computer"
                    self.bticon = Gtk.Image.new_from_icon_name(symbol, Gtk.IconSize.BUTTON)
                    self.bticon.set_pixel_size(28)
                    name = Gtk.Label(label=info[0][0])
                    name.set_name("semilb")
                    icon.add(self.bticon)
                    icon.set_name("semibt")
                    self.semibox.pack_start(icon, True, True, 0)
                    self.semibox.pack_start(name, False, False,10)
                    name = info[i][0].split(" ")
                    id = "semibt3" if info[i][1] != " Android " else "semibt8"
                    print("[ALLOWED]: ", data.ALLOWED)
                    print("[NAME] : ", "".join(name))

                    send = Gtk.Button()
                    self.sendicon = Gtk.Image.new_from_icon_name("selection-mode-symbolic", Gtk.IconSize.BUTTON)
                    if info[i][1] == " Android " or "Android":
                              send.connect("clicked", self.sendFile, info[i][0])
                    else:
                              send.connect("clicked", self.askFile, info[i][2])
                    self.sendicon.set_pixel_size(15)
                    send.add(self.sendicon)
                    send.set_name(id)
                    self.semibox.pack_end(send, True, True, 3)


         self.semibox.set_name("semibox")
         self.semibox.set_valign(Gtk.Align.START)
         self.scrolled_window.add(self.semibox)
         self.window.show_all()
         
         return

    def getBio(self, IPs):
         info = []
         for i in range(len(IPs)):
              if IPs[i][1] == " Android ":
                   semi = []
                   semi.append(IPs[i][0])
                   semi.append(IPs[i][1])
                   semi.append(IPs[i][2])
                   info.append(semi.copy())
                   semi.clear()
              else:
                    edit = "".join(IPs[i][2].split())
                    url = edit+"about"
                    
                    response  = requests.get(url)
                    if response.status_code == 200:
                         semi = []
                         semi.append(response.json()["bio"])
                         semi.append(IPs[i][1])
                         semi.append(IPs[i][2])
                         info.append(semi.copy())
                         semi.clear()
                    else:
                         self.error()
         return info
    
    def scanDev(self):
        MULTICAST_ADDRESS = '224.1.1.1'
        MULTICAST_PORT = 5000
        
        URL = []

        attempt = 0
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        group = socket.inet_aton(MULTICAST_ADDRESS)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.bind(('', MULTICAST_PORT))
        print(URL, len(URL))

        while True:
            attempt += 1
            print(attempt)
            packets, address = sock.recvfrom(1024)
            try:
                 bio = packets.decode().split("and")
                 if data.name == filter(bio[0]) and data.url == filter(bio[2]):
                      print("SELF DISCOVERED")
                      pass
                 else:
                      URL.append(bio)
                    
            except:
                 pass
            
            if attempt > 4 and len(URL) == 0:
                 print("Break of Length")
                 break
            if attempt > 5:
                 break
        return URL
    

if __name__ == "__main__":
    # Start Flask & UDP server
    url = data.check()
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("[INFO] SERVER ONLINE AT ", url)
            data.popup("A server is alreay running. Please stop that server.")
            os._exit(1)
            pass
    except:
            threading.Thread(target=server.init_server, daemon=True).start()

    # Main execution
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            if "//127.0.0.1" not in data.url.split(":"):
                micro = microApp()
                micro.run(file_path)
                print("[Online Mode]")
            else:
                print("[Local Mode]")
                data.popup("You are offline.")
            sys.exit(0)
        else:
            sys.exit(1)
