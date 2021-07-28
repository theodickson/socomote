import json
import logging
import os
import socket
import threading
from email.header import Header
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote, unquote

import requests
from stringcase import snakecase

from socomote.settings import MP3_LIB

START_PORT = 9001
END_PORT = 9999

logger = logging.getLogger('tts_server')

class TTSRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            filename = unquote(self.path[1:])
            file = self._get_mp3_file(filename)
            with file.open('rb') as file:
                encoded_basename = Header(self.path).encode()
                stat = os.fstat(file.fileno())
                self.send_response(200)
                self.send_header('Content-Length', str(stat[6]))
                self.send_header(
                    'Content-Type',
                    'audio/mpeg')
                self.send_header(
                    'Content-Disposition',
                    'attachment; filename="%s"' % encoded_basename)
                self.end_headers()
                self.wfile.write(file.read())
        except socket.error as error:
            print('Connection is closed by peer')
            pass
        except IOError as error:
            self.send_response(500)
            print('I/O error: %s' % (str(error)))
        return

    def _get_mp3_file(self, filename):
        file = MP3_LIB / filename
        if not file.exists():
            text = filename.replace('mp3', '')
            gen = f"https://freetts.com/Home/PlayAudio?Language=en-GB&Voice=en-GB-Standard-C&TextMessage={quote(text)}&type=0"
            resp = requests.get(gen)
            data = json.loads(resp.text)
            mp3_id = data['id']
            download = f"https://freetts.com/audio/{mp3_id}"
            resp = requests.get(download)
            with file.open("wb") as f:
                f.write(resp.content)
        return file


class TTSServer(HTTPServer):

    def __init__(self):
        self.ip_addr = self._detect_ip_addr()
        self.port = self._find_free_port()
        super().__init__((self.ip_addr, self.port), TTSRequestHandler)
        self._thread = threading.Thread(target=self.serve_forever, daemon=True)

    def __enter__(self):
        super().__enter__()
        self._thread.start()
        return self

    def get_uri(self, text: str):
        return f"http://{self.ip_addr}:{self.port}/{quote(text)}.mp3"

    def _is_port_in_use(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def _find_free_port(self):
        for port in range(START_PORT, END_PORT):
            if not self._is_port_in_use(port):
                return port
        raise Exception('Cannot find a free port to use')

    def _detect_ip_addr(self, ):
        """Return the local ip-address"""
        # Rather hackish way to get the local ip-address, recipy from
        # https://stackoverflow.com/a/166589
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
