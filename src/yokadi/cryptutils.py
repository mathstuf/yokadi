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

#TODO: add unit test
#TODO: check security issues

def encrypt(data, passphrase=None):
    """Encrypt user data. Passphrase is asked twice
    @return: encrypted data"""
    encryptedData = ""
    # Use temp dir instead of temp file because GPG complain if file already exists
    tmpFileDir = tempfile.mkdtemp(prefix="yokadi-")
    tmpFilePath = os.path.join(tmpFileDir, "data")
    cmd = ["gpg", "-ac", "-o", tmpFilePath]
    if passphrase:
        cmd.append("--passphrase-fd")
        cmd.append("0")
        cmd.append("--batch")
        cmd.append("--no-tty")
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        if passphrase:
            p.stdin.write(passphrase+"\n")
        p.stdin.write(data)
        p.stdin.flush()
        p.stdin.close()
        rc = p.wait()
        if rc == 0:
            encryptedData = file(tmpFilePath).read()
        else:
            print "Error while encrypting data"
    finally:
        os.unlink(tmpFilePath)
        os.removedirs(tmpFileDir)

    return encryptedData

def decrypt(data):
    """Decrypt user data. Passphrase is asked.
    @return: decrypted data"""
    decryptedData = "" 
    (fd, name) = tempfile.mkstemp(suffix=".txt", prefix="yokadi-") 
    try:
        fl = file(name, "w")
        fl.write(data)
        fl.close()
        p = subprocess.Popen(["gpg", "-ad", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rc = p.wait()
        if rc == 0:
            decryptedData = p.stdout.read()
        else:
            print "Error while decrypting data"
    finally:
        os.close(fd)
        os.unlink(name)

    return decryptedData

def isEncrypted(data):
    """Check if data is encrypted
    @return: True is the data seems encrypted, else False"""
    if data.startswith("-----BEGIN PGP MESSAGE-----"):
        return True
    else:
        return False