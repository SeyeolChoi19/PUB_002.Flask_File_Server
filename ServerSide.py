import os, jwt, base64

from flask              import Flask, request, jsonify 
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security  import generate_password_hash, check_password_hash
from config.secret_key  import SECRET_KEY

# to be changed
flask_file_server_user_database        = {"" : generate_password_hash("!")}
flask_file_server_interface            = Flask(__name__)
json_web_token_instance                = JWTManager(flask_file_server_interface)
flask_file_server_interface.secret_key = SECRET_KEY
flask_file_server_interface.debug      = True

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
    server_directory = request.form["server_directory"]
    file_object_64   = request.form["transferred_file"]
    os.makedirs(server_directory, exist_ok = True)    

    try: 
        with open(os.path.join(server_directory, file_name), "wb") as transferred_file:
            transferred_file.write(base64.b64decode(file_object_64))

        result_json = {"status" : f"File saved to {os.path.join(server_directory, file_name)}"}
    except IOError:
        result_json = {"status" : "File I/O error. File was not saved to the server"}
    except Exception:
        result_json = {"status" : "Unknown error. File was not saved to the server"}

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

@flask_file_server_interface.route("/search_file", methods = ["GET"])
@jwt_required
def search_file_name_in_server():
    file_name      = request.args.get("file_name")
    file_directory = request.args.get("file_directory")
    output_message = "Operation failed, file not found. Please check if the file name was entered correctly"

    for directory_object in os.walk(file_directory):
        for sub_file in directory_object[2]:
            if (file_name.lower() in sub_file.lower()):
                output_message = f"Operation success, {os.path.join(file_directory, file_name)}"
                break 
    
    return jsonify({"status" : output_message})

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

if (__name__ == "__main__"):
    flask_file_server_interface.run(host = "0.0.0.0", port = 5000, threaded = True)
