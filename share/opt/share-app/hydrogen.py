import os
import shutil
from pathlib import Path
from gi.repository import Gtk, GdkPixbuf

PATH = Path().home()
ROOT = os.path.dirname(__file__)+"/icons/"
IMAGES_EXT = ["svg", "png", "jpg", "jpeg", "webpg", "gif"]
PATH_INDEX = 0
ACTIVE = ""
PRE_ACTIVE = ""
ACTIVE_LIST = []

FORMATS_OF_FOLDERS = {
    "videos":"folder-videos",
    "video":"folder-videos",
    "movies":"folder-videos",
    "movie":"folder-videos",
    "clips":"folder-videos",
    "clip":"folder-videos",
    "pictures":"folder-pictures",
    "picture":"folder-pictures",
    "pictures":"folder-pictures",
    "photos":"folder-pictures",
    "photo":"folder-pictures",
    "images":"folder-pictures",
    "image":"folder-pictures",
    "documents":"folder-documents",
    "document":"folder-documents",
    "downloads":"folder-download",
    "download":"folder-download",
    "music":"folder-music",
    "musics":"folder-music",
    "audio":"folder-music",
    "audios":"folder-music",
    "templates":"folder-templates",
    "template":"folder-templates",
    "desktop":"user-desktop",
    "public":"folder-publicshare",
    "workspace":"folder-projects",
    "workspaces":"folder-projects",
    "project":"folder-projects",
    "projects":"folder-projects",
    "work":"folder-projects",
    "android":"folder-android",
    "android-studio":"folder-android",
    "arduino":"folder-arduino",
}

FORMATS_OF_FILE = {
    "default":"text-plain",
    "pdf":"application-pdf",
    "apk":"android-studio",
    "iso":"media-cdrom",
    "c":"text-x-csrc",
    "java":"text-x-java",
    "hex":"exec",
    "css":"text-css",
    "h":"text-x-chdr",
    "bin":"exec",
    "appimage":"exec",
    "msi":"exec",
    "deb":"application-vnd.debian.binary-package",
    "py":"text-x-python",
    "json":"application-json",
    "zip":"package-x-generic",
    "xz":"package-x-generic",
    "tar":"package-x-generic",
    "cpp":"text-x-c++src",
    "mp4":"media-video",
    "mpv":"media-video",
    "mkv":"media-video",
    "webm":"media-video",
    "ogg":"media-video",
    "mp3":"audio-mpeg",
    "wav":"audio-mpeg",
    "exe":"mintstick-logo-windows",
    "desktop":"exec",
    "so":"application-x-sharedlib",
    "blend":"image-x-3ds",
    "ui":"application-rtf"
}

