import os, json, io

import pandas as pd 

from flask              import request, jsonify 
from flask_jwt_extended import jwt_required

from werkzeug.security                         import check_password_hash
from config.miscellaneous.EnvironmentVariables import ADMIN_NAME, ADMIN_PWD
from config.flask_programs.FlaskFileServer     import flask_file_server_interface
from config.flask_programs.FlaskAPIObject      import marketing_team_two_database_object, flask_database_server_user_database

@flask_file_server_interface.route("/upload_data", methods = ["POST"])
@jwt_required()
def upload_data():
    table_name   = request.form["table_name"]
    server_name  = request.form["server_name"]
    db_user_name = request.form["db_user_name"]
    db_user_pwd  = request.form["db_user_pwd"]
    dataframe    = pd.read_json(io.StringIO(request.files["dataframe"].read().decode("utf-8")))
    marketing_team_two_database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", server_name)

    if ((db_user_name in flask_database_server_user_database) and (check_password_hash(flask_database_server_user_database[db_user_name], db_user_pwd))):
        try:
            marketing_team_two_database_object.upload_to_database(table_name, dataframe)
            return jsonify({"status" : f"Operation success, data uploaded to {server_name}.{table_name}"})
        except Exception as E:
            return jsonify({"status" : f"Operation failure, error message {E}"})          
    else:
        return jsonify({"status" : "Bad database user credentials"})

@flask_file_server_interface.route("/query", methods = ["GET"])
@jwt_required()
def query_data():
    server_name      = request.args.get("server_name")
    table_name       = request.args.get("table_name")
    columns_list     = request.args.get("column_names").split(",")
    filter_condition = request.args.get("filter_value")

    try:
        marketing_team_two_database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", server_name)
        result_json_data = pd.DataFrame(marketing_team_two_database_object.get_from_database(table_name, columns_list, filter_condition))
        return result_json_data.to_json()
    except Exception as E:
        return jsonify({"status" : f"Operation failure, error message {E}"})

@flask_file_server_interface.route("/delete", methods = ["DELETE"])
@jwt_required()
def delete_data():
    table_id         = request.args.get("table_id")
    server_name      = request.args.get("server_name")
    column_name      = request.args.get("column_name")
    filter_value     = request.args.get("filter_value")
    filter_condition = request.args.get("filter_condition")

    try:
        marketing_team_two_database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", server_name)
        marketing_team_two_database_object.delete_from_database(table_id, column_name, filter_value, filter_condition)
        output_json = {"status" : "success"}    
    except:
        output_json = {"status" : "failure"}    
    
    return jsonify(output_json)
