import gi
gi.require_version("Gtk", "3.0")
import os
import time
import pathlib
import threading
import subprocess
import hydrogen as h
from gi.repository import Gtk, GLib, Gdk, Pango, Gio

PATH = os.path.dirname(__file__)
Li = h.Lithium()
SIZE = 0
HOME_PATH = GLib.get_home_dir()
TO_COPY = ""
IS_MOVE = False

class Fluorine(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.hassan.fluorine")
        GLib.set_application_name("Fluorine")
        self.path = ""
        self.volume_monitor = Gio.VolumeMonitor.get()
        self.widget = None
        self.progress_int = 0
        self.is_rename_on = False

    def do_activate(self):
        self.window = Gtk.ApplicationWindow(application=self, title="Fluorine")
        self.window.set_default_size(800, 500)
        self.guard = None
        self.window.connect("destroy", self.hard_kill)

        styler = Gtk.CssProvider()
        styler.load_from_path(PATH+"/style.css")
        display = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(display, styler, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        left_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        left_box.set_halign(Gtk.Align.START)

        nav_box =  Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)

        self.center_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.center_box.set_halign(Gtk.Align.START)

        self.nav_back = Gtk.Button.new_from_icon_name("pan-start-symbolic", Gtk.IconSize.BUTTON)
        self.nav_back.set_name("back")
        self.nav_next = Gtk.Button.new_from_icon_name("pan-end-symbolic", Gtk.IconSize.BUTTON)
        self.nav_back.set_name("nav-box-bt")
        self.nav_next.set_name("nav-box-bt")
        self.nav_back.set_valign(Gtk.Align.CENTER)
        self.nav_next.set_valign(Gtk.Align.CENTER)
        self.nav_next.set_vexpand(False)
        self.nav_back.set_vexpand(False)

        nav_box.pack_start(self.nav_back, True, True, 0)
        nav_box.pack_start(self.center_box, True, True, 0)
        nav_box.pack_start(self.nav_next, True, True, 0)
        nav_box.set_vexpand(False)
                
        self.back = Gtk.Button.new_from_icon_name("go-next-symbolic-rtl", Gtk.IconSize.BUTTON)
        self.back.set_name("back")
        self.next = Gtk.Button.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        self.next.set_name("next")
        self.up = Gtk.Button.new_from_icon_name("go-up-symbolic", Gtk.IconSize.BUTTON)
        self.back.set_name("nav_bt")
        self.next.set_name("nav_bt")
        self.up.set_name("nav_bt")
        self.back.set_sensitive(False)
        self.up.set_sensitive(False)
        self.next.set_sensitive(False)

        self.back.connect("clicked", self.go_back)
        self.next.connect("clicked", self.go_next)
        self.up.connect("clicked", self.go_up)

        left_box.pack_start(self.back, True, True, 0)
        left_box.pack_start(self.next, True, True, 0)
        left_box.pack_start(self.up, True, True, 0)
        left_box.pack_start(nav_box, True, True, 0)

        right_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        right_box.set_hexpand(True)
        right_box.set_halign(Gtk.Align.END)

        search_bt = Gtk.Button.new_from_icon_name("system-search-symbolic", Gtk.IconSize.BUTTON)
        search_bt.set_valign(Gtk.Align.CENTER)
        search_bt.connect("clicked", self.search_widget)
        search_bt.set_name("search-bt")

        help_bt = Gtk.Button.new_from_icon_name("help-about-symbolic", Gtk.IconSize.BUTTON)
        help_bt.set_valign(Gtk.Align.CENTER)
        help_bt.set_name("search-bt")

        right_box.pack_start(search_bt, True, True, 0)
        right_box.pack_start(help_bt, True, True, 0)
        
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        self.header_box = Gtk.Box()
        self.header_box.set_valign(Gtk.Align.START)
        self.header_box.set_name("header-box")

        self.search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        self.search_box.set_valign(Gtk.Align.START)
        self.search_box.set_halign(Gtk.Align.FILL)
        self.search_box.set_name("search-box")
        self.search_box.hide()

        label = Gtk.Label(label="Search for files: ")
        label.set_name("search-text")
        label.set_halign(Gtk.Align.START)

        self.query = Gtk.Entry()
        self.query.set_hexpand(True)
        self.query.set_halign(Gtk.Align.FILL)
        self.query.set_name("search-entry")
        self.query.connect("activate", self.on_entry_activate)
        self.query.connect("focus-in-event", self.on_focus_in)

        self.search_box.pack_start(label, False, False, 0)
        self.search_box.pack_start(self.query, True, True, 0)

        self.header_box.pack_start(left_box, True, True, 0)
        self.header_box.pack_start(right_box, True, True, 0)

        self.bottom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.bottom_box.set_name("bottom-box")
        self.bottom_box.set_valign(Gtk.Align.END)

        self.text = Gtk.Label(label=f"{SIZE} Items")
        self.text.set_halign(Gtk.Align.CENTER)
        self.text.set_name("bottom-text")

        self.bottom_box.pack_start(self.text, True, True, 0)

        self.action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.action_box.set_valign(Gtk.Align.FILL)
        self.action_box.set_halign(Gtk.Align.FILL)
        self.action_box.set_name("action-box")
        self.action_box.set_vexpand(True)
        self.action_box.set_hexpand(True)

        self.scroll_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, expand=True)
        self.scroll_box.set_valign(Gtk.Align.FILL)
        self.scroll_box.set_halign(Gtk.Align.FILL)
        self.scroll_box.set_name("scroll")

        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_valign(Gtk.Align.FILL)
        self.scrolled_window.set_halign(Gtk.Align.FILL)
        self.scrolled_window.set_name("parent")

        scroll_box = Gtk.Box()
        scroll_box.set_hexpand(True)
        scroll_box.set_vexpand(False)
        scroll_box.set_valign(Gtk.Align.START)
        scroll_box.set_halign(Gtk.Align.START)
        scroll_box.set_name("scroll-box")

        self.parent_box = Gtk.FlowBox()
        self.parent_box.set_row_spacing(20)
        self.parent_box.set_column_spacing(20)
        self.parent_box.set_max_children_per_line(30)
        self.parent_box.set_homogeneous(True)
        self.parent_box.set_vexpand(False)
        self.parent_box.set_hexpand(False)

        self.folder_menu = self.create_folder_menu()
        self.file_menu = self.create_file_menu()
        self.menu = self.create_menu()

        self.window.connect("button-press-event", self.on_menu_toggle)
        self.window.connect("key-press-event", self.on_key_press)

        self.dialog = Gtk.Dialog()
        self.progress = Gtk.ProgressBar(show_text=True)

        self.scrolled_window.add(scroll_box)
        scroll_box.pack_start(self.parent_box, True, True, 0)

        self.scroll_box.pack_start(self.search_box, False, False, 0)
        self.scroll_box.pack_start(self.scrolled_window, True, True, 0)

        self.action_box.pack_start(self.scroll_box, False, True, 0)

        self.main_box.pack_start(self.header_box, False, False, 0)
        self.main_box.pack_start(self.action_box, True, True, 0)
        self.main_box.pack_start(self.bottom_box, False, False, 0)

        self.window.add(self.main_box)
        self.window.show_all()
        GLib.idle_add(self.open_folder, "/storage/emulated/0/")

    def clear(self):
        for child in self.parent_box.get_children():
              self.parent_box.remove(child)

    def highlight(self, widget):
        if self.widget is not None:
            try:
                text = self.widget.get_children()[0].get_children()[1]
                text.get_style_context().remove_class("hover")
            except:
                pass
        if widget is not None:
            context = widget.get_children()[0].get_children()[1].get_style_context()
            context.add_class("hover")
            self.widget = widget
        else:
            self.set_text(self.path)
        return
    
    def show_permission_error(self):
        self.dialog = Gtk.MessageDialog(
            parent=self.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            text=f'This Action requires sudo or super-user'
        )
        self.dialog.format_secondary_text(
            f"Please run files as sudo to execute it"
        )

        self.dialog.add_button("Close", Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)

        self.dialog.set_title("Requires sudo")

        def on_response(widget, response):
            widget.destroy()
            return

        self.dialog.connect("response", on_response)
        self.dialog.show_all()
        return

    def open_folder(self, path):
            self.path = path
            self.search_box.set_visible(False)
            threading.Thread(target=self.scan_dir, args=(False, ),daemon=True).start()

    
    def open_folder_for_folder(self, widget ,event ,path):
            self.highlight(widget)
            if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:  
                self.path = path    
                threading.Thread(target=self.scan_dir, args=(False, ),daemon=True).start()

    def scan_dir(self, hidden):
        GLib.idle_add(self.loader)
        content = Li.get_content(self.path, hidden)
        self.prepare_info()
        self.batch(content)
        return
    
    def prepare_info(self):
        if self.path is not None:
            
            GLib.idle_add(self.set_text, self.path)
            if not self.path in Li.HISTORY:
                Li.HISTORY.append(self.path)
        Li.PRE_ACTIVE = Li.ACTIVE
        Li.ACTIVE = self.path #Ignore This error.

        if len(Li.HISTORY) >= 2:
            self.back.set_sensitive(True)
        return
    
    def batch(self, data):
        GLib.idle_add(self.clear)
        index = 0
        id = None
        for is_dir, name, path in data:
            #BREAK Logic goes here. WILL ADD LATER
            if len(data) >= 150:
                index += 1
                if index >= 60:
                    time.sleep(1)
                    index = 0
            icon = self.get_icon(path, is_dir)
            if icon is False:
                continue
            else:
                widget = self.make_items([icon, name, path, is_dir])
                GLib.idle_add(self.add_items, widget)

        return False
    
    def get_icon(self, path, is_dir):
        return Li.is_folder(path, is_dir)
    
    def add_items(self, widget):
        self.parent_box.add(widget)
        self.parent_box.show_all()
        return
    
    def make_items(self, data):
                if len(data) >= 1:

                    button = Gtk.Button()
                    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
                    button.get_style_context().add_class("button")
                    box.set_hexpand(False)
                    box.set_vexpand(False)                
                    image = Gtk.Image.new_from_pixbuf(data[0])
                    text = Gtk.Label(label=data[1])
                    text.set_ellipsize(Pango.EllipsizeMode.END)
                    text.set_max_width_chars(10)
                    image.set_name("icon-image-folder")
                    box.pack_start(image, True, True, 0)
                    box.pack_start(text, True, True, 0)
                    button.add(box)
                    button.set_hexpand(True)
                    button.set_name(data[2])
                    button.set_valign(Gtk.Align.CENTER)
                    button.set_halign(Gtk.Align.CENTER)
                    button.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                    button.connect("button-press-event", self.on_menu_toggle)
                    if data[3]:
                        button.connect("button-press-event", self.open_folder_for_folder, data[2])
                    else:
                        button.connect("button-press-event", self.open_file_for_gtk, data[2])
                
                return button
    
    def refresh(self):
        self.open_folder(None, Li.ACTIVE)
        return
    
    def show_delete_dialog(self, widget):
        name = os.path.basename(self.path)
        self.dialog = Gtk.MessageDialog(
            parent=self.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            text=f'Are you sure you want to permanently delete "{name}"?'
        )
        self.dialog.format_secondary_text(
            f"If you delete an item, it will be permanently lost"
        )

        self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.dialog.add_button("Delete", Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)

        self.dialog.set_title("Delete '"+name+"'?")

        def on_response(widget, response):
            widget.destroy()
            self.delete_file(response == Gtk.ResponseType.OK)
            return

        self.dialog.connect("response", on_response)
        self.dialog.show_all()
        return
    
    def show_rename_error(self, name):
        self.dialog = Gtk.MessageDialog(
            parent=self.window,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            text=f'The item could not be renamed.'
        )
        self.dialog.format_secondary_text(
            f"The name '{name}' is already used in this folder, Please use a diffrent name."
        )

        self.dialog.add_button("OK", Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)

        def on_response(widget, response):
            widget.destroy()
            return

        self.dialog.connect("response", on_response)
        self.dialog.show_all()
        return
    
    def move_to_trash(self, widget):
        global IS_MOVE
        IS_MOVE = True
        address = f"{str(HOME_PATH)}/.recycle"
        path = str(address+"/"+os.path.basename(self.path))
        if os.path.exists(path):
            return
        self.start_copy(self.path, address)
        return
    
    def ask_conflict(self):
        name = os.path.basename(self.path)
        self.dialog = Gtk.MessageDialog(
            parent=self.window,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            text=f'A file with same name already exists in "{name}"?'
        )
        self.dialog.format_secondary_text(
            f"Please select Replace to replace this file with existing one"
        )

        self.dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        self.dialog.add_button("Replace", Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)

        self.dialog.set_title("Conflit")

        def on_response(widget, response):
            widget.destroy()
            if response == Gtk.ResponseType.OK:
                self.start_copy(TO_COPY, self.path)
            return

        self.dialog.connect("response", on_response)
        self.dialog.show_all()
        return
    
    def go_back(self, widget):
        history = Li.HISTORY.copy()
        if len(history) >= 1 and Li.ACTIVE in history:
            index = history.index(Li.ACTIVE)
            target = index - 1 if index >= 1 else 0
            self.open_folder(widget ,Li.HISTORY[target])
            if target == 0:
                GLib.idle_add(self.back.set_sensitive, False)
        return
    
    def go_next(self, widget):
        if len(Li.HISTORY) > h.PATH_INDEX:
            h.PATH_INDEX += 1
            self.open_folder(widget, Li.HISTORY[h.PATH_INDEX - 1])
        return
    
    def go_up(self, widget):
        if len(Li.HISTORY) > 1 and h.PATH_INDEX > len(Li.HISTORY):
            tared = Li.HISTORY[h.PATH_INDEX - 1].split("/")
            tared.pop()
            h.PATH_INDEX -= 1
            self.open_folder(widget, "/".join(tared))
        return

    def open_file_for_gtk(self, widget, event, path):
        self.highlight(widget)
        if event.type == Gdk.EventType._2BUTTON_PRESS and event.button == 1:
            try:
                file = Gio.File.new_for_path(path)
                info = file.query_info(
                    "standard::content-type",
                    Gio.FileQueryInfoFlags.NONE,
                    None
                )

                content_type = info.get_content_type()
                app = Gio.AppInfo.get_default_for_type(content_type, False)

                if app:
                    app.launch([file], None)
            except:  
                subprocess.run(["xdg-open", path])
        return
    
    def add_header(self, name, path):
    
        childs = self.center_box.get_children()
        if h.ACTIVE == name and len(childs) > 0:
            return
        
        if name in h.ACTIVE_LIST:
            h.PRE_ACTIVE = h.ACTIVE
            h.ACTIVE = name
            return
  
        if name not in h.ACTIVE_LIST:
            Li.new_active(path)

            if not os.path.isdir("/home/"+"/".join(h.ACTIVE_LIST)):
                print("[LOG] TRACK CHANGED")
                if not self.update_header(childs):
                    return
        
        bt = None
        if name == ".saved":
            bt = Gtk.Button(label="Bookmarks")
        elif name == ".recycle":
            bt = Gtk.Button(label="Trash")
        elif name == "":
            self.clear_center()
            bt = Gtk.Button.new_from_icon_name("drive-harddisk-symbolic", Gtk.IconSize.BUTTON)
        elif name == os.path.basename(HOME_PATH):
            self.clear_center()
            bt = Gtk.Button.new_from_icon_name("user-home-symbolic", Gtk.IconSize.BUTTON)
        else:
            bt = Gtk.Button(label=name)

        bt.set_name("head-bt")
        bt.connect("clicked", self.open_folder, path)
        self.center_box.pack_start(bt, True, True, 0)
        bt.set_valign(Gtk.Align.CENTER)
        self.update_window()
        return
    
    def clear_center(self):
        childs = self.center_box.get_children()
        for child in childs:
            self.center_box.remove(child)
        return
    
    def update_window(self):
        self.window.show_all()
        self.search_widget(None)
        
    
    def update_header(self, childs):

        base = pathlib.Path.cwd().parent.name

        if base in h.ACTIVE_LIST:
            target = h.ACTIVE_LIST.index(h.PRE_ACTIVE)+2 #if h.PRE_ACTIVE in h.ACTIVE_LIST else h.ACTIVE_LIST.index(base)
            length = len(h.ACTIVE_LIST)
            index  = length - target
            if target >= index:
                h.ACTIVE_LIST.pop()
                Li.HISTORY.pop()
                h.PATH_INDEX -= 1
                self.center_box.remove(childs[len(childs)-1])
                return True
            
            for i in range(target, length):
                    res = (index-i)+i-1
                  
                    h.ACTIVE_LIST.pop(res)
                    Li.HISTORY.pop(res)
                    h.PATH_INDEX -= 1
                    self.center_box.remove(childs[i])
                    index -= 1
            return True
        return False
    
    
    def set_text(self, path):
        storage = Li.get_usage(PATH)
        try:
          name = os.path.basename(path)
          self.window.set_title(name)

        except PermissionError or FileNotFoundError:
            return
            
        except Exception:
            return
    
    def open_folder_for_menu(self, widget):
        self.open_folder(widget, self.path)
    
    def on_menu_toggle(self, widget, event):
        name = widget.get_name()
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
                
                if name == "GtkApplicationWindow":
                    self.path = Li.ACTIVE
                    self.menu.popup_at_pointer(event)
                    return True
                
                if os.path.isdir(name):
                    self.path = name
                    self.folder_menu.popup_at_pointer(event)
                    return True
                
                if os.path.isfile(name):
                    self.path = name
                    self.file_menu.popup_at_pointer(event)
                    return True
  
        self.highlight(None)

    def on_key_press(self, widget, event):
        if event.type == Gdk.EventType.KEY_PRESS:
            ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
            if ctrl and event.keyval == Gdk.KEY_f:
                self.search_widget(None)
                return True    
    
    def create_folder_menu(self):
        menu = Gtk.Menu()
        menu.set_name("menu")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        image = Gtk.Image.new_from_icon_name("folder-open-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Open")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(10)
        box.set_halign(Gtk.Align.START)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        open = Gtk.MenuItem()
        open.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        box.set_vexpand(False)
        image = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Copy")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(10)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        copy = Gtk.MenuItem()
        copy.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("edit-cut-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Cut")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(10)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        cut = Gtk.MenuItem()
        cut.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("xapp-favorite-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Add to Favorite")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        fav = Gtk.MenuItem()
        fav.add(box)

        rename = Gtk.MenuItem(label="Rename")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("add-files-to-archive-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Compress....")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        arch = Gtk.MenuItem()
        arch.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_name("menu-box")
        box.set_vexpand(False)
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Move to Trash")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        trash = Gtk.MenuItem()
        trash.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Delete")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        dele = Gtk.MenuItem()
        dele.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("document-properties-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Properties")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        prop = Gtk.MenuItem()
        prop.add(box)

        open.connect("activate", self.open_folder_for_menu)
        trash.connect("activate", self.move_to_trash)
        dele.connect("activate", self.show_delete_dialog)

        menu.append(open)
        menu.append(copy)
        menu.append(cut)
        menu.append(rename)
        menu.append(fav)
        menu.append(arch)
        menu.append(trash)
        menu.append(dele)
        menu.append(prop)

        menu.show_all()
        return menu
    
    def create_file_menu(self):
        menu = Gtk.Menu()
        menu.set_name("menu")

        open = Gtk.MenuItem(label="Open...")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        box.set_vexpand(False)
        image = Gtk.Image.new_from_icon_name("edit-copy-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Copy")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(10)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        copy = Gtk.MenuItem()
        copy.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("edit-cut-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Cut")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(10)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        cut = Gtk.MenuItem()
        cut.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("xapp-favorite-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Add to Favorite")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        fav = Gtk.MenuItem()
        fav.add(box)

        rename = Gtk.MenuItem(label="Rename")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("add-files-to-archive-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Compress....")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        arch = Gtk.MenuItem()
        arch.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_name("menu-box")
        box.set_vexpand(False)
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Move to Trash")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        trash = Gtk.MenuItem()
        trash.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Delete")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        dele = Gtk.MenuItem()
        dele.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("document-properties-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Properties")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        prop = Gtk.MenuItem()
        prop.add(box)

        open.connect("activate", self.open_folder,)
        trash.connect("activate", self.move_to_trash)
        dele.connect("activate", self.show_delete_dialog)

        menu.append(open)
        menu.append(copy)
        menu.append(cut)
        menu.append(fav)
        menu.append(arch)
        menu.append(trash)
        menu.append(dele)
        menu.append(prop)

        menu.show_all()
        return menu
    
    def create_menu(self):
        menu = Gtk.Menu()
        menu.set_name("menu")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        image = Gtk.Image.new_from_icon_name("folder-new-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Create New Folder")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(30)
        box.set_halign(Gtk.Align.START)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        open = Gtk.MenuItem()
        open.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        box.set_vexpand(False)
        image = Gtk.Image.new_from_icon_name("document-new-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Create New Document")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(30)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        copy = Gtk.MenuItem()
        copy.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("edit-paste-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Paste")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        text.set_max_width_chars(30)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        pas = Gtk.MenuItem()
        pas.add(box)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.set_hexpand(False)
        box.set_vexpand(False)
        box.set_name("menu-box")
        box.set_halign(Gtk.Align.START)
        image = Gtk.Image.new_from_icon_name("document-properties-symbolic", Gtk.IconSize.BUTTON)
        image.set_pixel_size(15)
        text = Gtk.Label(label="Properties")
        text.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        box.pack_start(image, False, False, 0)
        box.pack_start(text, True, True, 0)
        prop = Gtk.MenuItem()
        prop.add(box)

        menu.append(open)
        menu.append(copy)
        menu.append(pas)
        menu.append(prop)

        menu.show_all()
        return menu
    
    def loader(self):
        box = Gtk.Box()
        box.set_hexpand(True)
        box.set_vexpand(True)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        spinner = Gtk.Spinner()
        spinner.set_halign(Gtk.Align.CENTER)
        spinner.set_valign(Gtk.Align.CENTER)
        spinner.set_size_request(30, 30)
        box.pack_start(spinner, True, True, 0)
        self.clear()
        self.parent_box.add(box)
        spinner.show()
        spinner.start()
        return
    
    def on_focus_in(self, entry, event):
        entry.select_region(0, -1)
        return False
    
    def on_entry_activate(self, entry):
        text = entry.get_text()
        
        return True
            
    def search_widget(self, widget):
        if self.search_box.is_visible():
            self.search_box.set_visible(False)
            return
        self.search_box.set_visible(True)
        self.query.grab_focus()
        return
    
    
    def empty(self, name):
        self.clear()
        return
    
    def hard_kill(self, widget):
        os._exit(1)
        return


if __name__=="__main__":  
    app = Fluorine()    
    app.run()