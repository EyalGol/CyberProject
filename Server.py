import socket
import pickle
from select import select
from threading import Thread
from sys import exit
from pprint import pformat
from random import randint, choice
from time import sleep
from utility import *

running = True
try:
    with open("dict.pickle", "rb") as file:
        GameDict = pickle.load(file)
except Exception:
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


def init_game(gid):
    GameDict[gid] = {}
    gd = GameDict[gid]
    gd["chat_log"] = []
    gd["players"] = {}
    gd["points"] = []
    gd["clear"] = False
    gd["last_won"] = None
    gd["closed"] = False
    gd["answer"] = choice(random_list)
    handle_game(gid)


def handle_game(gid):
    gd = GameDict[gid]
    gd["clear"] = False
    sleep(0.3)
    gd["drawing"] = choice(list(gd["players"].values()))
    while running:
        try:
            readl, writel, _ = select(gd["players"].keys(), gd["players"].keys(), [])
        except:
            readl, writel = [], []
        if readl:
            try:
                for conn in readl:
                    data = recv_msg(conn)
                    if not data:
                        conn.close()
                        del gd["players"][conn]
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
            except Exception as msg:
                print(msg)
        try:
            if writel:
                to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                           "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
                for conn in writel:
                    data = send_msg(conn, to_send)
                    if not data:
                        conn.close()
                        del gd["players"][conn]
            gd["clear"] = False
            sleep(0.1)
        except Exception as msg:
            print(msg)


def handle_connection():
    global GameDict, pid_counter, server
    print("listening")
    while running:
        conn, addr = server.accept()
        data = recv_msg(conn)
        pid = pid_counter
        pid_counter += 1
        if data["new"]:
            gid = randint(1000000, 9999999)
            while gid in GameDict:
                gid = randint(1000000, 9999999)
            Thread(target=init_game, args=([gid])).start()
            sleep(0.1)
            GameDict[gid]["players"][conn] = pid
            send_msg(conn, {"gid": gid, "pid": pid, "points": GameDict[gid]["points"]})
        else:
            gid = int(data["gid"])
            gd = GameDict[gid]
            gd["players"][conn] = pid
            if gd["closed"]:
                Thread(target=handle_game, args=([gid])).start()
            elif len(list(GameDict[gid]["players"].keys())) == 1:
                GameDict[gid]["drawing"] = list(GameDict[gid]["players"].values())[0]
                to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                           "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
                send_msg(conn, {"gid": gid, "pid": pid, "points": GameDict[gid]["points"]})
                send_msg(conn, to_send)
        print(str(addr), "has connected, with the id of", pid)


if __name__ == "__main__":
    Thread(target=handle_connection).start()
    while running:
        cmnd = input(">")
        if cmnd == "close":
            running = False
    for game in GameDict.values():
        game["players"] = {}
        game["closed"] = True
    with open("server_log.txt", "w") as file:
        print("\"making a database\"")
        file.write(pformat(GameDict))
    print("done")
    with open("dict.pickle", "wb") as file:
        print("making a database")
        pickle.dump(GameDict, file)
        print("done")

    exit()
