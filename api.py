import requests
import logging
import json
import time


class MPCoreAPI(object):
    def __init__(self, host, client_secret, login, password, api_port, front_port,pdql_query,asset_groups):
        requests.packages.urllib3.disable_warnings()
        self.logger = logging.getLogger("[core.api]")
        self.host = host
        self.login = login
        self.client_secret = client_secret
        self.password = password
        self.api_port = api_port
        self.front_port = front_port
        self.pdql_query = pdql_query
        self.asset_groups = asset_groups
        self.access_token = None
        self.auth_header = None
        self.time_wait = 5

    # Connect to MP API
    def connect(self):
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {"grant_type": "password", "client_id": "mpx", "client_secret": self.client_secret,
                    "scope": "authorization offline_access mpx.api", "response_type": "code id_token token",
                    "username": self.login, "password": self.password}
            data_masked = {"grant_type": "password", "client_id": "mpx", "client_secret": "*******",
                           "scope": "authorization offline_access mpx.api",
                           "response_type": "code id_token token", "username": self.login, "password": "*******"}
            url = "https://" + self.host + ":" + self.api_port + "/connect/token"
            print("Trying to connect API endpoint '" + url + "' with data '" + str(data_masked) + "'")
            self.logger.debug("Connect to API endpoint: " + url + "' with data '" + str(data_masked) + "'")
            r = requests.post(url, data=data, headers=headers, verify=False)
            logging.debug("Result status: " + str(r.status_code))
            print(r.status_code)
            if r.status_code != 200:
                self.logger.debug(str(r.__dict__))
            self.access_token = r.json()["access_token"]
            self.auth_header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.access_token}

            print("Got access token")
            self.logger.debug("Got access token")
            return True
        except:
            self.logger.error("API request to " + url + " failed", exc_info=False)
            self.logger.debug("Error info: ", exc_info=True)
            print("API endpoint connection failed.")
            return False

    # Get data
    def get_data(self):
        base_url = "https://" + self.host + ":" + str(self.front_port) + "/api/assets_temporal_readmodel/v1/assets_grid"
        data = {"pdql": self.pdql_query, "includeNestedGroups": "true", "utcOffset": "+03:00", "selectedGroupIds":self.asset_groups}
        
        # Trying to run PDQL and get token
        print("Trying to run PDQL query.")
        try:
            self.logger.debug("Connect to API endpoint: " + base_url + "' with data '" + str(json.dumps(data)) + "'")
            response = requests.post(base_url, headers=self.auth_header, verify=False, data=json.dumps(data))
            print(response.status_code)
            if response.status_code != 200:
                self.logger.debug(str(response.__dict__))
            token = response.json()["token"]
        except:
            self.logger.error("API request to " + base_url + " failed", exc_info=False)
            self.logger.debug("Error info: ", exc_info=True)
            print("Get PDQL query token failed.")
            return
        time.sleep(self.time_wait)
        # Trying to get result
        response = requests.get(base_url + "/export?pdqlToken=" + token, headers=self.auth_header, verify=False)
        if response.status_code == 404:
            print("Failed to get results. Increase wait time by 5 sec.")
            self.time_wait += 5
            result = self.get_data()
            return result
        print("Got result. Raw response text length: " + str(len(response.text)))
        return response.text
