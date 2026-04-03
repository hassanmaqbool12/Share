import time
import threading
import server
import data
import directShare

# ----------------------------------------------------
# LOCAL APP
# ----------------------------------------------------
class LocalApp:
    def __init__(self):
        self.direct = directShare.App()

    def start(self):
        threading.Thread(target=self.monitor_ip, daemon=True).start()
        threading.Thread(target=self.direct.run, daemon=True).start()
        threading.Thread(target=server.init_server, daemon=True).start()
        data.show_success_log(f"Running on: {data.url}")

    def monitor_ip(self):
        while True:
            try:
                new_url = data.check()
                if data.previousIP != new_url:
                    data.previousIP = new_url
                    data.url = new_url
                    data.url = new_url
                    if "//127.0.0.1" not in data.url.split(":"):
                        server.start_broadcast()
                    self.direct.updateIP(new_url)
            except Exception as e:
                print("[IP Monitor Error]", e)
            time.sleep(2)


# ----------------------------------------------------
# ENTRY POINT
# ----------------------------------------------------
if __name__ == "__main__":

    
    App = LocalApp()
    App.start()

    # Keep alive
    while True:
        time.sleep(1)
