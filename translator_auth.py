import urllib
import json
import requests
URL = 'https://datamarket.accesscontrol.windows.net/v2/OAuth2-13'
SCOPE = 'http://api.microsofttranslator.com'
GRANT_TYPE = 'client_credentials'

class OAuth(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_token(self):
        request_args = {
            'client_id' : self.client_id,
            'client_secret' : self.client_secret,
            'scope': SCOPE,
            'grant_type': GRANT_TYPE
        }

        self.response = requests.post(URL, data=urllib.urlencode(request_args))
        self.response.raise_for_status()
        data = json.loads(self.response.content)
        return data['access_token']
    
