

# yay -S python-pycryptodome

from Crypto.Cipher import AES
from Crypto import Random
import random
import hashlib
from Crypto.Util.py3compat import bchr, bord
import string
from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto import Random
import sys
import base64
import hmac
from hashlib import sha256
from cryptography.fernet import Fernet

from datetime import datetime, timedelta, timezone


def pad(data_to_pad, block_size, style='pkcs7'):
    padding_len = block_size-len(data_to_pad) % block_size
    if style == 'pkcs7':
        padding = bchr(padding_len)*padding_len
    elif style == 'x923':
        padding = bchr(0)*(padding_len-1) + bchr(padding_len)
    elif style == 'iso7816':
        padding = bchr(128) + bchr(0)*(padding_len-1)
    else:
        raise ValueError("Unknown padding style")
    return data_to_pad + padding


def unpad(padded_data, block_size, style='pkcs7'):
    pdata_len = len(padded_data)
    if pdata_len % block_size:
        raise ValueError("Input data is not padded")
    if style in ('pkcs7', 'x923'):
        padding_len = bord(padded_data[-1])
        if padding_len < 1 or padding_len > min(block_size, pdata_len):
            raise ValueError("Padding is incorrect.")
        if style == 'pkcs7':
            if padded_data[-padding_len:] != bchr(padding_len)*padding_len:
                raise ValueError("PKCS#7 padding is incorrect.")
        else:
            if padded_data[-padding_len:-1] != bchr(0)*(padding_len-1):
                raise ValueError("ANSI X.923 padding is incorrect.")
    elif style == 'iso7816':
        padding_len = pdata_len - padded_data.rfind(bchr(128))
        if padding_len < 1 or padding_len > min(block_size, pdata_len):
            raise ValueError("Padding is incorrect.")
        if padding_len > 1 and padded_data[1-padding_len:] != bchr(0)*(padding_len-1):
            raise ValueError("ISO 7816-4 padding is incorrect.")
    else:
        raise ValueError("Unknown padding style")
    return padded_data[:-padding_len]


def twoway_decrypt(encrypted, key):
    m = hashlib.md5()
    m.update(key.encode())
    key = m.hexdigest()
    key = key.encode()

    temp = encrypted
    iv = temp[0:16]
    encrypted = temp[16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    decrypted = decrypted.decode()
    return decrypted


def twoway_encrypt(plainmsg, key):
    m = hashlib.md5()
    m.update(key.encode())
    key = m.hexdigest()
    key = key.encode()

    iv = Random.new().read(AES.block_size)
    # iv = b'1111111100000000'

    plainmsg = plainmsg.encode()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plainmsg, AES.block_size))

    # print ('key ' + str(b64encode(key)))
    # print ('iv ' + str(b64encode(iv)))
    # print ('plainmsg ' + str(b64encode(plainmsg)))

    return iv + encrypted


def fernet_encrypt(message, key):
    f = Fernet(key)
    return f.encrypt(message.encode()).decode()

def fernet_decrypt(encrypted, key):
    f = Fernet(key)
    return f.decrypt(encrypted.encode()).decode()

def randomstring(stringLength):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def oneway_hash(message):
    message_bytes = str.encode(message)
    hexstring = hashlib.sha256(message_bytes).hexdigest()
    return hexstring




# this is not secured at all
def shuffle_generate():

    import string
    import random

    keys = string.ascii_letters + string.digits + '-'
    values = ''.join(
        random.sample(keys, len(keys))
    )

    mapping = dict(zip(keys, values))
    reverse_mapping = {v: k for k, v in mapping.items()}
    return mapping, reverse_mapping
def shuffle_encrypt(s):
    missing=' '
    mapping = {
        'a': 'E', 'b': 'T', 'c': 'H', 'd': 'U', 'e': '7', 'f': 'Z', 'g': 'y', 'h': 'o',
        'i': '0', 'j': 'A', 'k': 'c', 'l': '3', 'm': 'a', 'n': 'i', 'o': 'h', 'p': 'N',
        'q': 'J', 'r': 'F', 's': '-', 't': '9', 'u': 'G', 'v': 'V', 'w': 'l', 'x': 'W',
        'y': 'u', 'z': 'p', 'A': 'C', 'B': 'f', 'C': 'M', 'D': 'e', 'E': 'w', 'F': 'v',
        'G': 'b', 'H': 'm', 'I': 'z', 'J': 's', 'K': 'P', 'L': 'D', 'M': 'n', 'N': 'g',
        'O': '6', 'P': '5', 'Q': 'X', 'R': '1', 'S': 't', 'T': 'R', 'U': 'd', 'V': 'I',
        'W': 'S', 'X': 'q', 'Y': 'x', 'Z': '8', '0': 'O', '1': '2', '2': 'L', '3': 'r',
        '4': 'j', '5': 'k', '6': '4', '7': 'B', '8': 'K', '9': 'Y', '-': 'Q'
    }
    
    return ''.join([mapping.get(c, missing) for c in s])
def shuffle_decrypt(s):
    missing=' '
    reverse_mapping = {
        'E': 'a', 'T': 'b', 'H': 'c', 'U': 'd', '7': 'e', 'Z': 'f', 'y': 'g', 'o': 'h',
        '0': 'i', 'A': 'j', 'c': 'k', '3': 'l', 'a': 'm', 'i': 'n', 'h': 'o', 'N': 'p',
        'J': 'q', 'F': 'r', '-': 's', '9': 't', 'G': 'u', 'V': 'v', 'l': 'w', 'W': 'x',
        'u': 'y', 'p': 'z', 'C': 'A', 'f': 'B', 'M': 'C', 'e': 'D', 'w': 'E', 'v': 'F',
        'b': 'G', 'm': 'H', 'z': 'I', 's': 'J', 'P': 'K', 'D': 'L', 'n': 'M', 'g': 'N',
        '6': 'O', '5': 'P', 'X': 'Q', '1': 'R', 't': 'S', 'R': 'T', 'd': 'U', 'I': 'V',
        'S': 'W', 'q': 'X', 'x': 'Y', '8': 'Z', 'O': '0', '2': '1', 'L': '2', 'r': '3',
        'j': '4', 'k': '5', '4': '6', 'B': '7', 'K': '8', 'Y': '9', 'Q': '-'
    }

    return ''.join([reverse_mapping.get(c, missing) for c in s])
