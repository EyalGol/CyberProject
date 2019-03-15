import socket
from select import select
from pickle import dumps, loads
from threading import Thread
from random import randint, choice
from time import sleep

HEADERSIZE = 14
GameDict = {}
pid_counter = 0
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 3345))
print("binding successful")
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


def handle_game(gid):
    global GameDict
    GameDict[gid] = {}
    gd = GameDict[gid]
    gd["chat_log"] = []
    gd["players"] = {}
    gd["points"] = []
    gd["clear"] = False
    gd["last_won"] = None
    sleep(0.1)
    gd["answer"] = choice(random_list)
    gd["drawing"] = choice(list(gd["players"].values()))
    while True:
        readl, writel, _ = select(gd["players"].keys(), gd["players"].keys(), [])
        if readl:
            for conn in readl:
                data = recv_msg(conn)
                if data["is_drawing"]:
                    gd["points"] = data["points"]
                else:
                    gd["chat_log"].append(data["msg"])
                    if data["msg"] == gd["answer"]:
                        gd["last_won"] = gd["players"][conn]
                        gd["answer"] = choice(random_list)
                        gd["drawing"] = choice(list(gd["players"].values()))
                        gd["clear"] = True
                    else:
                        gd["clear"] = False
        if writel:
            to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                       "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
            for conn in writel:
                send_msg(conn, to_send)
        gd["clear"] = False
        sleep(0.2)


def handle_connection():
    global GameDict, pid_counter, server
    print("listening")
    while True:
        conn, addr = server.accept()
        data = recv_msg(conn)
        pid = pid_counter
        pid_counter += 1
        if data["new"]:
            gid = ""
            for x in range(6):
                gid += str(randint(0, 10))
            gid = int(gid)
            Thread(target=handle_game, args=([gid])).start()
        else:
            gid = int(data["gid"])
        GameDict[gid]["players"][conn] = pid
        send_msg(conn, {"gid": gid, "pid": pid})
        print(str(addr), "has connected, with the id of", pid)


if __name__ == "__main__":
    Thread(target=handle_connection).start()
    while True:
        pass
