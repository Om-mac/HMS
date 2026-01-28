"""
AES-256 Encryption utility for sensitive medical data.
Implements HIPAA-compliant encryption for patient notes and sensitive fields.
"""
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from django.conf import settings


class AESEncryption:
    """
    AES-256 encryption class for encrypting/decrypting sensitive medical data.
    Uses CBC mode with PKCS7 padding.
    """
    
    def __init__(self, key: str = None):
        """
        Initialize the encryption handler with a key.
        
        Args:
            key: Optional encryption key. Uses settings.AES_ENCRYPTION_KEY if not provided.
        """
        if key is None:
            key = settings.AES_ENCRYPTION_KEY
        
        # Ensure key is 32 bytes for AES-256
        self.key = hashlib.sha256(key.encode()).digest()
        self.block_size = AES.block_size
    
    def _pad(self, data: str) -> bytes:
        """Apply PKCS7 padding to data."""
        padding_length = self.block_size - (len(data.encode()) % self.block_size)
        padding = chr(padding_length) * padding_length
        return (data + padding).encode()
    
    def _unpad(self, data: bytes) -> str:
        """Remove PKCS7 padding from data."""
        padding_length = data[-1]
        return data[:-padding_length].decode()
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext using AES-256-CBC.
        
        Args:
            plaintext: The text to encrypt.
            
        Returns:
            Base64-encoded encrypted string (IV + ciphertext).
        """
        if not plaintext:
            return ""
        
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = self._pad(plaintext)
        ciphertext = cipher.encrypt(padded_data)
        
        # Combine IV and ciphertext, then encode as base64
        encrypted_data = base64.b64encode(iv + ciphertext).decode()
        return encrypted_data
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt AES-256-CBC encrypted text.
        
        Args:
            encrypted_text: Base64-encoded encrypted string.
            
        Returns:
            Decrypted plaintext.
        """
        if not encrypted_text:
            return ""
        
        try:
            encrypted_data = base64.b64decode(encrypted_text.encode())
            iv = encrypted_data[:self.block_size]
            ciphertext = encrypted_data[self.block_size:]
            
            cipher = AES.new(self.key, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(ciphertext)
            
            return self._unpad(decrypted_padded)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")


class EncryptedTextField:
    """
    Descriptor for encrypting/decrypting text fields transparently.
    """
    
    def __init__(self, field_name: str):
        self.field_name = field_name
        self.encryption = AESEncryption()
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        encrypted_value = getattr(obj, f'_encrypted_{self.field_name}', '')
        return self.encryption.decrypt(encrypted_value) if encrypted_value else ''
    
    def __set__(self, obj, value):
        encrypted_value = self.encryption.encrypt(value) if value else ''
        setattr(obj, f'_encrypted_{self.field_name}', encrypted_value)


# Singleton instance for convenience
aes_encryption = AESEncryption()


def encrypt_field(value: str) -> str:
    """Convenience function to encrypt a value."""
    return aes_encryption.encrypt(value)


def decrypt_field(value: str) -> str:
    """Convenience function to decrypt a value."""
    return aes_encryption.decrypt(value)
