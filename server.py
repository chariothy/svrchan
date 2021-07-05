from http.server import HTTPServer, BaseHTTPRequestHandler
from fastapi import FastAPI, Request
import json
import os
from urllib.parse import parse_qs, urlsplit

from trans import transition
from utils import su
from case import case_dict

app = FastAPI()
ENV = os.environ.get('ENV', 'prod')


def trans(title: str, content: str):
    #print(title, content)
    try:
        transition(title, content)
    except Exception as ex:
        su.ex(f'转换ServerChan消息出错：{ex}')
        su.info(f'Failed to parse: \n>>> title={title} \n>>> content={content}\n')
        

@app.post('/send')
async def do_POST(req: Request):
    r"""  post json """
    body = await req.body()
    body = body.decode('utf-8')
    #print(body)
    payload = parse_qs(body)
    #print(payload)
    trans(payload['title'][0], payload['content'][0])


if __name__ == "__main__":
    import uvicorn, os
    print(f'Listening ++++++ ENV={ENV} ++++++')
    reload = os.environ.get('UVICORN_ENV') != 'prod'
    uvicorn.run("server:app", host="0.0.0.0", port=8822, reload=reload)