import requests
from typing import List, Tuple
from configs import NewsConfig as config
from apiConnector.models.rawNewsModel import model as rawModel
from apiConnector.models.summarizedNewsModel import model as summarizedModel

class ApiConnector:
    ''' Used for call a New-s summarize API '''
    def __init__(self, token:str = '') -> 'ApiConnector':
        self.__API_URL = config.APIUrl
        self.__SERVICES = {
            "raw" : config.RawNewsServices,
            "summarized" : config.SummarizedNewsServices
        }
        self.__RAW_MODEL = rawModel
        self.__SUMMARIZED_MODEL = summarizedModel
        self.__PASS_STATUS = {200:'OK', 201:'Created', 204:'No content return'}
        self.__point2model = self.__RAW_MODEL
        self.__token = token or config.Token
        self.__headers = {'Content-Type': 'application/json',
                          'Authorization': 'Bearer {}'.format(self.__token)}
    
    @property
    def MODEL_LISTS(self):
        """Show all models available to set
        
        Returns
        -------
        List[str]
            list of available models
        """        
        return ['raw', 'summarized', 'token']

    def setModel(self, model: str) -> 'ApiConnector':
        """Set API payload model
        
        Parameters
        ----------
        model : str
            name of model
        
        Returns
        -------
        ApiConnector
            return self
        
        Raises
        ------
        Exception 'Invalid model name'
            if given model name can't found in list of model names will raise this exception
        """        
        if model not in self.MODEL_LISTS:
            raise Exception('Invalid model name')
        else:
            if model == 'raw':
                self.__point2model = self.__RAW_MODEL
            elif model == 'summarized':
                self.__point2model = self.__SUMMARIZED_MODEL
            return self

    def setToken(self, token: str) -> 'ApiConnector':
        """Set API token
        
        Parameters
        ----------
        token : str
            token to access all summarized news services
        
        Returns
        -------
        ApiConnector
            return self
        """        
        self.__token = token
        self.__headers['Authorization'] = 'Bearer {}'.format(self.__token)
        return self

    def current_model(self) -> str:
        """Show current model
        
        Returns
        -------
        str
            name of model
        """        
        if self.__point2model is self.__SUMMARIZED_MODEL:
            return 'summarized'
        elif self.__point2model is self.__RAW_MODEL:
            return 'raw'
    
    def __verifyParams(self, payload:dict = False, token:bool = False, empty:bool = False) -> None:
        """Verify all parameters that need to send to API service
        
        Parameters
        ----------
        payload : dict, optional
            request body or parameters according to current model, by default False
        token : bool, optional
            flag to indicate the presence of the access token, by default False
        empty : bool, optional
            flag to allow empty payload or not, by default False
        
        Raises
        ------
        Exception 'Missing token'
            if token is empty and not set token parameter to false will raise this exception
        Exception 'Empty payload'
            if payload is empty and not set empty parameter to true will raise this exception
        Exception 'Invalid payload'
            if given payload is not suited with API model will raise this exception
        """        
        if token:
            if self.__token == '':
                raise Exception('Missing token')
        if not isinstance(payload, dict):
            if payload == False:
                return
            if len(payload) == 0 and not empty:
                raise Exception('Empty payload')
        for k in payload.keys():
            if k not in self.__point2model.keys():
                raise Exception('Invalid payload')

    def __returnRes(self, response: requests.models.Response) -> Tuple[int, str]:
        """Return post request to API services according to current model
        
        Parameters
        ----------
        response : requests.models.Response
            response object from API
        
        Returns
        -------
        Tuple[int, str]
            status_code, response_in_json or status_description
        """        
        try:
            res_data = response.json()
        except ValueError as err:
            res_data = response.text
        return response.status_code, res_data

    async def post(self, payload: dict) -> Tuple[int, str]:
        """Send post request to API services according to current model
        
        Parameters
        ----------
        payload : dict
            request object
        
        Returns
        -------
        Tuple[int, str]
            status_code, response_in_json or status_description
        """        
        self.__verifyParams(payload=payload, token=True)
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]
        response = requests.post(reqUrl, json=payload, headers=self.__headers)
        return self.__returnRes(response)
    
    async def get(self, payload:dict) -> Tuple[int, List[dict]]:
        """Send get request to API services according to current model
        
        Parameters
        ----------
        payload : dict
            request parameters
        
        Returns
        -------
        Tuple[int, List[dict]]
            status_code, response_in_json or status_description
        
        Raises
        ------
        Exception 'Model not found'
            raise this exception when can't find suit model for given payload
        """        
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]
        if self.__point2model is self.__SUMMARIZED_MODEL:
            self.__verifyParams(payload=payload, empty=True)
            response = requests.get(reqUrl, params=payload)
        elif self.__point2model is self.__RAW_MODEL:
            self.__verifyParams(token=True, payload=payload, empty=True)
            response = requests.get(reqUrl, params=payload, headers=self.__headers)
        else:
            raise Exception('Model not found')
        return self.__returnRes(response)

    async def put(self, id: str, payload: dict) -> Tuple[int, str]:
        """Send put request to API services according to current model
        
        Parameters
        ----------
        id : str
            mongoDb object id
        payload : dict
            object to be replace
        
        Returns
        -------
        Tuple[int, str]
            status_code, response_in_json or status_description
        """        
        self.__verifyParams(token=True, payload=payload)
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]+'/'+id
        response = requests.put(reqUrl, json=payload, headers=self.__headers)
        return self.__returnRes(response)
    
    async def delete(self, id: str) -> Tuple[int, str]:
        """Send delete request to API services according to current model
        
        Parameters
        ----------
        id : str
            mongoDb object id
        
        Returns
        -------
        Tuple[int, str]
            status_code, response_in_json or status_description
        """        
        self.__verifyParams(token=True)
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]+'/'+id
        response = requests.delete(reqUrl, headers=self.__headers)
        return self.__returnRes(response)