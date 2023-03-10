#loading dependencies
import webbrowser
import requests



class TradeStationClient(object):

    def __init__(
        self, 
        username: str, 
        client_id: str, 
        client_secret: str, 
        scope: list | str = 'openid', 
        state: str = None,
        auth_manual : bool = True
    ) -> None:


        self.CONFIG_ = {
            #known parameters
            'base' : 'https://api.tradestation.com',
            'paper_base': 'https://sim-api.tradestation.com',
            'api_version' : 'v3',
            'paper_api_version' : 'v3',
            'auth_endpoint' : 'https://signin.tradestation.com/authorize',
            'token_endpoint' : 'https://signin.tradestation.com/oauth/token',
            'token_header' : {'content-type': 'application/x-www-form-urlencoded'},
            'response_type' : 'code',
            'grant_type' : 'authorization_code',


            #instance defined parameters
            'client_id': client_id,
            'username': username,
            'client_secret' : client_secret,
            'redirect_uri' : 'http://localhost:8080',
            'scope' : scope,
            'state' : state,
            'auth_manual' : auth_manual
        }

    def _build_auth_url(self) -> str:
        '''
        Function builds autoriztion URL

        Returns:
        ----
        (str): string representation of authorization url
        '''
        params = '?response_type=' + self.CONFIG_['response_type'] + '&client_id=' + \
                self.CONFIG_['client_id'] + '&redirect_uri=' + self.CONFIG_['redirect_uri'] + \
                '&audience=' + self.CONFIG_['base'] + '&scope=' + self.CONFIG_['scope'] 
        
        #adding state param if neeeded
        if self.CONFIG_['state']:
            params = params + '&state=' + self.CONFIG_['state']
        auth_url = self.CONFIG_['auth_endpoint'] + params

        return auth_url

    def _authorize_manual(self) -> str:
        '''
        Authorizes session for Client by manual process. User must login into brower and grab auth code from 
        redirect_uri = http://localhost:8080/?code=<AUTHORIZATION_CODE>&state=fhx8y3lfchqxcb8q

        Returns:
        -----
        (str): manual user input of authorization code
        '''

        auth_url = self._build_auth_url()
        webbrowser.open_new(auth_url)

        return input('Please enter the authorization code from the url: ')
    
    def _authorize_auto(self) -> None:
        #TODO: build automatic process for grabbing auth code
        pass

    def _get_access_token(self) -> dict:
        '''
        Taking the authorization code and using it to retieve access token.
        NOTE: access tokens expire every 20 mins. 

        Returns:
        -----
        (dict) : Post response from authorization code containing access token
        '''
        
        if self.CONFIG_['auth_manual']:
            auth_code = self._authorize_manual()
        else:
            auth_code = self._authorize_auto()

        #create data dict for post request
        data = {'code' : auth_code}
        for key in ['grant_type', 'client_id', 'client_secret', 'redirect_uri']:
            data[key] = self.CONFIG_[key]

        #sending request to TS for access key
        req = requests.post(
            url = self.CONFIG_['token_endpoint'],
            headers = self.CONFIG_['token_header'],
            data = data
        )
        
        if req.status_code != 200: 
            print('-'*80)
            print(f'Access Token Retrieval Unsuccessful: {req} \n \n')
        else:
            print(req.json())
            return req.json


