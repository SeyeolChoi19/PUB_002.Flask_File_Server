import os

import pandas as pd

from cryptography.fernet                            import Fernet 
from config.database_operations.DBInterfacePostgres import DBInterface 
from config.miscellaneous.EnvironmentVariables      import INFO_KEY, ADMIN_NAME, ADMIN_PWD, TABLE_NAME, SERVER_NAME, DB_INFO_TABLE

fernet_object   = Fernet(os.getenv(INFO_KEY).encode())
database_object = DBInterface()
database_object.connection_settings("postgresql", os.getenv(ADMIN_NAME), os.getenv(ADMIN_PWD), "localhost", os.getenv(SERVER_NAME))

def retrieve_api_user_info(info_flag: str):
    info_flag   = 1 if (info_flag == "password") else 2
    output_data = database_object.get_from_database(os.getenv(TABLE_NAME), ["*"])
    output_dict = {}
    
    for row_number in range(len(output_data)):
        transformed_string_data       = bytes.fromhex(output_data[row_number][0][2:]).decode()
        decoded_username              = fernet_object.decrypt(transformed_string_data).decode()
        string_password_hash          = output_data[row_number][info_flag]
        output_dict[decoded_username] = string_password_hash
    
    return output_dict
