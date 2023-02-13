#loading dependencies
import requests
import webbrowser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By




from config import CHROME_DRIVER_PATH
import time

class TradeStationClient(object):
    '''
    TradeStationClient class is to be used with the tradestation api. 
    '''

    def __init__(
        self, 
        username: str, 
        password: str,
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
            'token_header' : {'content-type':'application/x-www-form-urlencoded'},
            'response_type' : 'code',
            'grant_type' : 'authorization_code',


            #instance defined parameters
            'client_id': client_id,
            'username': username,
            'password':password,
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
        Authorizes session for Client by manual process. User must login into 
        browser and grab auth code from redirect_uri 
        ie: http://localhost:8080/?code=<AUTHORIZATION_CODE>&state=fhx8y3lfchqxcb8q

        Returns:
        -----
        (str): manual user input of authorization code
        '''

        auth_url = self._build_auth_url()
        webbrowser.open_new(auth_url)

        return input('Please enter the authorization code from the url: ')

    def _get_auth_code_input(self) -> str:
        '''
        Function to get manual input of MFA auth code from SMS message
        
        Returns:
        -----
        (str): string representing the auth_code
        '''
        code =  input('Enter 2FA code from text message: ')
        return code

    
    def _authorize_auto(self) -> str:
        '''
        Function to automate parsing through the entire autothentication process.
        This process uses chrome driver which needs to be synced with your 
        chrome version. In addition <add something about 2FA when that part is 
        completed>

        Returns:
        -----
        (str): authentication code form ts login redirect
        '''

        #setting driver options and setting url connection
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        #chrome_options.headless = True #this keeps a browser from opening
        chrome_options.add_argument("--log-level=3") #keeps output from webdriver quiet
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=chrome_options)
        driver.get(self._build_auth_url())
        time.sleep(1)

        #inputting credentials
        for elem in ['username', 'password']:
            driver.find_element(By.ID, elem).send_keys(self.CONFIG_[elem])
        driver.find_element(By.ID, 'btn-login').click()
        time.sleep(1)

        #checking if needing to MFA for account (current only trust device for 30 days)
        if 'mfa-sms-challenge' in driver.current_url:
            #TODO: make SMS otp_code input automatic.... maybe twilio integration???
            #keeps trusted device for 30 days
            driver.find_element(
                By.XPATH, 
                ".//*[contains(text(), 'Remember this device for 30 days')]").click() 
            otp_code = self._get_auth_code_input()
            driver.find_element(By.ID, 'code').send_keys(otp_code)
            time.sleep(0.5)
            driver.find_element(By.NAME, 'action').click()
            time.sleep(2)

        #grabbing auth_code from current_url
        url = driver.current_url
        driver.close()
        auth_code = url.split('code=')[-1].split('&state')[0]        
       
        return auth_code


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


