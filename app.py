import sqlite3
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import os
import signal
import sys
from database import create_database

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('templates'),  # assuming your templates are in a directory named "templates"
    autoescape=select_autoescape(['html', 'xml'])
)

dbname = 'app.db'

class MyHttpRequestHandler(SimpleHTTPRequestHandler):


    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        if self.path == '/home':
            # Check if the user is logged in
            cookie = self.headers.get('Cookie')
            if cookie is None:
                # No cookie, redirect to login page
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return

            # Check if the cookie is valid
            cookie = cookie.split('=')[1]
            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=?", (cookie,))
            user = cursor.fetchone()
            if user is None:/
                # Invalid cookie, redirect to login page
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
                return

            # Valid cookie, show the home page
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            template = env.get_template('home.html')
            lastname='tushar'
            home_page = template.render(username=cookie,lastname=lastname)
            self.wfile.write(home_page.encode())
            return
        return super().do_GET()

    def do_POST(self):
        if self.path == '/login':
            content_len = int(self.headers.get('Content-Length'))
            post_body = self.rfile.read(content_len)
            data = urllib.parse.parse_qs(post_body.decode())
            username = data.get('username', [''])[0]
            password = data.get('password', [''])[0]

            conn = sqlite3.connect(self.dbname)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            user = cursor.fetchone()

            if user is None:
                # No such user, register them
                cursor.execute("INSERT INTO users VALUES (?, ?)", (username, password))
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Registered successfully, you can login now.")
            else:
                # User exists, check the password
                if user[1] == password:
                    # Redirect to home.html
                    self.send_response(302)  # 302 means "Found" and is commonly used for redirection
                    self.send_header("Set-Cookie", f"username={username};")  # Set the cookie
                    self.send_header("Location", "/home")  # This is the URL the client should redirect to
                    self.end_headers()
                else:
                    self.send_response(401)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    template = env.get_template('error.html')
                    error_page = template.render(error_message='Invalid username or password.')
                    self.wfile.write(error_page.encode())

            conn.commit()
            conn.close()
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Not Found")


def signal_handler(signal, frame):
    print("\nServer is stopping...")
    sys.exit(0)


if __name__ == '__main__':

    create_database(dbname)

    handler_object = MyHttpRequestHandler
    handler_object.dbname = dbname

    signal.signal(signal.SIGINT, signal_handler)

    PORT = 8000
    my_server = HTTPServer(("localhost", PORT), handler_object)

    print(f"Server running on port {PORT}")
    print("Press Ctrl+C to stop")
    try:
        my_server.serve_forever()
    except KeyboardInterrupt:
        pass

    my_server.server_close()
    print("Server stopped.")
