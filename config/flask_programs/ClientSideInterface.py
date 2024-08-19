import os, base64, requests

import pandas as pd 

class ClientSideInterface:
    def login_to_server(self, username: str, password: str, target_ip: str):
        api_url  = f"{target_ip}/login"
        response = requests.post(
            api_url, 
            json = {
                "username" : username, 
                "password" : password
            }
        )

        if (response.status_code == 200):
            self.jwt_token = response.json()["access_token"]
            return "login successful"
        else:
            return "login failed"

    def upload_file_to_server(self, local_file_name: str, server_file_name: str, target_ip: str):
        server_directory_array = server_file_name.replace("\\", "/").split("/")
        server_directory       = "/".join(server_directory_array[:-1])
        file_name              = server_directory_array[-1]
        
        with open(local_file_name, "rb") as file_object:
            file_object_base64 = base64.b64encode(file_object.read()).decode()

        api_url  = f"{target_ip}/save_file"
        response = requests.post(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            data = {
                "file_name"        : file_name, 
                "server_directory" : server_directory
            },
            files = {
                "transferred_file" : file_object_base64
            }
        )

        return response.json()["status"]

    def retrieve_file_from_server(self, server_file_name: str, destination_folder: str, target_ip: str):
        server_directory_array = server_file_name.replace("\\", "/").split("/")
        server_directory       = "/".join(server_directory_array[:-1])
        file_name              = server_directory_array[-1]

        api_url  = f"{target_ip}/retrieve_file"
        response = requests.get(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            params = {
                "file_name"      : file_name, 
                "file_directory" : server_directory
            }
        )

        with open(os.path.join(destination_folder, file_name), "wb") as retrieved_file: 
            retrieved_file.write(base64.b64decode(response.json()["file_object"]))

        return response

    def search_file_server(self, server_file_name: str, target_ip: str):
        server_directory_array = server_file_name.replace("\\", "/").split("/")
        file_directory         = "/".join(server_directory_array[:-1])
        file_name              = server_directory_array[-1]

        api_url  = f"{target_ip}/search_file"
        response = requests.get(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            params = {
                "file_name"      : file_name, 
                "file_directory" : file_directory
            }
        )

        return response.json()["status"]

    def delete_from_server(self, server_file_name: str, target_ip: str):
        server_directory_array = server_file_name.replace("\\", "/").split("/")
        file_directory         = "/".join(server_directory_array[:-1])
        file_name              = server_directory_array[-1]

        api_url  = f"{target_ip}/delete_file"
        response = requests.delete(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            params = {
                "file_name"      : file_name, 
                "file_directory" : file_directory 
            }
        )

        return response.json()
    
    def upload_to_database(self, table_name: str, server_name: str, target_ip: str, data_to_upload: pd.DataFrame, schema_name: str = "public"):
        api_url  = f"{target_ip}/upload_data"
        response = requests.post(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            data = {
                "table_name"  : table_name, 
                "server_name" : server_name,
                "schema_name" : schema_name
            },
            files = {
                "dataframe" : data_to_upload.to_json()
            }
        )

        return response
    
    def query_database(self, table_name: str, server_name: str, target_ip: str,  columns_list: list[str], filter_value: str = None, schema_name: str = "public"):
        filter_value = "" if (filter_value == None) else filter_value

        api_url  = f"{target_ip}/query"
        response = requests.get(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            params = {
                "server_name"      : server_name,
                "table_name"       : table_name,
                "schema_name"      : schema_name,
                "column_names"     : ",".join(columns_list),
                "filter_condition" : (lambda x: "" if (x == None) else x)(filter_value)
            }
        )
        
        return response
    
    def delete_from_database(self, table_name: str, server_name: str, target_ip: str, column_name: str, filter_value: str, filter_condition: str, schema_name: str = "public"):
        api_url  = f"{target_ip}/delete"
        response = requests.delete(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            params = {
                "table_id"         : table_name,
                "server_name"      : server_name,
                "schema_name"      : schema_name,
                "column_name"      : column_name, 
                "filter_value"     : filter_value,
                "filter_condition" : filter_condition
            }
        )
        
        return response
