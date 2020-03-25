import asyncio
import requests
import json
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
        self.MODEL_LISTS = ['raw', 'summarized', 'token']
        self.__RAW_MODEL = rawModel
        self.__SUMMARIZED_MODEL = summarizedModel
        self.__PASS_STATUS = {200:'OK', 201:'Created', 204:'No content return'}
        self.__point2model = self.__RAW_MODEL
        self.__token = token or config.Token
        self.__headers = {'Content-Type': 'application/json',
                          'Authorization': 'Bearer {}'.format(self.__token)}
    
    def setModel(self, model: str) -> 'ApiConnector':
        """
        Set API payload model
        :param str model: text to identify model
        :return: ApiConnector
        """
        if model not in self.MODEL_LISTS:
            raise Exception('Invalid model, requested model not in {}'.format(self.MODEL_LISTS))
        else:
            if model == 'raw':
                self.__point2model = self.__RAW_MODEL
            elif model == 'summarized':
                self.__point2model = self.__SUMMARIZED_MODEL
            return self

    def setToken(self, token: str) -> 'ApiConnector':
        """
        Set API token
        :param str token: access token for manipulate summarized news database
        :return: ApiConnector
        """
        self.__token = token
        self.__headers['Authorization'] = 'Bearer {}'.format(self.__token)
        return self

    def models(self) -> List[str]:
        """
        Show all models available to set
        :return: list of available models
        """
        return self.MODEL_LISTS 

    def current_model(self) -> str:
        """
        Show current model
        :return: name of model
        """
        if self.__point2model is self.__SUMMARIZED_MODEL:
            return 'summarized'
        elif self.__point2model is self.__RAW_MODEL:
            return 'raw'
    
    def __verifyParams(self, payload:dict = False, token:bool = False, empty:bool = False) -> None:
        """
        Verify all parameters that need to send to API service
        :param dict payload: request body or parametes according to current model
        :param bool token: flag to indicate the presence of the access token
        :param bool empty: flag to allow empty payload or not
        :return: None
        """
        if token:
            if self.__token == '':
                raise Exception('Token missing')
        if not isinstance(payload, dict):
            if payload == False:
                return
            if len(payload) == 0 and not empty:
                raise Exception('payload need to be a non-empty dictionary')
        for k in payload.keys():
            if k not in self.__point2model.keys():
                raise Exception('Invalid payload, the payload is not suited for the model')

    def __returnRes(self, response: requests.models.Response) -> Tuple[int, str]:
        """
        Return the response from API to method caller
        :param Response response: response object from API
        :return: status_code, response_in_json or status_description
        """
        try:
            res_data = response.json()
        except ValueError as err:
            res_data = response.text
        return response.status_code, res_data

    async def post(self, payload: dict) -> Tuple[int, str]:
        """
        Send post request to API services according to current model
        :param dict payload: request object
        :return: status_code, response_in_json or status_description
        """
        self.__verifyParams(payload=payload, token=True)
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]
        response = requests.post(reqUrl, json=payload, headers=self.__headers)
        return self.__returnRes(response)
    
    async def get(self, payload) -> Tuple[int, List[dict]]:
        """
        Send get request to API services according to current model
        :param dict payload: request parameters
        :return: status_code, response_in_json or status_description
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
        """
        Send put request to API services according to current model
        :param str id: mongoDb object id
        :param dict payload: object to be replace
        :return: status_code, response_in_json or status_description
        """
        self.__verifyParams(token=True, payload=payload)
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]+'/'+id
        response = requests.put(reqUrl, json=payload, headers=self.__headers)
        return self.__returnRes(response)
    
    async def delete(self, id: str) -> Tuple[int, str]:
        """
        Send delete request to API services according to current model
        :param str id: mongoDb object id
        :return: status_code, response_in_json or status_description
        """
        self.__verifyParams(token=True)
        reqUrl = self.__API_URL+self.__SERVICES[self.current_model()]+'/'+id
        response = requests.delete(reqUrl, headers=self.__headers)
        return self.__returnRes(response)