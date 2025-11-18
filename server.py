from flask import Flask, request, jsonify
import hashlib
import hmac
import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os
from datetime import datetime, timezone, timedelta
import uuid

app = Flask(__name__)

# Konfigurasi kunci lengkap
CONFIG = {
    "API_KEY": "vT8tINqHaOxXbGE7eOWAhA==",
    "EncryptionKey": "880d8e7e9b4b787aa50a3917b09fc0ec",
    "EncryptionKeyHmac512": "iBLeja3ryA4SGB6Y2GGVmbMJ3zMeCAih54vWVM7LAfaPct71JThN8LCa5XmMfJ4fHKf0TH0KCMzaS612Pk9ghdZv5P0aX08aatFGPVgFhrTGCKmAPM7ptmZHp5yjpxhA",
    "AX_FP_KEY": "18b4d589826af50241177961590e6693"
}

class CryptoUtils:
    @staticmethod
    def encrypt_aes_cbc(data: str, key_hex: str) -> str:
        key = bytes.fromhex(key_hex)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted).decode('utf-8')

    @staticmethod
    def decrypt_aes_cbc(encrypted_data: str, key_hex: str) -> str:
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]
        cipher = AES.new(bytes.fromhex(key_hex), AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(ciphertext)
        return unpad(decrypted, AES.block_size).decode('utf-8')

    @staticmethod
    def calculate_hmac_512(data: str, key: str) -> str:
        h = hmac.new(key.encode('utf-8'), data.encode('utf-8'), hashlib.sha512)
        return h.hexdigest()

@app.route('/xdataenc', methods=['POST'])
def xdata_encrypt_sign():
    data = request.get_json()
    body_json = json.dumps(data.get('body', {}), separators=(',', ':'))
    encrypted_data = CryptoUtils.encrypt_aes_cbc(body_json, CONFIG["EncryptionKey"])
    xtime = int(datetime.now().timestamp() * 1000)
    return jsonify({'encrypted_body': {'xdata': encrypted_data, 'xtime': xtime}})

@app.route('/xdatadec', methods=['POST'])
def xdata_decrypt():
    data = request.get_json()
    decrypted_data = CryptoUtils.decrypt_aes_cbc(data['xdata'], CONFIG["EncryptionKey"])
    return jsonify({'plaintext': json.loads(decrypted_data)})

@app.route('/paysign', methods=['POST'])
def payment_sign():
    data = request.get_json()
    data_to_sign = f"{data['access_token']}{data['sig_time_sec']}{data['package_code']}{data['token_payment']}{data['payment_method']}{data['payment_for']}{data['path']}"
    x_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["EncryptionKeyHmac512"])
    return jsonify({'x_signature': x_signature})

@app.route('/ax_sign', methods=['POST'])
def ax_sign():
    data = request.get_json()
    data_to_sign = f"{data['ts_for_sign']}{data['contact']}{data['code']}{data['contact_type']}"
    ax_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["AX_FP_KEY"])
    return jsonify({'ax_signature': ax_signature})

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    print("XL Full Crypto Server starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)
