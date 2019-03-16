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
        print("sending", str(msg)[:20] + "...")
        msg = dumps(msg)
        conn.send(msg)
    except:
        pass


def recv_msg(conn):
    try:
        print("receiving msg")
        data = loads(conn.recv(100000000))
        print(data, "received")
        return data
    except:
        pass

#def send_msg(conn, msg):
#    try:
#        print("sending", str(msg)[:20] + "...")
#        msg = dumps(msg)
#        msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf8") + msg
#        print("byte form:", msg)
#        total_sent = 0
#        msglen = len(msg)
#        while total_sent < msglen:
#            total_sent += conn.send(msg[total_sent:])
#            print("total_sent:", total_sent, "left:", msglen - total_sent)
#    except:
#        pass
#
#
#def recv_msg(conn):
#    print("receiving")
#    msg = conn.recv(64)
#    msglen = int(msg[:HEADERSIZE])
#    full_msg = b'' + msg
#    print("fullmsg:", full_msg)
#    print("msglen:", msglen)
#    while len(full_msg) < msglen+HEADERSIZE:
#        try:
#            full_msg += conn.recv(1024)
#            print("recved:", len(full_msg), "left:", msglen-len(full_msg))
#        except:
#            pass
#    print(full_msg, "full msg")
#    msg = loads(full_msg[HEADERSIZE:msglen+HEADERSIZE])
#    print(msg, "final messge")
#    return msg

