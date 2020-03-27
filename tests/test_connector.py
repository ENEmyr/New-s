#from apiConnector import *
import unittest
from apiConnector.ApiConnector import ApiConnector
import asyncio 
import json

def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

class TestApiConnector(unittest.TestCase):
    ''' Unit test for ApiConnector class '''
    def __init__(self, methodName):
        super().__init__(methodName)
        self.data = {
            "title":"News4",
            "content":"This is a contents",
            "sourceUrl":"https://aichanserv.com",
            "imageUrl":"https://aichanserv.com/image.jpg",
            "author":"ENEmy",
            "publisher":"Aichanserv",
            "category":"Politic",
            "tags":["Prayut"],
            "language":["th"],
            "publishAt":"2020-03-24T09:39:50.001Z"
        }
        self.pass_status = [200, 201, 204]

    @async_test
    async def test_get(self):
        connector = ApiConnector()
        connector = connector.setModel(model='summarized')
        status_code, res = await connector.get({'limit':1})
        self.assertIn(status_code, self.pass_status, 'Unexpected html status code')
        if len(res) != 0:
            self.assertIsInstance(res[0], dict, 'Unexpected response data from summarized Api')
            #json_formatted = json.dumps(res, indent=2)
            #print(json_formatted)

if __name__ == "__main__":
    unittest.main()

#async def doAwait():
#    data = {
#        "title":"News4",
#        "content":"This is a contents",
#        "sourceUrl":"https://aichanserv.com",
#        "imageUrl":"https://aichanserv.com/image.jpg",
#        "author":"ENEmy",
#        "publisher":"Aichanserv",
#        "category":"Politic",
#        "tags":["Prayut"],
#        "language":["th"],
#        "publishAt":"2020-03-24T09:39:50.001Z"
#    }
#    connector = ApiConnector()
#    connector = connector.setModel(model='summarized')
#    print(connector.current_model())
#    #status_code, res = await connector.post(data)
#    #status_code, res = await connector.put(id='5e7accab280d5a4b28f62bfd', payload=data)
#    #status_code, res = await connector.delete(id='5e7accab280d5a4b28f62bfd')
#    status_code, res = await connector.get({'limit':1})
#    print("Return status: {}".format(status_code))
#    if len(res) != 0:
#        json_formatted = json.dumps(res, indent=2)
#        print(json_formatted)
#        print(len(res))
#
#if __name__ == '__main__':
#    #print(thai_stopwords())
#    asyncio.run(doAwait())