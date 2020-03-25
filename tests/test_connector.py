from pythainlp.corpus.common import thai_stopwords
from apiConnector.ApiConnector import ApiConnector
import asyncio
import json

async def doAwait():
    data = {
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
    connector = ApiConnector()
    connector = connector.setModel(model='summarized')
    print(connector.current_model())
    #status_code, res = await connector.post(data)
    #status_code, res = await connector.put(id='5e7accab280d5a4b28f62bfd', payload=data)
    status_code, res = await connector.delete(id='5e7accab280d5a4b28f62bfd')
    print("Return status: {}".format(status_code))
    if status_code == 204:
        status_code, res = await connector.get({'limit':1})
    else:
        return
    if len(res) != 0:
        json_formatted = json.dumps(res, indent=2)
        print(json_formatted)
        print(len(res))

if __name__ == '__main__':
    #print(thai_stopwords())
    asyncio.run(doAwait())