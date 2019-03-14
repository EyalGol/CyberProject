import socket
from select import select
from json import dumps, loads
from threading import Thread
from random import randint, choice
from time import sleep

GameDict = {}
pid_counter = 0
server = socket.socket()
server.bind(("localhost", 3345))
server.listen(30)
random_list = ['beef', 'photo album', 'water bottle', 'toothpaste', 'packing peanuts', 'grid paper', 'clothes',
               'picture frame', 'pen', 'bowl', 'leg warmers', 'stop sign', 'bread', 'lotion', 'bracelet', 'soap',
               'sand paper', 'clay pot', 'cat', 'carrots', 'spring', 'box', 'fake flowers', 'cell phone', 'socks',
               'needle', 'soy sauce packet', 'wagon', 'USB drive', 'food', 'spoon', 'shampoo', 'candy wrapper', 'mop',
               'shoe lace', 'sponge', 'desk', 'piano', 'charger', 'lip gloss', 'flowers', 'buckel', 'video games',
               'shovel', 'soda can', 'face wash', 'seat belt', 'helmet', 'bag', 'tissue box', 'door', 'tomato',
               'mouse pad', 'teddies', 'pillow', 'truck', 'playing card', 'sun glasses', 'brocolli', 'fridge',
               'coasters', 'button', 'keyboard', 'computer', 'bed', 'bottle', 'mirror', 'pool stick', 'speakers',
               'house', 'nail file', 'candle', 'mp3 player', 'slipper', 'toe ring', 'knife', 'scotch tape', 'camera',
               'chocolate', 'chapter book', 'drill press', 'toilet', 'plastic fork', 'bow', 'radio', 'table',
               'newspaper']


def handle_game(gid):
    global GameDict
    GameDict[gid] = {}
    gd = GameDict[gid]
    gd["chat_log"] = []
    gd["players"] = {}
    gd["points"] = []
    sleep(0.1)
    gd["answer"] = choice(random_list)
    gd["last_won"] = None
    gd["drawing"] = choice(list(gd["players"].values()))
    while True:
        readl, writel, _ = select(gd["players"].keys(), gd["players"].keys(), [])
        if readl:
            for conn in readl:
                data = conn.recv(1024).decode().split("}")[0] + "}"
                data = loads(data)
                if data["is_drawing"]:
                    gd["points"] = data["points"]
                else:
                    data = conn.recv(1024).decode().split("}")[0] + "}"
                    data = loads(data)
                    gd["chat_log"].append(data["msg"])
                    if data["msg"] == gd["answer"]:
                        gd["last_won"] = gd["players"][conn]
                        gd["answer"] = choice(random_list)
        if writel:
            to_send = dumps({"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                             "answer": gd["answer"]}).encode()
            for conn in writel:
                conn.sendall(to_send)


def handle_connection():
    global GameDict, pid_counter, server
    while True:
        conn, addr = server.accept()
        json_dump = loads(conn.recv(1024).decode())
        pid = pid_counter
        pid_counter += 1
        if json_dump["new"]:
            gid = ""
            for x in range(6):
                gid += str(randint(0, 10))
            gid = int(gid)
            Thread(target=handle_game, args=([gid])).start()
        else:
            gid = json_dump["gid"]
        GameDict[gid]["players"][conn] = pid
        conn.sendall(dumps({"gid": gid, "pid": pid}).encode())


if __name__ == "__main__":
    Thread(target=handle_connection).start()
    while True:
        pass
