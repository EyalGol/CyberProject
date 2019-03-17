import socket
import pickle
from select import select
from threading import Thread
from sys import exit
from pprint import pformat
from random import randint, choice
from time import sleep, time
from utility import *

MAX_CONNECTIONS = 30
PORT = 3345
BACKUP_TIME = 60
RANDOM_LIST = ['beef', 'photo album', 'water bottle', 'toothpaste', 'grid paper', 'clothes', 'picture frame', 'pen',
               'bowl', 'stop sign', 'bread', 'lotion', 'bracelet', 'soap', 'clay pot', 'cat', 'carrots', 'spring',
               'box', 'cell phone', 'socks', 'needle', 'wagon', 'USB drive', 'food', 'spoon', 'shampoo',
               'candy wrapper', 'mop', 'shoe lace', 'sponge', 'desk', 'piano', 'charger', 'flowers', 'buckel',
               'video games', 'shovel', 'soda can', 'seat belt', 'helmet', 'bag', 'tissue box', 'door', 'tomato',
               'mouse pad', 'teddies', 'pillow', 'truck', 'playing card', 'sun glasses', 'brocolli', 'fridge',
               'coasters', 'button', 'keyboard', 'computer', 'bed', 'bottle', 'mirror', 'pool stick', 'speakers',
               'house', 'candle', 'mp3 player', 'slipper', 'knife', 'camera', 'chocolate', 'drill press', 'toilet',
               'fork', 'bow', 'radio', 'table', 'newspaper']

server_running = True
# init global vars:
try:
    with open("back_up.pickle", "rb") as file:
        GameDict = pickle.load(file)
except Exception as err:
    print("restoration from backup failed:", err)
    GameDict = {}
for lobby in GameDict.values():
    lobby["running"] = False
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", PORT))
print("binding successful")


def init_new_lobby(gid):
    GameDict[gid] = {}
    gd = GameDict[gid]
    gd["chat_log"] = []
    gd["players"] = {}
    gd["points"] = []
    gd["clear"] = False
    gd["last_won"] = None
    gd["running"] = False
    gd["answer"] = choice(RANDOM_LIST)


def delete_player(gid, conn_dell):
    gd = GameDict[gid]
    for pid, conn in gd["players"].items():
        if conn == conn_dell:
            del gd["players"][pid]
            break


def handle_lobby(gid):
    gd = GameDict[gid]
    gd["running"] = True
    while server_running:
        if gd["players"]:
            try:
                readl, writel, _ = select(gd["players"].values(), gd["players"].values(), [])
            except Exception as err:
                print("gid:", gid, "select failed:", err)
                readl, writel = [], []
            if readl:
                try:
                    for conn in readl:
                        data = recv_msg(conn)
                        if not data:
                            conn.close()
                            delete_player(gid, conn)
                        else:
                            if data["is_drawing"]:
                                gd["points"] = data["points"]
                            else:
                                gd["chat_log"].append(data["msg"])
                                if data["msg"] == gd["answer"]:
                                    gd["last_won"] = gd["players"][conn]
                                    gd["answer"] = choice(RANDOM_LIST)
                                    gd["drawing"] = choice(list(gd["players"].keys()))
                                    gd["clear"] = True
                                else:
                                    gd["clear"] = False
                except Exception as err:
                    print(err)
            try:
                if writel:
                    to_send = to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                                         "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
                    for conn in writel:
                        data = send_msg(conn, to_send)
                        if not data:
                            conn.close()
                            delete_player(gid, conn)
                gd["clear"] = False
                sleep(0.1)
            except Exception as err:
                print(err)


def accept_client_connections():
    """
    Starts as a thread and handles new connections and new lobbies
    :return: Nothing
    """
    server.listen(MAX_CONNECTIONS)
    print("Server is open")
    while server_running:
        conn, addr = server.accept()
        data = recv_msg(conn)
        if data:
            if data["new"]:
                gid = randint(10000, 99999)
                while gid in GameDict:
                    gid = randint(10000, 99999)
                init_new_lobby(gid)
                Thread(target=handle_lobby, args=([gid])).start()
            else:
                try:
                    gid = int(data["gid"])
                except Exception as err:
                    print(addr, "tried to connect but entered a false gid", err)
            if not GameDict[gid]["running"]:
                Thread(target=handle_lobby, args=([gid])).start()
            while data["pid"] in GameDict[gid]["players"]:
                data["pid"] += "1"
            pid = data["pid"]
            was_empty = True if not GameDict[gid]["players"] else False
            if was_empty:
                GameDict[gid]["drawing"] = pid
            gd = GameDict[gid]
            send_msg(conn, {"gid": gid, "pid": pid, "points": GameDict[gid]["points"]})
            to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                       "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
            send_msg(conn, to_send)
            GameDict[gid]["players"][pid] = conn
            print(str(addr), "has connected, as:", pid)
        else:
            print("connection failed:", addr)


def backup(do_now=None):
    """
    backups the server every BACKUP_TIME seconds (start as a thread)
    :param do_now: if do_now is True the the instant the backup is called the server will backup
    :return: Nothing
    """

    def write_backup():
        try:
            for lobby in GameDict.values():
                lobby["players"] = {}
            with open("back_up.pickle", "wb") as file:
                print("backing up")
                pickle.dump(GameDict, file)
                print("done")
        except Exception as err:
            print("backup failed:", err)

    if do_now:
        write_backup()
    o_time = time()
    while server_running:
        if time() - o_time > BACKUP_TIME:
            write_backup()
            o_time = time()
        sleep(20)


if __name__ == "__main__":
    Thread(target=backup).start()
    Thread(target=accept_client_connections).start()
    while server_running:
        cmnd = input(">")
        if cmnd == "close":
            server_running = False
    with open("server_log.txt", "w") as file:
        print("writing log")
        file.write(pformat(GameDict))
    print("done")

    backup(True)
    exit()
