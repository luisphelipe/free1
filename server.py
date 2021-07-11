from flask import Flask, request, send_from_directory
from flask_cors import CORS, cross_origin
import json

from hashlib import md5
from base64 import b64decode
from base64 import b64encode

from Crypto.Cipher import AES, Salsa20
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

app = Flask(__name__)
cors = CORS(app)


@app.route('/')
def index():
    return send_from_directory('public', 'index.html')


class AESCipher:
    def __init__(self, key):
        self.key = md5(key.encode('utf8')).digest()

    def encrypt(self, data):
        iv = get_random_bytes(AES.block_size)
        self.cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + self.cipher.encrypt(pad(data.encode('utf-8'),
                                                      AES.block_size)))

    def decrypt(self, data):
        raw = b64decode(data)
        self.cipher = AES.new(self.key, AES.MODE_CBC, raw[:AES.block_size])
        return unpad(self.cipher.decrypt(raw[AES.block_size:]), AES.block_size)


@app.route('/generate-url-aes', methods=['POST'])
def generate_url():
    secret = "ULTRA_SECRET"
    message = request.data.decode('utf-8')
    phash = AESCipher(secret).encrypt(message).decode('utf-8')
    return f'https://www.google.com/search?q={phash}'


@app.route('/generate-url-salsa', methods=['POST'])
def generate_url_salsa20():
    message = request.data
    secret = b'*Thirty-two byte (256 bits) key*'
    cipher = Salsa20.new(key=secret)
    phash = cipher.nonce + cipher.encrypt(message)
    phash = b64encode(phash).decode('utf-8')
    return f'https://www.google.com/search?q={phash}'


@app.route('/generate-url-base', methods=['POST'])
def generate_url_base():
    message = request.data
    phash = b64encode(message).decode('utf-8')
    return f'https://www.google.com/search?q={phash}'
