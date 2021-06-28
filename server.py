from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from urllib.parse import parse_qs, urlsplit


from trans import transition
from utils import su
from case import case_dict

ENV = os.environ.get('ENV', 'prod')

class EchoHTTPHandler(BaseHTTPRequestHandler):
  def do_GET(self):
        r""" 响应 get 请求，打印 http 头，并返回给 http 客户端 """
        print('%s - %s - %s' % (self.client_address, self.request_version, self.path))
        print('### request headers ###')
        req_head = str(self.headers)
        print('req_head: %s' % req_head)
        for line in req_head.split('\n'):
            line = line.strip()
            print(line)
        self.send_response(200)
        self.end_headers()

        text = '%s - %s - %s\n---\n%s' % (self.client_address, 
                                            self.request_version, 
                                            self.path, 
                                            req_head)
        text = text.encode('utf8')
        self.wfile.write(text)
        
        
  def do_POST(self):
      r"""  post json """
      print('%s - %s - %s' % (self.client_address, self.request_version, self.path))
      # POST 有 Content-Length，GET 无 Content-Length
      content_len = int(self.headers['Content-Length'])   
      post_body = self.rfile.read(content_len)

      try:
        parsed_path = urlsplit(self.path)
        self.send_response(200)
        self.end_headers()

        # 目前仅支持pushplus，其它的因为使用https，容易产生400错误
        # 在微信推送界面上，需要将pushplus与微信推送的token都填上
        # 因为源码中：
        # [ ! -z "$pushplus_token" ] && [ -z "$sckey" ] && str_tab=""
        # 这样会导致tab被去掉而影响正则解析
        params = dict(parse_qs(parsed_path.query))
        #print(params)
        
        parsed_body = post_body.decode('utf-8')
        #print(parsed_body, self.headers, '' )
        
        if ENV == 'debug' or ENV == 'dev':
            parsed_body = case_dict[self.path.strip('/')]
            
        data = parse_qs(parsed_body)
        if 'title' not in data or 'content' not in data:
            return
        title = data['title'][0]
        content = data['content'][0]
        transition(title, content)
      except Exception as ex:
          su.ex(f'转换ServerChan消息出错：{ex}')
          su.info('Failed to parse body: \n\n' + parsed_body)
          
      self.wfile.write(json.dumps({
          'method': self.command,
          'path': self.path,
          'real_path': parsed_path.query,
          'query': parsed_path.query,
          'request_version': self.request_version,
          'protocol_version': self.protocol_version,
          'body': title
      }, ensure_ascii=False).encode('utf8'))
        
        
if __name__ == '__main__':
    ip = '0.0.0.0'
    port = 80
    print('Listening %s:%d, ++++++ ENV=%s ++++++' % (ip, port, ENV))
    server = HTTPServer((ip, port), EchoHTTPHandler)
    server.serve_forever()
