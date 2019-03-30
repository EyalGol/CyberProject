from _pickle import dumps, loads
import pygame as pg
import socket
from Crypto.Cipher import AES

HEADERSIZE = 10


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


def send_msg(aes_key, conn, msg):
    """
    sends a message to he designated connetion
    :param conn: the designated socket
    :param msg: the data
    :return: True if sent scornfully Else False
    """
    cipher_aes = AES.new(aes_key[0], AES.MODE_EAX, aes_key[1])
    try:
        print("send decrypted data", msg)
        msg = bytes(str(msg), "utf-8")
        enc_msg = cipher_aes.encrypt(msg)
        print("send encrypted data", enc_msg)
        conn.send(enc_msg)
        return True
    except ConnectionError as err:
        print(err)
        return False


def recv_msg(aes_key, conn):
    """
    receives data fron the designated connection
    :param conn: the connection socket
    :return: the received data
    """
    cipher_aes = AES.new(aes_key[0], AES.MODE_EAX, aes_key[1])
    try:
        enc_data = conn.recv(10000000)
        print("recv encrypted data", enc_data)
        data = cipher_aes.decrypt(enc_data)
        print("recv decrypted data", data)
        data = dict(data.decode())
        return data
    except ConnectionError as err:
        print(err)
        return False
    except EOFError as err:
        print(err)


"""
def send_msg(conn, msg):
    sends a buffered message to he designated connetion
    :param conn: the designated socket
    :param msg: the data
    :return: True if sent scornfully Else False
    msg = dumps(msg)
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


def recv_msg(conn):
    receives buffered data fron the designated connection
    :param conn: the connection socket
    :return: the received data
    try:
        msg = conn.recv(64)
    except:
        return False
    msglen = int(msg[:HEADERSIZE], 16)
    full_msg = b'' + msg
    while len(full_msg) < msglen+HEADERSIZE:
        try:
            full_msg += conn.recv(1024)
            print("recved:", len(full_msg), "left:", msglen-len(full_msg))
        except ConnectionError as err:
            print(err)
            return False
        except EOFError as err:
            print(err)
    msg = loads(full_msg[HEADERSIZE:msglen+HEADERSIZE])
    return msg

"""
