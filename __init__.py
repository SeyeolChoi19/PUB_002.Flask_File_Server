from config.flask_programs.FlaskDBInterface import flask_file_server_interface

if (__name__ == "__main__"):
    flask_file_server_interface.run(host = "0.0.0.0", port = 5000, threaded = True)
