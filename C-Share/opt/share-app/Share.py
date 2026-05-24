import time
import threading
import server
import data
import os
import directShare


class App:
    def __init__(self):

        self.direct = None

        if self.is_ui():
            self.direct = directShare.App()

        data.show_success_log('Press Ctrl + C to STOP')

        if self.direct:
            threading.Thread(target=self.monitor_ip, daemon=True).start()
            threading.Thread(target=server.init_server, daemon=True).start()
            data.show_success_log('Starting UI class')
            self.direct.run()

        else:
            threading.Thread(target=self.monitor_ip, daemon=True).start()
            data.show_error_log('Running in headless mode')
            server.init_server()

    def monitor_ip(self): # Monitors IP changes and informs the app to update the QR and the URL
        while True:
            try:
                new_url = data.check()
                if data.previousIP != new_url:
                    data.previousIP = new_url
                    data.url = new_url
                    data.show_success_log(f"[IP INFO] Running on: {data.url}")

                    if self.direct:
                        self.direct.update_IP(new_url) # This will be handled more gracefully in next version
                        
            except Exception as e:
                data.show_error_log(f"IP Monitor Error {e}")
            time.sleep(2)

    def is_ui(self):
        return bool(os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'))


if __name__ == "__main__":
    app = App()
