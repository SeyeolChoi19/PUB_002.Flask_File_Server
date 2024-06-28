import os

import pandas as pd

from cryptography.fernet         import Fernet 
from config.DBInterfacePostgres  import DBInterface 
from werkzeug.security           import check_password_hash
from config.EnvironmentVariables import INFO_KEY, ADMIN_NAME, ADMIN_PWD, TABLE_NAME, SERVER_NAME

SQL_TYPE  = "postgresql"
HOST_NAME = "localhost"

def retrieve_api_user_info():
    fernet_object   = Fernet(os.getenv(INFO_KEY).encode())
    database_object = DBInterface()
    database_object.connection_settings(SQL_TYPE, os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), HOST_NAME, os.getenv(SERVER_NAME))
    output_data     = database_object.get_from_database(os.getenv(TABLE_NAME), ["*"])
    output_dict     = {}
    
    for row_number in range(len(output_data)):
        transformed_string_data       = bytes.fromhex(output_data[row_number][0][2:]).decode()
        decoded_username              = fernet_object.decrypt(transformed_string_data).decode()
        string_password_hash          = output_data[row_number][1]
        output_dict[decoded_username] = string_password_hash
    
    return output_dict
