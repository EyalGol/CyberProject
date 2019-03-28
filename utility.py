from _pickle import dumps, loads
import pygame as pg
import socket
from queue import Queue
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
from threading import Thread

HEADERSIZE = 14


def render_text_center(surface, text, center_cords, color, backround=None):
    font = pg.font.Font(None, 30)
    render = font.render(text, True, color, backround)
    rect = render.get_rect()
    rect.center = center_cords
    surface.blit(render, rect)
    return rect


def render_text_topleft(surface, text, topleft_cords, color, backround=None):
    font = pg.font.Font(None, 30)
    render = font.render(text, True, color, backround)
    rect = render.get_rect()
    rect.topleft = topleft_cords
    surface.blit(render, rect)
    return rect


def render_text_bottomleft(surface, text, bottomleft_cords, color, backround=None):
    font = pg.font.Font(None, 30)
    render = font.render(text, True, color, backround)
    rect = render.get_rect()
    rect.bottomleft = bottomleft_cords
    surface.blit(render, rect)
    return rect


def render_text_midright(surface, text, midright_cords, color, backround=None):
    font = pg.font.Font(None, 30)
    render = font.render(text, True, color, backround)
    rect = render.get_rect()
    rect.midright = midright_cords
    surface.blit(render, rect)
    return rect


def send_thread(conn, to_send):
    """
    starts a thread and returns the value it returns.
    used because i need to have async data collection
    :param conn: the connection you want to send the data to
    :param to_send: the msg to send
    :return: returns True if was able to send data else False
    """
    que = Queue()
    t = Thread(target=lambda q, arg1, arg2: q.put(send_msg(arg1, arg2)), args=(que, conn, to_send))
    t.daemon = True
    t.start()
    t.join()
    return que.get()


def recv_thread(conn):
    """
    starts a thread and returns the value it returns.
    used because i need to have async data collection
    :param conn: where to receive from
    :return: False if there was an interaction or connection was lost else will return the data
    """
    que = Queue()
    t = Thread(target=lambda q, arg1: q.put(recv_msg(arg1)), args=(que, conn))
    t.daemon = True
    t.start()
    t.join()
    return que.get()


def send_msg(cipher_aes, conn, msg):
    """
    sends a messge with buffering
    :param conn: the connection you want to send the data to
    :param msg: the msg to send
    :return: returns True if was able to send data else False
    """
    msg = dumps(msg)
    msg = encrypt_AES(cipher_aes, msg)
    msg = bytes(f'{hex(len(msg)):<{HEADERSIZE}}', "utf8") + msg
    total_sent = 0
    msglen = len(msg)
    while total_sent < msglen:
        try:
            total_sent += conn.send(msg[total_sent:])
        except ConnectionError as err:
            print(err)
            return False
        except EOFError as err:
            print(err)
    return True


def recv_msg(cipher_aes, conn):
    """
    receives a message with buffering
    :param conn: where to receive from
    :return: False if there was an interaction or connection was lost else will return the data
    """
    try:
        msg = conn.recv(64)
    except:
        return False
    try:
        msglen = int(msg[:HEADERSIZE], 16)
    except ValueError:
        try:
            data = conn.recv(100000)
            data = loads(data[HEADERSIZE:])
            return data
        except ConnectionError as err:
            print(err)
            return False
        except EOFError as err:
            print(err)
        except Exception:
            return {"failed": True}
    full_msg = b'' + msg
    while len(full_msg) < msglen + HEADERSIZE:
        try:
            full_msg += conn.recv(1024)
        except ConnectionError as err:
            print(err)
            return False
        except EOFError as err:
            print(err)
    full_msg = decrypt_AES(cipher_aes, full_msg)
    msg = loads(full_msg[HEADERSIZE:msglen + HEADERSIZE])
    msg["failed"] = False
    return msg


def decrypt_AES(cipher_aes, data):
    """
    decrypt AES encrypted data
    :param cipher_aes: the AES key object
    :param data: the encrypted data
    :return: the decrypted data
    """
    return cipher_aes.decrypt_and_verify(data[0], data[1])


def encrypt_AES(cipher_aes, data):
    """
    encrypts AES
    :param cipher_aes: the AES key object
    :param data: the data to encrypt
    :return: the encrypted data
    """
    return cipher_aes.encrypt_and_digest(data)


def recv_session_key(private_key, conn):
    """
    listens to the conn, receives and gets the encrypted key
    :param private_key: private rsa key object
    :param conn: the connection you expect to get a message from
    :return: AES key object
    """
    print("receiving key")
    enc_session_key = loads(conn.recv(4096))
    cipher_rsa = PKCS1_OAEP.new(private_key)
    print("enc_key", enc_session_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    print("key received:", session_key)
    return AES.new(session_key[0], AES.MODE_EAX, session_key[1])


def send_session_key(conn):
    print("sending key")
    public_key = RSA.import_key(conn.recv(4096))
    session_key = get_random_bytes(16)
    cipher_rsa = PKCS1_OAEP.new(public_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    enc_session_key = cipher_rsa.encrypt(session_key)
    to_send = (enc_session_key, cipher_aes.nonce)
    conn.sendall(dumps(to_send))
    print("key sent")
    return cipher_aes


def init_key_exchange(public_key, conn):
    conn.sendall(public_key.export_key())
