"""XOR-based file encryption and decryption tool with compression."""

import zlib
import hashlib


def xor_encrypt_decrypt(data, key):
    """XOR encryption/decryption function."""
    if not data or not key:
        raise ValueError("Data and key cannot be empty")
    
    result = bytearray()
    key_len = len(key)
    
    for i, byte in enumerate(data):
        if isinstance(byte, int):
            result.append(byte ^ key[i % key_len])
        else:
            result.append(ord(byte) ^ key[i % key_len])
    
    return bytes(result)


def derive_key_from_password(password):
    """Derive a key from a password using SHA256 hashing."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    key = hashlib.sha256(password).digest()
    return key


def encrypt_file(input_file, output_file, password):
    """Encrypt a file using XOR encryption with zlib compression."""
    try:
        with open(input_file, 'rb') as f:
            data = f.read()
        
        compressed_data = zlib.compress(data, level=9)
        key = derive_key_from_password(password)
        encrypted_data = xor_encrypt_decrypt(compressed_data, key)
        
        with open(output_file, 'wb') as f:
            f.write(encrypted_data)
        
        print(f"✓ File encrypted successfully: {output_file}")
        return True
    
    except FileNotFoundError:
        print(f"✗ Error: File '{input_file}' not found")
        return False
    except Exception as e:
        print(f"✗ Error during encryption: {e}")
        return False


def decrypt_file(input_file, output_file, password):
    """Decrypt a file using XOR encryption with zlib decompression."""
    try:
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()
        
        key = derive_key_from_password(password)
        decrypted_data = xor_encrypt_decrypt(encrypted_data, key)
        original_data = zlib.decompress(decrypted_data)
        
        with open(output_file, 'wb') as f:
            f.write(original_data)
        
        print(f"✓ File decrypted successfully: {output_file}")
        return True
    
    except FileNotFoundError:
        print(f"✗ Error: File '{input_file}' not found")
        return False
    except zlib.error:
        print(f"✗ Error: Wrong password or file is corrupted")
        return False
    except Exception as e:
        print(f"✗ Error during decryption: {e}")
        return False
