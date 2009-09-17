# coding:utf-8
"""
Cryptographic functions for encrypting and decrypting text.
Temporary file are used by only contains encrypted data.

@author: Sébastien Renard <Sebastien.Renard@digitalfox.org>
@license: GPL v3
"""

import base64
import hashlib

import tui
import db

from sqlobject import SQLObjectNotFound

# Prefix used to recognise encrypted message
CRYPTO_PREFIX = "---YOKADI-ENCRYPTED-MESSAGE---"

try:
    from ncrypt.cipher import CipherType, EncryptCipher, DecryptCipher, CipherError
    NCRYPT=True
    cipherType = CipherType("AES-128", "CBC")
    initialVector = cipherType.ivLength()*"y"
except ImportError:
    tui.warning("NCrypt module not found. You will not be able to use cryptographic function")
    tui.warning("like encrypting or decrypting task title or description")
    tui.warning("You can find NCrypt here http://tachyon.in/ncrypt/")
    NCRYPT=False

#TODO: add unit test

class YokadiCryptoManager(object):
    """Manager object for Yokadi cryptographic operation"""
    def __init__(self):
        self.passphrase = None # Cache encryption passphrase
        try:
            self.passphraseHash = db.Config.byName("PASSPHRASE_HASH").value
        except SQLObjectNotFound:
            self.passphraseHash = None # Passphrase hash


    def encrypt(self, data):
        """Encrypt user data.
        @return: encrypted data"""
        if not NCRYPT:
            tui.warning("Crypto functions not available")
            return data
        self.askPassphrase()
        aPassphrase = adjustPassphrase(self.passphrase)
        encryptCipher = EncryptCipher(cipherType, aPassphrase, initialVector)
        return CRYPTO_PREFIX + base64.b64encode(encryptCipher.finish(data))


    def decrypt(self, data):
        """Decrypt user data.
        @return: decrypted data"""
        if not NCRYPT:
            tui.warning("Crypto functions not available")
            return data
        data = data[len(CRYPTO_PREFIX):] # Remove crypto prefix
        data = base64.b64decode(data)
        self.askPassphrase()
        aPassphrase = adjustPassphrase(self.passphrase)
        try:
            decryptCipher = DecryptCipher(cipherType, aPassphrase, initialVector)
            data = decryptCipher.finish(data)
        except CipherError:
            data = "<...Failed to decrypt data...>"
        return data


    def askPassphrase(self):
        """Ask user for passphrase if needed"""
        cache = bool(int(db.Config.byName("PASSPHRASE_CACHE").value))
        if self.passphrase and cache:
            return
        self.passphrase = tui.editLine("", prompt="passphrase> ", echo=False)
        hash = hashlib.md5(self.passphrase).hexdigest()
        if hash!=self.passphraseHash and cache:
            tui.warning("Passphrase differ from previous one. "
                        "If you really want to have different passphrase, "
                        "you should deactivate passphrase cache "
                        "with c_set PASSPHRASE_CACHE 0")

        self.passphraseHash = hash
        db.Config.byName("PASSPHRASE_HASH").value = hash


    def isEncrypted(self, data):
        """Check if data is encrypted
        @return: True is the data seems encrypted, else False"""
        if data.startswith(CRYPTO_PREFIX):
            return True
        else:
            return False


def adjustPassphrase(passphrase):
    """Adjust passphrase to meet cipher requirement length"""
    passphrase = passphrase[:cipherType.keyLength()] # Shrink if key is too large
    passphrase = passphrase.ljust(cipherType.keyLength(), "y") # Complete if too short
    return passphrase