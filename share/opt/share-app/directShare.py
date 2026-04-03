from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import qrcode
import io
import threading
import subprocess
import requests
import socket
import json
import bridge
import struct
import os

app = bridge.start()
data = app.data1
toolBox = app.tools
server = app.server2
PATH = os.path.dirname(__file__)
IP = None
LIST = None
IS_ON = False

class App():

    def __init__(self):
        self.data = bridge.start()
        self.main = Gtk.Window(title="Carbon-Share")
        self.main.connect("destroy", self.stop)
        self.main.set_resizable(False)
        self.main.connect("key-press-event", self.on_key)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        boxVertical = Gtk.Box(
                            orientation=Gtk.Orientation.VERTICAL,
                            spacing=0,
                            expand=True,
                            halign=Gtk.Align.START,
                            valign=Gtk.Align.START
                        )

        self.css = b"""

            #refresh {
                border: 1px solid @theme_selected_bg_color;
                border-radius:0px;
                padding:4px 3px;
                background-color:@theme_selected_bg_color;
                min-width:308px;
            }

            #disable {
                border: 1px solid @theme_selected_bg_color;
                border-radius:0px;
                padding:4px 3px;
                min-width:308px;
            }

            #quit, #quitoff {
             border:none;
             background-color:transparent;
            }

            #quitoff:hover {
            background-color:@theme_selected_bg_color;
            }

            #ip {
              margin:14px 14px;
            }

            #quit:hover {
               color:@theme_selected_bg_color; 
            }

            #quit:active {
               color:@theme_fg_color;
               background-color:@theme_selected_bg_color; 
            }

            #open {
                background-color:@theme_selected_bg_color;
                border:none;
                border-radius:0px;
            }

            #red {
                background:red;
            }

            button {
                background:none;
                border:none;
                border-radius:0px;
            }
        """

        styler = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        styler.load_from_data(self.css)


        self.image = Gtk.Image.new_from_pixbuf()
        self.label = Gtk.Label()
        self.label.set_name("ip")
        boxVertical.pack_start(self.image, False, False, 0)
        boxVertical.pack_start(self.label, False, False, 0)

        box.pack_start(boxVertical, False, False, 0)

        self.main.add(box)
        self.main.show_all()

    def on_key(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            ctrl = event.state & Gdk.ModifierType.CONTROL_MASK

            if event.keyval == Gdk.KEY_i:
                self.aboutus(None)
                return True    

            if event.keyval == Gdk.KEY_q:
                self.stop(None)
                return True   

    
    def aboutus(self, widget):
        import webbrowser
        webbrowser.open("https://github.com/hassanmaqbool12/Share")
        return

    def run(self):
        Gtk.main()

    def filter(self, text):
        edit = text.split(" ")
        return "".join(edit)

    def getQR(self, url):
        qr = qrcode.QRCode(box_size=6, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color=app.data1.color)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        buf.seek(0)
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(buf.getvalue())
        loader.close()
        return loader.get_pixbuf()

    def updateIP(self,url):
        GLib.idle_add(self.label.set_text, url)
        GLib.idle_add(self.image.set_from_pixbuf, self.getQR(url))

    def stop(self, widget):
        os._exit(1)

    def isLocal(self):
        if "//127.0.0.1" in data.url.split(":"):
            data.popup("Device Discovery is not avaliable. Because you are not connected with any network.")
            return True
        else:
            return False
    