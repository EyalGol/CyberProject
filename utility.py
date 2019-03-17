from _pickle import dumps, loads
import pygame as pg

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


def send_msg(conn, msg):
    try:
        msg = dumps(msg)
        conn.send(msg)
        return True
    except:
        return False


def recv_msg(conn):
    try:
        data = loads(conn.recv(100000))
        return data
    except:
        pass


"""
def send_msg(conn, msg):
    msg = dumps(msg)
    msg = bytes(f'{hex(len(msg)):<{HEADERSIZE}}', "utf8") + msg
    total_sent = 0
    msglen = len(msg)
    while total_sent < msglen:
        try:
            total_sent += conn.send(msg[total_sent:])
        except:
            return False
    return True


def recv_msg(conn):
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
        except:
            return False
    msg = loads(full_msg[HEADERSIZE:msglen+HEADERSIZE])
    return msg
"""
