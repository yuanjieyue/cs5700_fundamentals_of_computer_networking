# WEB API SERVER
# Author: Yuanjie Yue
# Date: 10/16/2019

import http
import utils
import config
import pymemcache
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

########################################################################
#                   Memcache KEY - VALUE Design                        #
#    1. Each API                                                       #
#           key:   api itself                                          #
#           val:   a list of datetime joined by ',' as a string        #
#       Example                                                        #
#           key:   '/api/gettime'                                      #
#           val:   '16/10/2019 20:50:47,16/10/2019 20:50:47'           #
#    2. Last Ten Expressions:                                          # 
#           key:   'last_ten_exprs'                                    #
#           value: a list of expressions joined by ',' as a string     #
#                  (the number of expressions are no more than 10)     #
#       Example                                                        #
#           key:   'last_ten_exprs'                                    #
#           val:   '1,1+1,-2,-2+3'                                     #
########################################################################

cache = pymemcache.client.base.Client((config.CACHE_SERVER, config.CACHE_PORT))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle GET request of different URL path
        self.print_header_line()
        if self.path == '/api/gettime':
            utils.update_api_count(cache, '/api/gettime')
            curr_time = utils.get_time().encode()
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('Content-Length', str(len(curr_time)))
            self.end_headers()       
            print('Server send:', curr_time)     
            self.wfile.write(curr_time)
        elif self.path == '/status.html':
            resp_html = utils.get_status(cache).encode()
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.send_header('Content-Length', str(len(resp_html)))
            self.end_headers()
            # Send the html message
            print('Server send:', resp_html)
            self.wfile.write(resp_html)
        else:  
            self.send_response(404)
            self.end_headers()
        self.print_footer_line()
        return

    def do_POST(self):
        # Handle POST request of different URL path
        self.print_header_line()
        if self.path == '/api/evalexpression':
            utils.update_api_count(cache, '/api/evalexpression')
            content_length = int(self.headers['Content-Length'])
            # read data from the client based on the Content-Length
            body = utils.io_read_n_bytes(self.rfile, content_length)
            print('Server recv:', body)
            utils.update_last_ten_expressions(cache, 'last_ten_exprs', body.decode())
            # set up a tcp connection with EXPRESSION EVAL SERVER
            resp = utils.connect_server(config.EXPRESSION_EVAL_SERVER, config.EXPRESSION_EVAL_PORT, body)
            if not resp:
                self.send_response(400)
                self.end_headers()
            else:
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.send_header('Content-Length', str(len(resp)))
                self.end_headers()
                print('Server send:', resp)
                self.wfile.write(resp)
        else:
            self.send_response(404)
            self.end_headers()
        self.print_footer_line()
        return

    def print_header_line(self):
        print('+----------------------------------+')
        print('Server connected by client at:', self.client_address)
        print('Request line:', self.requestline)

    def print_footer_line(self):
        print('+----------------------------------+')

def run(server_class=ThreadingHTTPServer, handler_class=Handler):
    server_address = (config.WEB_API_SERVER, config.WEB_API_PORT)
    httpd = server_class(server_address, handler_class)
    print('Web_API_Server started. Waiting for connnection...')
    httpd.serve_forever()
run()






