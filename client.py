#loading dependencies
import webbrowser



class TradeStationClient(object):

    def __init__(self, username: str, client_id: str, client_secret: str, scope: list = None, state: str = None) -> None:
        self.CONFIG_ = {
            #known parameters
            'base' : 'https://api.tradestation.com',
            'paper_base': 'https://sim-api.tradestation.com',
            'api_version' : 'v3',
            'paper_api_version' : 'v3',
            'auth_endpoint' : 'https://signin.tradestation.com/authorize',
            'response_type' : 'code',
            'token_endpoint' : 'https://signin.tradestation.com/oauth/token',

            #instance defined parameters
            'client_id': client_id,
            'username': username,
            'client_secret' : client_secret,
            'redirect_uri' : 'http://localhost:8080',
            'scope' : 'openid ' + ' '.join(scope) if scope else 'openid',
            'state' : state
        }

    def _build_auth_url(self) -> None:
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


    def _auth_code_manual(self) -> None:
        '''
        Authorizes session for Client by manual process. User must login into brower and grab auth code from 
        redirect. Redirect uri = http://localhost:8080/?code=<AUTHORIZATION_CODE>&state=fhx8y3lfchqxcb8q

        Returns:
        -----
        (str): manual user input of authorization code
        '''

        auth_url = self._build_auth_url()
        webbrowser.open_new(auth_url)

        return input('Please enter the authorization code from the url: ')
    
    def _auth_code_auto(self) -> None:
        '''
        TODO: build automatic process for grabbing auth code
        '''

    def _get_access_token(self) -> None:
        '''
        Taking the authorization code and using it to retieve access token
        '''


