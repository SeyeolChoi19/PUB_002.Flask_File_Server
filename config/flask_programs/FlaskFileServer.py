import os, base64

from flask                                             import request, jsonify 
from flask_jwt_extended                                import create_access_token, jwt_required
from werkzeug.security                                 import check_password_hash
from config.flask_programs.FlaskAPIObject              import flask_file_server_interface, flask_file_server_user_database, flask_file_server_user_ip_addresses, database_object, root_path_folder
from config.database_operations.log_database_operation import log_database_usage
from config.miscellaneous.validate_file_mime_type      import validate_file_type_and_mime 

@flask_file_server_interface.route("/login", methods = ["POST"])
def login_to_server():
    username = request.json.get("username")
    password = request.json.get("password")

    if ((username in flask_file_server_user_database) and (check_password_hash(flask_file_server_user_database[username], password))):
        access_token = create_access_token(identity = username)
        return jsonify(access_token = access_token)
    else:
        return jsonify({"msg" : "Bad user credentials"})

@flask_file_server_interface.route("/save_file", methods = ["POST"])
@jwt_required()
def save_file_to_server():
    file_name        = request.form["file_name"]
    server_directory = request.form["server_directory"].strip()
    file_object_64   = request.form["transferred_file"]
    file_validity    = validate_file_type_and_mime()

    if (server_directory.startswith(request.remote_addr)):
        try: 
            with open(os.path.join(root_path_folder, server_directory, file_name), "wb") as transferred_file:
                transferred_file.write(base64.b64decode(file_object_64))

            result_json = {"status" : f"File saved to {os.path.join(server_directory, file_name)}"}
            log_database_usage(f"FILE_SERVER_OPERATION: File {file_name} saved to {os.path.join(server_directory, file_name)}", "/save_file", request.remote_addr)
        except IOError:
            result_json = {"status" : "File I/O error. File was not saved to the server"}
        except Exception:
            result_json = {"status" : "Unknown error. File was not saved to the server"}
    else:
        result_json = {"status" : "File path error. Illegal file path"}

    return jsonify(result_json)

@flask_file_server_interface.route("/retrieve_file", methods = ["GET"])
@jwt_required()
def retrieve_file_from_server():
    file_name      = request.args.get("file_name")
    file_directory = request.args.get("file_directory")
    full_file_path = os.path.join(file_directory, file_name)
    result_json    = {"status" : "failure"}

    if (os.path.exists(full_file_path)):
        with open(full_file_path, "rb") as target_file:
            target_file = base64.b64encode(target_file.read()).decode()
        
        result_json = {"status" : "success", "file_object" : target_file}

    return jsonify(result_json)

@flask_file_server_interface.route("/delete_file", methods = ["DELETE"])
@jwt_required()
def delete_file_from_server():
    file_name      = request.args.get("file_name")
    file_directory = request.args.get("file_directory")
    status_message = "Operation failure"

    if (os.path.exists(os.path.join(file_directory, file_name)) != True):
        status_message += ", please check if the file directory was inputted correctly"
    else:
        os.remove(os.path.join(file_directory, file_name))
        status_message = "Operation success, file deleted"
    
    return jsonify({"status" : status_message})
