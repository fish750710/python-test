from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import base64


def generate_key(site, sitetime):
    try:
        site = str(site)
        sitetime = str(sitetime)
        # Ensure site is at least 8 characters, pad with '1' if shorter
        site_padded = site.rjust(8, '1')
        # Use last 8 characters of sitetime, pad with '0' if shorter
        sitetime_last_eight = sitetime[-8:].rjust(8, '0')
        # Combine site padded and last 8 characters of sitetime to form 16-byte key
        key_str_128 = (site_padded + sitetime_last_eight).encode()
        
        return key_str_128
    except Exception as e:
        raise ValueError(f"Error generation_key: {e}")


def encrypt_ecb(plaintext, site, sitetime, key=None):
    try:
        # Generate or use provided key
        if key is None:
            key = generate_key(site, sitetime)
        else:
            key = key.encode()  # Convert key string to bytes
        
        # Serialize plaintext to JSON
        plaintext_json = json.dumps(plaintext, separators=(',', ':'))
        
        # Convert key and plaintext to bytes
        key_bytes = key if isinstance(key, bytes) else key.encode()
        plaintext_bytes = plaintext_json.encode('utf-8')
        
        # Create AES ECB cipher
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        
        # Pad plaintext using PKCS7
        padded_plaintext = pad(plaintext_bytes, AES.block_size)
        
        # Encrypt padded plaintext
        ciphertext = cipher.encrypt(padded_plaintext)
        
        # Encode encrypted ciphertext to Base64
        encrypted_base64 = base64.b64encode(ciphertext).decode('utf-8')
        
        return encrypted_base64
    except Exception as e:
        raise ValueError(f"Error encrypt_ecb: {e}")