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
    "AX_FP_KEY": "iBLeja3ryA4SGB6Y2GGVmbMJ3zMeCAih54vWVM7LAfaPct71JThN8LCa5XmMfJ4fHKf0TH0KCMzaS612Pk9ghdZv5P0aX08aatFGPVgFhrTGCKmAPM7ptmZHp5yjpxhA"
}

class CryptoUtils:
    @staticmethod
    def encrypt_aes_cbc(data: str, key_hex: str) -> str:
        """Encrypt AES CBC seperti di build_encrypted_field"""
        key = bytes.fromhex(key_hex)
        iv = get_random_bytes(16)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        
        # Gabungkan IV + encrypted data
        result = iv + encrypted
        return base64.b64encode(result).decode('utf-8')

    @staticmethod
    def decrypt_aes_cbc(encrypted_data: str, key_hex: str) -> str:
        """Decrypt AES CBC"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # Extract IV (16 byte pertama) dan ciphertext
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            cipher = AES.new(bytes.fromhex(key_hex), AES.MODE_CBC, iv)
            decrypted = cipher.decrypt(ciphertext)
            unpadded = unpad(decrypted, AES.block_size)
            
            return unpadded.decode('utf-8')
        except Exception as e:
            raise Exception(f"Decryption failed: {str(e)}")

    @staticmethod
    def calculate_hmac_512(data: str, key: str) -> str:
        """Calculate HMAC SHA512"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        if isinstance(key, str):
            key = key.encode('utf-8')
        
        h = hmac.new(key, data, hashlib.sha512)
        return h.hexdigest()

    @staticmethod
    def java_like_timestamp(now: datetime) -> str:
        """Generate timestamp seperti java_like_timestamp"""
        ms2 = f"{int(now.microsecond / 10000):02d}"
        tz = now.strftime("%z")
        tz_colon = tz[:-2] + ":" + tz[-2:] if tz else "+00:00"
        return now.strftime(f"%Y-%m-%dT%H:%M:%S.{ms2}") + tz_colon

    @staticmethod
    def ts_gmt7_without_colon(dt: datetime) -> str:
        """Generate timestamp GMT+7 tanpa colon"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone(timedelta(hours=7)))
        else:
            dt = dt.astimezone(timezone(timedelta(hours=7)))
        millis = f"{int(dt.microsecond / 1000):03d}"
        tz = dt.strftime("%z")
        return dt.strftime(f"%Y-%m-%dT%H:%M:%S.{millis}") + tz

@app.route('/xdataenc', methods=['POST'])
def xdata_encrypt_sign():
    """Endpoint untuk encrypt data dan generate signature - compatible dengan encryptsign_xdata"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400

        # Validasi API Key
        if api_key != CONFIG["API_KEY"]:
            return jsonify({
                'status': 'error', 
                'message': 'Invalid API key'
            }), 401

        id_token = data.get('id_token')
        method = data.get('method')
        path = data.get('path')
        body = data.get('body', {})
        
        if not all([id_token, method, path]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: id_token, method, path'
            }), 400

        # Encrypt body data
        body_json = json.dumps(body, separators=(',', ':'))
        encrypted_data = CryptoUtils.encrypt_aes_cbc(body_json, CONFIG["EncryptionKey"])
        
        # Generate timestamp (xtime)
        current_time = datetime.now()
        xtime = int(current_time.timestamp() * 1000)
        
        # Generate signature untuk encrypted data
        signature_data = f"{encrypted_data}{xtime}{path}{method}"
        x_signature = CryptoUtils.calculate_hmac_512(signature_data, CONFIG["EncryptionKeyHmac512"])
        
        response_data = {
            'encrypted_body': {
                'xdata': encrypted_data,
                'xtime': xtime
            },
            'x_signature': x_signature
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Encryption failed: {str(e)}'
        }), 500

@app.route('/xdatadec', methods=['POST'])
def xdata_decrypt():
    """Endpoint untuk decrypt data - compatible dengan decrypt_xdata"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400

        # Validasi API Key
        if api_key != CONFIG["API_KEY"]:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401

        xdata = data.get('xdata')
        xtime = data.get('xtime')
        
        if not xdata or not xtime:
            return jsonify({
                'status': 'error',
                'message': 'Missing xdata or xtime'
            }), 400

        # Decrypt data
        decrypted_data = CryptoUtils.decrypt_aes_cbc(xdata, CONFIG["EncryptionKey"])
        
        # Parse JSON decrypted data
        plaintext = json.loads(decrypted_data)
        
        return jsonify({
            'plaintext': plaintext
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Decryption failed: {str(e)}'
        }), 500

@app.route('/paysign', methods=['POST'])
def payment_sign():
    """Endpoint untuk signing payment - compatible dengan get_x_signature_payment"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400

        # Validasi API Key
        if api_key != CONFIG["API_KEY"]:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401

        access_token = data.get('access_token')
        sig_time_sec = data.get('sig_time_sec')
        package_code = data.get('package_code')
        token_payment = data.get('token_payment')
        payment_method = data.get('payment_method')
        payment_for = data.get('payment_for')
        path = data.get('path')
        
        if not all([access_token, sig_time_sec, package_code, token_payment, payment_method, payment_for, path]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields for payment signing'
            }), 400

        # Generate signature seperti XL
        data_to_sign = f"{access_token}{sig_time_sec}{package_code}{token_payment}{payment_method}{payment_for}{path}"
        x_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["EncryptionKeyHmac512"])
        
        return jsonify({
            'x_signature': x_signature
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Payment signing failed: {str(e)}'
        }), 500

