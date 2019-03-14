import pygame as pg
from pygame.locals import *
from threading import Thread
import socket
from json import dumps, loads
from select import select

pg.init()


class Game:
    def __init__(self):
        self.is_playing = True
        self.screen = pg.display.set_mode((360, 600))
        self.font = pg.font.Font(None, 30)
        self.client = socket.socket()
        self.chat_log = []
        self.msg = ""
        self.points = []
        self.pid = None
        self.gid = None
        self.is_drawing = False

    def start_client(self, ip, port, gid=None):
        self.client.connect((ip, int(port)))
        if gid is None:
            data = dumps({"new": True}).encode()
        else:
            data = dumps({"new": False, "gid": gid}).encode()
        self.client.sendall(data)
        json_dump = loads(self.client.recv(1024).decode())
        self.pid = json_dump["pid"]
        self.gid = json_dump["gid"]
        while self.is_playing:
            read, write, _ = select([self.client], [self.client], [])
            if write:
                if len(self.msg) > 0:
                    self.client.sendall(self.msg.encode())
                if self.is_drawing:
                    # TODO: make the server send stuff
                    pass
            if read:
                # TODO: make the server receive stuff
                json_dump = loads(read[0].recv(1024))
                if self.pid == json_dump["drawing"]:
                    self.is_drawing = True
                else:
                    self.is_drawing = False
                    self.points = json_dump["points"]
                    self.chat_log = json_dump["chat_log"]
        self.client.close()

    def start_menu(self):
        self.screen = pg.display.set_mode((360, 350))
        center = self.screen.get_rect().center
        create_text = self.font.render("Create a new game", True, (255, 255, 255), (80, 80, 80))
        connect_text = self.font.render("Connect to an existing game", True, (255, 255, 255), (80, 80, 80))
        create_rect = create_text.get_rect()
        connect_rect = connect_text.get_rect()
        create_rect.center = (center[0], center[1] - 50)
        connect_rect.center = (center[0], center[1] + 50)
        self.screen.fill((0, 0, 0))
        self.screen.blit(create_text, create_rect)
        self.screen.blit(connect_text, connect_rect)
        pg.display.flip()
        while self.is_playing:
            for evt in pg.event.get():
                if evt.type == QUIT:
                    self.is_playing = False
            is_pressed = pg.mouse.get_pressed()[0]
            if is_pressed:
                pos = pg.mouse.get_pos()
                if create_rect.collidepoint(pos):
                    self.create_menu()
                elif connect_rect.collidepoint(pos):
                    self.connect_menu()

    def connect_menu(self):
        self.screen = pg.display.set_mode((640, 480))
        is_typing = True
        ip = "IP"
        port = "PORT"
        gid = "Game ID"
        editing = None
        while is_typing and self.is_playing:
            for evt in pg.event.get():
                if evt.type == KEYDOWN:
                    if evt.key == K_BACKSPACE:
                        if editing == 0:
                            ip = ip[:-1]
                        elif editing == 1:
                            port += port[:-1]
                        elif editing == 2:
                            gid = gid[:-1]
                    elif editing == 0:
                        ip += evt.unicode
                    elif editing == 1:
                        port += evt.unicode
                    elif editing == 2:
                        gid += evt.unicode
                if evt.type == QUIT:
                    self.is_playing = False
            self.screen.fill((0, 0, 0))
            center = self.screen.get_rect().center
            ip_text = self.font.render(ip, True, (255, 255, 255), (80, 80, 80))
            port_text = self.font.render(port, True, (255, 255, 255), (80, 80, 80))
            gid_text = self.font.render(gid, True, (255, 255, 255), (80, 80, 80))
            connect_button = self.font.render("Connect", True, (255, 255, 255), (80, 80, 80))
            connect_button_rect = connect_button.get_rect()
            ip_rect = ip_text.get_rect()
            port_rect = port_text.get_rect()
            gid_rect = gid_text.get_rect()
            ip_rect.center = (center[0], center[1] - 70)
            port_rect.center = (center[0], center[1] - 25)
            gid_rect.center = (center[0], center[1] + 25)
            connect_button_rect.center = (center[0], center[1] + 75)
            self.screen.fill((0, 0, 0))
            self.screen.blit(ip_text, ip_rect)
            self.screen.blit(port_text, port_rect)
            self.screen.blit(gid_text, gid_rect)
            self.screen.blit(connect_button, connect_button_rect)
            pg.display.flip()
            is_pressed = pg.mouse.get_pressed()[0]
            if is_pressed:
                pos = pg.mouse.get_pos()
                if ip_rect.collidepoint(pos):
                    ip = ""
                    editing = 0
                elif port_rect.collidepoint(pos):
                    port = ""
                    editing = 1
                elif gid_rect.collidepoint(pos):
                    gid = ""
                    editing = 2
                elif connect_button_rect.collidepoint(pos):
                    Thread(target=self.start_client, args=(ip, port, gid)).start()
                    self.game_start()

    def create_menu(self):
        self.screen = pg.display.set_mode((640, 480))
        is_typing = True
        ip = "IP"
        port = "PORT"
        editing = None
        while is_typing and self.is_playing:
            for evt in pg.event.get():
                if evt.type == KEYDOWN:
                    if evt.key == K_BACKSPACE:
                        if editing == 0:
                            ip = ip[:-1]
                        elif editing == 1:
                            port = port[:-1]
                    elif editing == 0:
                        ip += evt.unicode
                    elif editing == 1:
                        port += evt.unicode
                if evt.type == QUIT:
                    self.is_playing = False
            self.screen.fill((0, 0, 0))
            center = self.screen.get_rect().center
            ip_text = self.font.render(ip, True, (255, 255, 255), (80, 80, 80))
            port_text = self.font.render(port, True, (255, 255, 255), (80, 80, 80))
            connect_button = self.font.render("Create", True, (255, 255, 255), (80, 80, 80))
            ip_rect = ip_text.get_rect()
            port_rect = port_text.get_rect()
            connect_button_rect = connect_button.get_rect()
            ip_rect.center = (center[0], center[1] - 50)
            port_rect.center = center
            connect_button_rect.center = (center[0], center[1] + 50)
            self.screen.fill((0, 0, 0))
            self.screen.blit(ip_text, ip_rect)
            self.screen.blit(port_text, port_rect)
            self.screen.blit(connect_button, connect_button_rect)
            pg.display.flip()
            is_pressed = pg.mouse.get_pressed()[0]
            if is_pressed:
                pos = pg.mouse.get_pos()
                if ip_rect.collidepoint(pos):
                    ip = ""
                    editing = 0
                elif port_rect.collidepoint(pos):
                    port = ""
                    editing = 1
                elif connect_button_rect.collidepoint(pos):
                    Thread(target=self.start_client, args=(ip, port)).start()
                    self.game_start()

    def game_start(self):
        width, height = 1000, 500
        msg_current = ""
        self.screen = pg.display.set_mode((width, height))
        while self.is_playing:
            if self.is_drawing:
                for evt in pg.event.get():
                    if evt.type == QUIT:
                        self.is_playing = False
                is_pressed = pg.mouse.get_pressed()[0]
                if is_pressed:
                    pos = pg.mouse.get_pos()
                    if pos[0] < width-413:
                        self.points.append(pos)
            else:
                for evt in pg.event.get():
                    if evt.type == QUIT:
                        self.is_playing = False
                    if evt.type == KEYDOWN:
                        if evt.key == K_RETURN:
                            self.msg = msg_current
                            msg_current = ""
                        elif evt.key == K_BACKSPACE:
                            msg_current = msg_current[:-1]
                        else:
                            msg_current += evt.unicode
            self.screen.fill((230, 230, 230))
            hr = pg.Rect(width-400, 0, 10, height)
            pg.draw.rect(self.screen, (30, 0, 0), hr)
            if self.points:
                for point in self.points:
                    pg.draw.circle(self.screen, (20, 100, 50), point, 15)
            chat_height = 30
            if len(msg_current) > 0:
                    chat_line = self.font.render(msg_current, True, (255, 255, 255), (80, 80, 80))
                    chat_line_rect = chat_line.get_rect()
                    chat_line_rect.bottomleft = ((width - 380), (height - chat_height))
                    chat_height += 20
                    self.screen.blit(chat_line, chat_line_rect)
            if self.chat_log:
                for msg in self.chat_log[-1]:
                    chat_line = self.font.render(msg, True, (255, 255, 255), (80, 80, 80))
                    chat_line_rect = chat_line.get_rect()
                    chat_line_rect.bottomleft = ((width - 380), (height - chat_height))
                    chat_height += 20
                    self.screen.blit(chat_line, chat_line_rect)

            pg.display.flip()


if __name__ == "__main__":
    game = Game()
    game.start_menu()
    pg.quit()
