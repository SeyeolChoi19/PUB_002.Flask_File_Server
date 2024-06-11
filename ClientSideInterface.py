import os, base64, requests 

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

    def upload_file_to_server(self, file_name: str, local_directory: str, server_directory: str, target_ip: str):
        with open(os.path.join(local_directory, file_name), "rb") as file_object:
            file_object_base64 = base64.b64encode(file_object.read()).decode()

        api_url  = f"{target_ip}/save_file"
        response = requests.post(
            api_url, 
            headers = {
                "Authorization" : f"Bearer {self.jwt_token}"
            },
            data    = {
                "file_name"        : file_name, 
                "server_directory" : server_directory,
                "transferred_file" : file_object_base64
            }
        )

        return response.json()["status"]

    def retrieve_file_from_server(self, file_name: str, server_directory: str, destination_folder: str, target_ip: str):
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

    def search_file_server(self, file_name: str, file_directory: str, target_ip: str):
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

    def delete_from_server(self, file_name: str, file_directory: str, target_ip: str):
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

if (__name__ == "__main__"):
    client_interface = ClientSideInterface()
    client_interface.login_to_server()
    client_interface.retrieve_file_from_server("TEST_FILE.txt", "test_environment", "test_environment", "")
    client_interface.upload_file_to_server("TEST_FILE.txt", "test_environment", "test_environment", "")