@app.route('/bountysign', methods=['POST'])
def bounty_sign():
    """Endpoint untuk signing bounty - compatible dengan get_x_signature_bounty"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400

        if api_key != CONFIG["API_KEY"]:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401

        access_token = data.get('access_token')
        sig_time_sec = data.get('sig_time_sec')
        package_code = data.get('package_code')
        token_payment = data.get('token_payment')
        
        if not all([access_token, sig_time_sec, package_code, token_payment]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields for bounty signing'
            }), 400

        # Generate signature untuk bounty
        data_to_sign = f"{access_token}{sig_time_sec}{package_code}{token_payment}"
        x_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["EncryptionKeyHmac512"])
        
        return jsonify({
            'x_signature': x_signature
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Bounty signing failed: {str(e)}'
        }), 500

@app.route('/rolaysign', methods=['POST'])
def loyalty_sign():
    """Endpoint untuk signing loyalty - compatible dengan get_x_signature_loyalty"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400

        if api_key != CONFIG["API_KEY"]:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401

        sig_time_sec = data.get('sig_time_sec')
        package_code = data.get('package_code')
        token_confirmation = data.get('token_confirmation')
        path = data.get('path')
        
        if not all([sig_time_sec, package_code, token_confirmation, path]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields for loyalty signing'
            }), 400

        # Generate signature untuk loyalty
        data_to_sign = f"{sig_time_sec}{package_code}{token_confirmation}{path}"
        x_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["EncryptionKeyHmac512"])
        
        return jsonify({
            'x_signature': x_signature
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Loyalty signing failed: {str(e)}'
        }), 500

@app.route('/ax_sign', methods=['POST'])
def ax_sign():
    """Endpoint untuk AX signature - compatible dengan ax_api_signature"""
    try:
        data = request.get_json()
        api_key = request.headers.get('x-api-key')
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Missing request body'
            }), 400

        if api_key != CONFIG["API_KEY"]:
            return jsonify({
                'status': 'error',
                'message': 'Invalid API key'
            }), 401

        ts_for_sign = data.get('ts_for_sign')
        contact = data.get('contact')
        code = data.get('code')
        contact_type = data.get('contact_type')
        
        if not all([ts_for_sign, contact, code, contact_type]):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields for AX signing'
            }), 400

        # Generate signature untuk AX
        data_to_sign = f"{ts_for_sign}{contact}{code}{contact_type}"
        ax_signature = CryptoUtils.calculate_hmac_512(data_to_sign, CONFIG["AX_FP_KEY"])
        
        return jsonify({
            'ax_signature': ax_signature
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'AX signing failed: {str(e)}'
        }), 500

@app.route('/request_otp', methods=['POST'])
def request_otp():
    """Endpoint untuk mensimulasikan permintaan OTP."""
    data = request.get_json()
    phone_number = data.get('phone_number')

    if not phone_number:
        return jsonify({'status': 'error', 'message': 'Nomor telepon diperlukan'}), 400

    # Di dunia nyata, di sini Anda akan mengirim OTP.
    # Di sini kita hanya mensimulasikan keberhasilan.
    print(f"OTP diminta untuk nomor: {phone_number}. OTP simulasi adalah '123456'.")
    return jsonify({
        'status': 'success',
        'message': f'OTP telah dikirim ke {phone_number}'
    })

@app.route('/validate_otp', methods=['POST'])
def validate_otp():
    """Endpoint untuk mensimulasikan validasi OTP dan mengembalikan token."""
    data = request.get_json()
    phone_number = data.get('phone_number')
    otp_code = data.get('otp_code')

    if not phone_number or not otp_code:
        return jsonify({'status': 'error', 'message': 'Nomor telepon dan kode OTP diperlukan'}), 400

    # OTP yang benar di-hardcode untuk simulasi
    CORRECT_OTP = "123456"

    if otp_code == CORRECT_OTP:
        # Buat token akses palsu
        dummy_token = f"dummy_token_for_{phone_number}_{uuid.uuid4()}"
        print(f"OTP benar untuk {phone_number}. Token dibuat: {dummy_token}")
        return jsonify({
            'status': 'success',
            'access_token': dummy_token,
            'message': 'Login berhasil'
        })
    else:
        print(f"OTP salah untuk {phone_number}. Diterima: {otp_code}")
        return jsonify({'status': 'error', 'message': 'Kode OTP salah'}), 401

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'XL Crypto Server',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

# Additional helper endpoints
@app.route('/build_encrypted_field', methods=['GET'])
def build_encrypted_field():
    """Helper endpoint untuk testing build_encrypted_field"""
    iv_hex16 = os.urandom(8).hex()
    key = CONFIG["EncryptionKey"]
    
    # Simulate empty data encryption
    iv = iv_hex16.encode('ascii')
    cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, iv=iv)
    ct = cipher.encrypt(pad(b'', AES.block_size))
    
    encrypted_field = base64.b64encode(ct).decode('ascii') + iv_hex16
    return jsonify({'encrypted_field': encrypted_field})

if __name__ == '__main__':
    print("XL Crypto Server starting...")
    print(f"API Key: {CONFIG['API_KEY']}")
    print("Endpoints available:")
    print("  POST /xdataenc     - Encrypt and sign data")
    print("  POST /xdatadec     - Decrypt data") 
    print("  POST /paysign      - Payment signing")
    print("  POST /bountysign   - Bounty signing")
    print("  POST /rolaysign    - Loyalty signing")
    print("  POST /ax_sign      - AX signing")
    print("  GET  /health       - Health check")
    
    app.run(host='0.0.0.0', port=5000, debug=True)