import os 

import datetime as dt 
import pandas   as pd 

from config.flask_programs.FlaskAPIObject      import marketing_team_two_database_object
from config.miscellaneous.EnvironmentVariables import ADMIN_NAME, ADMIN_PWD, SERVER_NAME, ACTIVITY_LOG

def log_database_usage(usage_log: str, api_endpoint: str, source_ip: str):
    usage_data = pd.DataFrame({"activity_date_time" : [str(dt.datetime.now())], "usage_log" : [usage_log], "api_endpoint" : [api_endpoint], "source_ip" : [source_ip]})
    marketing_team_two_database_object.connection_settings("postgresql", ADMIN_NAME, ADMIN_PWD, "localhost", os.getenv(SERVER_NAME))
    marketing_team_two_database_object.upload_to_database(os.getenv(ACTIVITY_LOG), usage_data)
