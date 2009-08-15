# coding:utf-8
"""
Cryptographic functions for encrypting and decrypting text.
Temporary file are used by only contains encrypted data.

@author: Sébastien Renard <Sebastien.Renard@digitalfox.org>
@license: GPL v3
"""

import os
import tempfile
import subprocess

import tui

# Prefix used to recognise encrypted message
CRYPTO_PREFIX = "---YOKADI-ENCRYPTED-MESSAGE---"

try:
    from ncrypt.cipher import CipherType, EncryptCipher, DecryptCipher
    NCRYPT=True
    cipherType = CipherType("AES-128", "CBC")
    initialVector = cipherType.ivLength()*"y"
except ImportError:
    tui.warning("NCrypt module not found. You will not be able to use cryptographic function")
    tui.warning("like encrypting or decrypting task title or description")
    tui.warning("You can find NCrypt here http://tachyon.in/ncrypt/")
    NCRYPT=False

#TODO: add unit test
#TODO: catch exception and wrap it into yokadi exception ?

def encrypt(data, passphrase):
    """Encrypt user data.
    @return: encrypted data"""
    if not NCRYPT:
        tui.warning("Crypto functions not available")
        return data
    passphrase = adjustPassphrase(passphrase)
    encryptCipher = EncryptCipher(cipherType, passphrase, initialVector)
    return CRYPTO_PREFIX+encryptCipher.finish(data)

def decrypt(data, passphrase):
    """Decrypt user data.
    @return: decrypted data"""
    if not NCRYPT:
        tui.warning("Crypto functions not available")
        return data
    data = data[len(CRYPTO_PREFIX):] # Remove crypto prefix
    passphrase = adjustPassphrase(passphrase)
    decryptCipher = DecryptCipher(cipherType, passphrase, initialVector)
    return decryptCipher.finish(data)

def isEncrypted(data):
    """Check if data is encrypted
    @return: True is the data seems encrypted, else False"""
    if data.startswith(CRYPTO_PREFIX):
        return True
    else:
        return False

def askPassphrase():
    """Ask user for passphrase"""
    return tui.editLine("", prompt="passphrase> ")

def adjustPassphrase(passphrase):
    """Adjust passphrase to meet cipher requirement length"""
    passphrase = passphrase[:cipherType.keyLength()] # Shrink if key is too large
    passphrase = passphrase.ljust(cipherType.keyLength(), "y") # Complete if too short
    return passphrase