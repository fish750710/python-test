from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64
import json

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
        raise ValueError(f"Error generate_key: {e}")

def decrypt_aes(encrypted_base64, site, sitetime, key=None):
    try:
        # Generate or use provided key
        if key is None:
            key = generate_key(site, sitetime)
        else:
            key = key.encode() if isinstance(key, str) else key

        # Decode base64 and decrypt
        encrypted_bytes = base64.b64decode(encrypted_base64)
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        try:
            plaintext = unpad(decrypted_bytes, AES.block_size)
        except ValueError:
            plaintext = decrypted_bytes
            
        # Convert to string and parse JSON
        try:
            decrypted_text = plaintext.decode('utf-8')
            return json.loads(decrypted_text)
        except json.JSONDecodeError:
            return decrypted_text.rstrip('\0')
        except UnicodeDecodeError:
            decrypted_text = plaintext.rstrip(b'\0').decode('utf-8', errors='ignore')
            return decrypted_text
            
    except Exception as e:
        raise ValueError(f"Error decrypt_aes: {e}")