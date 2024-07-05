"""
1. `ClientSideInterface` 클래스의 인스턴스 생성
2. `login_to_server` 메서드를 사용하여 서버에 로그인
3. 데이터를 데이터베이스에 업로드하려면 `upload_to_database` 
4. 데이터베이스에서 데이터를 쿼리하려면 `query_database` 
"""
import os, base64, requests

import pandas as pd 

from config.DBInterfacePostgres import DBInterface

class ClientSideInterface:
    def login_to_server(self, username: str, password: str, target_ip: str):
        """
        서버에 로그인
            - username   : 사용자 이름
            - password   : 비밀번호
            - target_ip  : 타겟 서버의 IP 주소
            - 반환값      : 로그인 성공 여부 메시지
        """
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

    def upload_to_database(self, table_name: str, server_name: str, target_ip: str, data_to_upload: pd.DataFrame, schema_name: str = "public"):
        """
        데이터를 데이터베이스에 업로드하는 함수.
            - table_name: 테이블 이름
            - server_name: 서버 이름
            - target_ip: 타겟 서버의 IP 주소
            - data_to_upload: 업로드할 데이터프레임
            - schema_name: 스키마 이름 (기본값: "public")
            - 반환값: 업로드 상태 메시지
        """
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
        """
        데이터베이스에서 데이터를 쿼리함.
            - table_name: 테이블 이름
            - server_name: 서버 이름
            - target_ip: 타겟 서버의 IP 주소
            - columns_list: 조회할 컬럼 리스트
            - filter_value: 필터 조건 (옵션)
            - schema_name: 스키마 이름 (기본값: "public")
            - 반환값: 쿼리 결과

        메서드에서 반환된 "response" 객체의 .json()을 pd.DataFrame()으로 감싸면 데이터프레임으로 변환됨 -> 하단 if-else 문 참조
        """
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
    
if (__name__ == "__main__"):
    client_interface = ClientSideInterface()
    database_object  = DBInterface()
    dataframe        = pd.read_excel(r"C:\Users\User\015.Amore_Pacific\src\BY24 소셜버즈 데이터_취합본.xlsx")
    client_interface.login_to_server("taeheon.park@samsung.com", "test_password_1", "http://172.21.121.117:5001")
    # client_interface.upload_to_database("001_BY24_BUZZ_DATA", "MT2_Datalake", "http://172.21.121.117:5001", dataframe, "AP_PHASE_01")
    get_data = client_interface.query_database("001_BY24_BUZZ_DATA", "MT2_Datalake", "http://172.21.121.117:5001", ["*"], filter_value = '"Brand" = \'설화수\'', schema_name = "AP_PHASE_01")
    pd.DataFrame(get_data.json())