class Lithium:
    def __init__(self):
        try:
            self.HISTORY = []
            self.ACTIVE = None
            self.PRE_ACTIVE = None
            self.theme = Gtk.IconTheme.get_default() 
        except:
            pass
            
    def check(self, path):
        try:
            return os.path.exists(path)
        except PermissionError:
            return []

    def move(self, src_path, dest_path):
        if self.check(src_path) and self.check(dest_path):
            return
        return False
    
    def remove(self, path):
        if self.check(str(path)):
            if os.path.isdir(str(path)):
                os.rmdir(path)
                return
            return os.remove(path)
        return False

    def paste(self, path, live_path):
        return self.move(path, live_path)

    def rename(self, path, name):
        if self.check(path):
            return os.rename(path, name)
        return False
    
    def get_chunk_size(self, path):
        size = os.path.getsize(path)
        if len(str(size)) > 3:
            return 1024 * 1024
        else:
            return 1024 * 1024
        return

    def get_content(self, path, hidden):
        if self.check(str(path)):
            try:
                result = []
                data = os.scandir(str(path))
                for i in data:
                    if i.name.startswith(".") and hidden is False:
                        continue
                    result.append((
                        i.is_dir(),
                        i.name,
                        i.path
                    ))
                result.sort()
               
                return result
            
            except PermissionError or FileNotFoundError:
                return []
            
        return []

    def search(self, query):
        results = []
        return 
    
    def new_active(self, path):
        global ACTIVE
        global PRE_ACTIVE
        global ACTIVE_LIST
        tared = path.split("/")
        if len(tared) >= 1:
            PRE_ACTIVE = ACTIVE
            ACTIVE = tared[len(tared) - 1]
            if ACTIVE in ACTIVE_LIST:
                return 
            ACTIVE_LIST.append(ACTIVE)
        return
    
    def prepare_value(self, value):
        length = len(value)
        if length > 3:
            sub = None
            if length%3 == 0:
                sub = length / 3
                sub -= 1
                length -= 3*sub
                return value[:int(str(length).split(".")[0])]
            else:
                odd_index = length%3
                return value[:odd_index]+"."+value[odd_index]
        return value
    
    def get_suffex(self, data):
        length = len(data)
        if length <= 3:
            return "B"
        if length <= 6:
            return "kB"
        if length <= 9:
            return "MB"
        if length <= 12:
            return "GB"
        if length <= 15:
            return "TB"
        if length <= 18:
            return "PB"
        return
    
    def get_usage(self, path):
        if self.check(path):
            result = []
            data = shutil.disk_usage(path)
            for i in range(len(data)):
                suffix = self.get_suffex(str(data[i]))
                value = self.prepare_value(str(data[i]))
                result.append(f"{value} {suffix}")

            return result
        
    def get_size(self, path):
        if self.check(path):
            result = ""
            data = os.path.getsize(path)
            suffix = self.get_suffex(str(data))
            value = self.prepare_value(str(data))
            result = f"{value} {suffix}"

            return result
    
    def get_file_type(self, path):
        if self.check(path):
            whole_dir = path.split("/")
            last_item = whole_dir[len(whole_dir) - 1] if len(whole_dir) >= 1 else whole_dir[0]
            whole_last_item = last_item.split(".")
            last_ext = whole_last_item[len(whole_last_item) - 1] if len(whole_last_item) >= 1 else whole_last_item[0]
            if len(whole_last_item) == 1:
                if whole_last_item[0].lower() in ["makefile", "cmake"]:
                    return self.theme.load_icon(
                        "text-x-makefile",
                        64,
                        Gtk.IconLookupFlags.FORCE_SIZE
                        )
                return self.theme.load_icon(
                    FORMATS_OF_FILE["hex"],
                    64,
                    Gtk.IconLookupFlags.FORCE_SIZE
                    )
            if last_ext in IMAGES_EXT:
                return self.theme.load_icon(
                    "image",
                    64,
                    Gtk.IconLookupFlags.FORCE_SIZE
                    )
            try:
                return self.theme.load_icon(
                    FORMATS_OF_FILE[last_ext.lower()],
                    64,
                    Gtk.IconLookupFlags.FORCE_SIZE
                    )
            except:
                return self.theme.load_icon(
                    FORMATS_OF_FILE["default"],
                    64,
                    Gtk.IconLookupFlags.FORCE_SIZE
                    )
        return False
    
    def get_folder_type(self, path):
        if self.check(path):
            whole_dir = path.split("/")
            last_item = whole_dir[len(whole_dir) - 1] if len(whole_dir) >= 1 else whole_dir[0]
            try:
                return self.theme.load_icon(
                    FORMATS_OF_FOLDERS[last_item.lower()],
                    64,
                    Gtk.IconLookupFlags.FORCE_SIZE
                    )
            except:
                return self.theme.load_icon(
                    "folder",
                    64,
                    Gtk.IconLookupFlags.FORCE_SIZE
                    )
        return False
    
    def is_folder(self, Path, is_dir):
        if is_dir:
            return self.get_folder_type(Path)
        
        return self.get_file_type(Path)
    
    def del_file(self, src):
        if self.check(src):
            if os.path.isfile(src):
                os.remove(src)
                return
            if os.path.isdir(src):
                os.rmdir(src)
                return
        
        return
    
    def get_basepath(self, path):
        return os.path.dirname(path)
    
    def get_image(self, path):
        return GdkPixbuf.Pixbuf.new_from_file(path)
    
    def make_dir(self,path):
        try:
            os.mkdir(path)
            return True
        except PermissionError:
            return False