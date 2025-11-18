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

# Konfigurasi keys dari informasi Anda
CONFIG = {
    "API_KEY": "vT8tINqHaOxXbGE7eOWAhA==",
    "EncryptionKey": "880d8e7e9b4b787aa50a3917b09fc0ec",
    "EncryptionKeyAESCustomPrepaidAndPrio": "9fc97ed1-6a30-48d5-9516-60c53ce3a135",
    "EncryptionKeyHmac512": "iBLeja3ryA4SGB6Y2GGVmbMJ3zMeCAih54vWVM7LAfaPct71JThN8LCa5XmMfJ4fHKf0TH0KCMzaS612Pk9ghdZv5P0aX08aatFGPVgFhrTGCKmAPM7ptmZHp5yjpxhA",
    "LiveChatAesEncryptionKey": "C8CA5B0AC44E8F4C554EF6FBF2B92A55",
    "AX_FP_KEY": "18b4d589826af50241177961590e6693"
}

class CryptoUtils:
    @staticmethod
    def calculate_hmac_512(data: str, key: str) -> str:
        """Calculate HMAC SHA512"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')

        h = hmac.new(key, data, hashlib.sha512)
        return h.hexdigest()

# Endpoint-endpoint lain (xdataenc, xdatadec, paysign, dll.) tidak relevan untuk
# alur kerja xl-cli, jadi kita sederhanakan servernya.

@app.route('/paysign', methods=['POST'])
def payment_sign():
    """Endpoint untuk signing payment - dibutuhkan oleh `xl-cli purchase`."""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')

        if not data:
            return jsonify({'status': 'error', 'message': 'Missing request body'}), 400

        if api_key != CONFIG["API_KEY"]:
            return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401

        # Kunci-kunci ini harus cocok dengan yang dikirim oleh xl-cli api.py
        required_keys = ['access_token', 'sig_time_sec', 'package_code', 'token_payment', 'payment_method', 'payment_for', 'path']
        if not all(key in data for key in required_keys):
            return jsonify({'status': 'error', 'message': 'Missing required fields for payment signing'}), 400

        # Generate signature seperti XL
        data_to_sign = f"{data['access_token']}{data['sig_time_sec']}{data['package_code']}{data['token_payment']}{data['payment_method']}{data['payment_for']}{data['path']}"
        x_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["EncryptionKeyHmac512"])

        return jsonify({
            'x_signature': x_signature
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Payment signing failed: {str(e)}'}), 500

@app.route('/ax_sign', methods=['POST'])
def ax_sign():
    """Endpoint untuk AX signature - compatible dengan ax_api_signature"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')

        if not data:
            return jsonify({'status': 'error', 'message': 'Missing request body'}), 400

        if api_key != CONFIG["API_KEY"]:
            return jsonify({'status': 'error', 'message': 'Invalid API key'}), 401

        ts_for_sign = data.get('ts_for_sign')
        contact = data.get('contact')
        code = data.get('code')
        contact_type = data.get('contact_type')

        if not all([ts_for_sign, contact, code, contact_type]):
            return jsonify({'status': 'error', 'message': 'Missing required fields for AX signing'}), 400

        # Generate signature untuk AX
        data_to_sign = f"{ts_for_sign}{contact}{code}{contact_type}"
        ax_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["AX_FP_KEY"])

        return jsonify({
            'ax_signature': ax_signature
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': f'AX signing failed: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'XL Crypto Server (Signature-only)',
        'version': '2.0.0'
    })

if __name__ == '__main__':
    print("XL Signature Server starting...")
    print(f"API Key: {CONFIG['API_KEY']}")
    print("Endpoints available:")
    print("  POST /ax_sign      - AX signature generation for login")
    print("  POST /paysign      - Payment signature generation for purchase")
    print("  GET  /health       - Health check")

    app.run(host='0.0.0.0', port=5000, debug=True)
