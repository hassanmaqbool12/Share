import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, Notify, GLib

class askFor():
    
    response = False

    def __init__(self):

        css = b"""

            label {
            font-size:10pt
            }

            #start, #cancel {
            padding:4px 50px;
            margin-bottom:4px
            }

        """

        self.styler = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.styler.load_from_data(css)


        self.main = Gtk.Window(title="Share")
        self.main.connect("destroy", Gtk.main_quit)
        self.main.set_default_size(300, 180)
        self.main.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        box = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=60,
                    expand=True,
                    halign=Gtk.Align.CENTER,
                    valign=Gtk.Align.END
                )

        boxVertical = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=5,
                    expand=True,
                    halign=Gtk.Align.CENTER,
                    valign=Gtk.Align.START
                )

        boxHorizontal = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL,
                    spacing=10,
                    expand=True,
                    halign=Gtk.Align.CENTER,
                    valign=Gtk.Align.END
                )

        self.label1 = Gtk.Label(label="A Password is Required For Safe File Transfer!")
        boxVertical.pack_start(self.label1, False, False, 0)

        self.label2 = Gtk.Label(label="Would you Like to Create one?")
        boxVertical.pack_start(self.label2, False, False, 0)

        self.startsetup = Gtk.Button()
        self.startsetup.set_name("start")
        self.bticon = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.BUTTON)
        self.startsetup.add(self.bticon)
        self.startsetup.connect("clicked", self.yes)
        boxHorizontal.pack_end(self.startsetup, False, False, 0)

        self.cancel = Gtk.Button()
        self.bticon = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        self.cancel.add(self.bticon)
        self.cancel.set_name("cancel")
        self.cancel.connect("clicked", self.stop)
        boxHorizontal.pack_end(self.cancel, False, False, 0)

        box.pack_start(boxVertical, False, False, 0)
        box.pack_start(boxHorizontal, False, False, 0)

        self.main.add(box)
        self.main.show_all()

    def yes(self, widget):
            self.response = True
            self.main.close()

    def run(self):
            Gtk.main()
            Gtk.main_quit()
            return self.response

    def stop(self, widget):
            os._exit(1)

class confirm:
    def __init__(self):
        self.loop = GLib.MainLoop()
        self.response = None

    def on_action(self, n, action):
        if action == 'allow':
            self.response = True
        elif action == 'deny':
            self.response = False
        self.loop.quit()

    def show_notification(self, title):
        Notify.init('File Upload')
        n = Notify.Notification.new("Share", title)
        n.add_action('allow', 'Allow', self.on_action)
        n.add_action('deny', 'Deny', self.on_action)
        n.show()
        self.loop.run()
        return self.response

    


class TakeInput():

    response = False

    def __init__(self):
        self.css = b"""

        #label {
        font-size:12pt;
        font-weight:800
        }

       #ok, #close {
        padding:4px 20px;
        margin-bottom:12px;
        }
        
        """

        self.styler = Gtk.CssProvider()
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        self.styler.load_from_data(self.css)


        self.main = Gtk.Window(title="Share")
        self.main.set_default_size(300, 140)
        self.main.connect("destroy", Gtk.main_quit)
        self.main.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        box = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=20,
                    expand=True,
                    halign=Gtk.Align.CENTER,
                    valign=Gtk.Align.END
                )

        boxVertical = Gtk.Box(
                    orientation=Gtk.Orientation.VERTICAL,
                    spacing=13,
                    expand=True,
                    halign=Gtk.Align.START,
                    valign=Gtk.Align.START
                )

        boxHorizontal = Gtk.Box(
                    orientation=Gtk.Orientation.HORIZONTAL,
                    spacing=10,
                    expand=True,
                    halign=Gtk.Align.END,
                    valign=Gtk.Align.END
                )

        self.label = Gtk.Label(label="Enter Your Key")
        self.label.set_name("label")
        self.label.set_xalign(0)
        boxVertical.pack_start(self.label, False, False, 0)

        self.bar = Gtk.Entry()
        self.bar.set_size_request(275, -1)
        self.bar.connect("activate", self.confirm)
        boxVertical.pack_start(self.bar, True, True, 0)

        self.ok = Gtk.Button()
        self.ok.connect("clicked", self.confirm)
        self.ok.set_halign(1)
        self.bticon = Gtk.Image.new_from_icon_name("object-select-symbolic", Gtk.IconSize.BUTTON)
        self.ok.add(self.bticon)
        self.ok.set_name("ok")
        boxHorizontal.pack_end(self.ok, True, True, 0)

        self.cancel = Gtk.Button()
        self.bticon = Gtk.Image.new_from_icon_name("window-close-symbolic", Gtk.IconSize.BUTTON)
        self.cancel.add(self.bticon)
        self.cancel.connect("clicked", self.stopNow)
        self.cancel.set_halign(1)
        self.cancel.set_name("close")
        boxHorizontal.pack_end(self.cancel, True, True, 0)

        box.pack_end(boxHorizontal, True, True, 0)
        box.pack_end(boxVertical, False, False, 0)

        self.main.add(box)
        self.main.show_all()

    def confirm(self, widget):
        self.result = self.bar.get_text()
        if self.result:
              self.main.destroy()
              self.response = self.result
        else:
             pass
              

    def run(self, text):
        self.label.set_label(text)
        self.bar.grab_focus()
        Gtk.main()
        return self.response
    
    def stopNow(self, widget):
            self.main.destroy()

    def stop(self):
        self.main.destroy()



#listDev().run()
