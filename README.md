# Carbon-Share

Carbon-Share is a local-network file sharing app for Linux desktops. It runs a Flask server for browser-based file access and, when a graphical session is available, opens a small GTK window that shows the share URL as text and as a QR code.

![ScreenShot](https://github.com/hassanmaqbool12/Share/blob/6826afb023cf68a2c6e23a739076826de7ebbe32/Media/demo.png)

The project is designed for quick sharing across devices on the same network. It supports authentication through the host machine's PAM login, directory browsing, file download and upload, clipboard copy, and trash-based deletion.

This project is strictly designed for Linux desktop users who want to share files over a local network, especially on Debian- and Ubuntu-based systems where the packaged build can be installed directly.

Run it with:

```bash
python3 Code/Share.py
```

For Debian and Ubuntu based systems, a packaged build is also included as `Carbon-Share.deb`.

For full implementation details, flow notes, and function-by-function documentation, see `notes.txt`.

Its next version is upcoming and it will include much more secure API endpoints, This version uses Flask session and the next one would also use auth token method for each API call.