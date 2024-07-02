import os, json, io

import pandas as pd 

from flask              import request, jsonify 
from flask_jwt_extended import jwt_required

from config.miscellaneous.EnvironmentVariables import ADMIN_NAME, ADMIN_PWD
from config.flask_programs.FlaskFileServer     import flask_file_server_interface
from config.flask_programs.FlaskAPIObject      import database_object

@flask_file_server_interface.route("/upload_data", methods = ["POST"])
@jwt_required()
def upload_data():
    table_name  = request.form["table_name"]
    server_name = request.form["server_name"]
    schema_name = request.form["schema_name"]
    dataframe   = pd.read_json(io.StringIO(request.files["dataframe"].read().decode("utf-8")))
    database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", server_name)

    try:
        database_object.upload_to_database(table_name, dataframe, schema_name = schema_name)
        return jsonify({"status" : f"Operation success, data uploaded to {server_name}.{table_name}"})
    except Exception as E:
        return jsonify({"status" : f"Operation failure, error message {E}"})          
     
@flask_file_server_interface.route("/query", methods = ["GET"])
@jwt_required()
def query_data():
    server_name      = request.args.get("server_name")
    table_name       = request.args.get("table_name")
    schema_name      = request.args.get("schema_name")
    columns_list     = request.args.get("column_names").split(",")
    filter_condition = request.args.get("filter_value")

    try:
        database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", server_name)
        result_json_data = pd.DataFrame(database_object.get_from_database(table_name, columns_list, filter_condition, schema_name = schema_name))
        return result_json_data.to_json()
    except Exception as E:
        return jsonify({"status" : f"Operation failure, error message {E}"})

@flask_file_server_interface.route("/delete", methods = ["DELETE"])
@jwt_required()
def delete_data():
    table_id         = request.args.get("table_id")
    server_name      = request.args.get("server_name")
    schema_name      = request.args.get("schema_name")
    column_name      = request.args.get("column_name")
    filter_value     = request.args.get("filter_value")
    filter_condition = request.args.get("filter_condition")

    try:
        database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", server_name)
        database_object.delete_from_database(table_id, column_name, filter_value, filter_condition, schema_name = schema_name)
        return jsonify({"status" : "success"})
    except Exception as E:
        return jsonify({"status" : f"Operation failure, error message {E}"})
