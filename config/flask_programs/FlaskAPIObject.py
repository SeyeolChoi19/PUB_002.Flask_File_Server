import ipaddress, os

from flask_jwt_extended                              import JWTManager 
from config.miscellaneous.GenerateSecretKey          import SECRET_KEY
from config.database_operations.retrieve_user_info   import retrieve_api_user_info
from config.database_operations.DBInterfacePostgres  import DBInterface
from config.miscellaneous.EnvironmentVariables       import ALLOWED_IP_ADDRESSES
from flask                                           import Flask, request, abort

def filter_ip_addresses():
    allowed_ip_addresses_list = ipaddress.ip_network(os.getenv(ALLOWED_IP_ADDRESSES))
    request_client_ip_address = ipaddress.ip_address(request.remote_addr)

    if (request_client_ip_address not in allowed_ip_addresses_list):
        abort(403)

flask_file_server_user_database        = retrieve_api_user_info("file_server")
personal_database_interface_object     = DBInterface()
flask_file_server_interface            = Flask(__name__)
json_web_token_instance                = JWTManager(flask_file_server_interface)
flask_file_server_interface.secret_key = SECRET_KEY
flask_file_server_interface.debug      = True
flask_file_server_interface.before_request(filter_ip_addresses)
