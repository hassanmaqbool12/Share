import gi
gi.require_version('Gtk','3.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import qrcode
import io
import bridge
import os

data = bridge.data_module

class App():

    def __init__(self):
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

            #ip {
              margin:1px;
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
        self.label = Gtk.Button(label='Server URL')
        self.label.set_name("ip")
        boxVertical.pack_start(self.image, False, False, 0)
        boxVertical.pack_start(self.label, False, False, 0)

        box.pack_start(boxVertical, False, False, 0)

        self.label.connect('clicked', self.open_browser)

        self.main.add(box)

    def on_key(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:

            if event.keyval == Gdk.KEY_q:
                self.stop(None)
                return True   

    
    def open_browser(self, widget):
        if data.url:
            import webbrowser
            webbrowser.open(data.url)
        return

    def run(self):
        self.main.show_all()
        Gtk.main()

    def get_QR(self, url):
        qr = qrcode.QRCode(box_size=6, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color=data.color)
        buf = io.BytesIO()
        img.save(buf, "PNG")
        buf.seek(0)
        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(buf.getvalue())
        loader.close()
        return loader.get_pixbuf()

    def update_IP(self,url):
        GLib.idle_add(self.label.set_label, url)
        GLib.idle_add(self.image.set_from_pixbuf, self.get_QR(url))

    def stop(self, widget):
        os._exit(1)
