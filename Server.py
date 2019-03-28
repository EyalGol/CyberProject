import pickle
from select import select
from threading import Thread
from sys import exit
from pprint import pformat
from random import randint, choice
from time import sleep, time
from utility import *
from copy import deepcopy as copy
from queue import Queue
from Crypto.PublicKey import RSA

private_key = RSA.generate(2048)
public_key = private_key.publickey()

SOCKET_TIME_OUT = 5
MAX_CONNECTIONS = 30
PORT = 3345
BACKUP_TIME = 60
RANDOM_LIST = ['beef', 'photo album', 'water bottle', 'toothpaste', 'clothes', 'picture frame', 'pen', 'bowl',
               'stop sign', 'bread', 'lotion', 'bracelet', 'soap', 'clay pot', 'cat', 'carrots', 'spring', 'box',
               'cell phone', 'socks', 'needle', 'wagon', 'USB drive', 'food', 'spoon', 'shampoo', 'candy wrapper',
               'mop', 'shoe lace', 'sponge', 'desk', 'piano', 'charger', 'flowers', 'buckel', 'video games', 'shovel',
               'soda can', 'seat belt', 'helmet', 'bag', 'tissue box', 'door', 'tomato', 'mouse pad', 'teddies',
               'pillow', 'truck', 'playing card', 'sun glasses', 'brocolli', 'fridge', 'coasters', 'button', 'keyboard',
               'computer', 'bed', 'bottle', 'mirror', 'pool stick', 'speakers', 'house', 'candle', 'mp3 player',
               'slipper', 'knife', 'camera', 'chocolate', 'drill press', 'toilet', 'fork', 'bow', 'radio', 'table',
               'newspaper']
server_running = True
# init global vars:
try:
    with open("back_up.pickle", "rb") as file:
        GameDict = pickle.load(file)
        for lobby in GameDict.values():
            lobby["players"] = {}
except Exception as err:
    print("restoration from backup failed:", err)
    GameDict = {}
for lobby in GameDict.values():
    lobby["running"] = False
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", PORT))
print("binding successful")


def init_new_lobby(gid):
    """
    initiates a "table" for a new lobby with the key of gid
    :param gid: key for the table
    :return: nothing
    """
    GameDict[gid] = {}
    gd = GameDict[gid]
    gd["chat_log"] = []
    gd["players"] = {}
    gd["points"] = []
    gd["clear"] = False
    gd["drawing"] = None
    gd["last_won"] = None
    gd["running"] = False
    gd["answer"] = choice(RANDOM_LIST)


def get_player_by_conn(gid, conn):
    """
    Gets a player PID from GameDict by his connection
    :param gid: the player lobbies ID
    :param conn: the players connection
    :return: the players PID
    """
    gd = GameDict[gid]
    try:
        for pid, conn_cipher in gd["players"].items():
            if conn_cipher[0] == conn:
                return pid
    except Exception as err:
        print("wasn't able to get key by val:", err)


def handle_lobby(gid):
    """
    handles a new lobby
    :param gid: the lobbies ID
    :return: Nothing
    """
    gd = GameDict[gid]
    gd["running"] = True
    start_time = time()
    while server_running:
        if gd["players"]:
            sockets = [conn_cipher[0] for conn_cipher in gd["players"].values()]
            try:
                readl, writel, _ = (sockets, sockets, [])
            except Exception as err:
                print("gid:", gid, "select failed:", err)
                readl, writel = [], []
            if readl:
                for conn in readl:
                    recv_from_client(conn, gid)

            if writel:
                to_send = to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                                     "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
                for conn in writel:
                    send_to_client(conn, gid, to_send)
            gd["clear"] = False
            sleep(0.2)
        else:
            if time() - start_time > 200:
                gd["running"] = False
                break


def send_to_client(conn, gid, to_send):
    """
    handles sending data to a client
    :param conn: client connection (socket)
    :param gid: the lobby the player belongs to
    :param to_send: data meant to be sent
    :return: Nothing
    """
    gd = GameDict[gid]
    try:
        pid = get_player_by_conn(gid, conn)
        data = send_thread(gd["players"][pid][1], conn, to_send)
        if not data:
            print("player", pid, "has disconnected")
            conn.close()
            del gd["players"][pid]
    except Exception as err:
        print("failed to send data to a client:", err)


def recv_from_client(conn, gid):
    """
    handles receiving and sorting data from a client
    :param conn: the clients connection (socket)
    :param gid: the lobby the player belongs to
    :return: Nothing
    """
    try:
        gd = GameDict[gid]
        pid = get_player_by_conn(gid, conn)
        data = recv_msg(gd["players"][pid][1], conn)
        if not data:
            pid = get_player_by_conn(gid, conn)
            print("player", pid, "has disconnected")
            conn.close()
            del gd["players"][pid]
        else:
            if data["failed"]:
                pass
            elif data["is_drawing"]:
                gd["points"] = data["points"]
            else:
                gd["chat_log"].append(data["msg"])
                if str(data["msg"]).strip().lower() == str(gd["answer"]).strip().lower():
                    gd["last_won"] = get_player_by_conn(gid, conn)
                    gd["answer"] = choice(RANDOM_LIST)
                    gd["drawing"] = choice(list(gd["players"].keys()))
                    gd["clear"] = True
                else:
                    gd["clear"] = False
                while len(gd["chat_log"]) > 24:
                    gd["chat_log"] = gd["chat_log"][1:]
    except KeyError as err:
        print("failed to receive data from a client:", err)
    except AttributeError as err:
        print("failed to receive data from a client:", err)


def accept_client_connections():
    """
    Starts as a thread and handles new connections and new lobbies
    :return: Nothing
    """
    server.listen(MAX_CONNECTIONS)
    print("Server is open")
    while server_running:
        conn, addr = server.accept()
        conn.settimeout(SOCKET_TIME_OUT)
        init_key_exchange(public_key, conn)
        AES_key = recv_session_key(private_key, conn)
        cipher_aes = AES.new(AES_key, AES.MODE_EAX)
        data = recv_msg(cipher_aes, conn)
        if data:
            # if the client asked to build a new lobby for him
            if data["new"]:
                gid = randint(10000, 99999)
                while gid in GameDict:
                    gid = randint(10000, 99999)
                init_new_lobby(gid)
                Thread(target=handle_lobby, args=([gid])).start()

            # if the client asks to connect to an existing lobby
            else:
                try:
                    gid = int(data["gid"])
                except Exception as err:
                    print(addr, "tried to connect but entered a false gid", err)

            # checks if the lobby is running atm if not opens a new thread for it
            if not GameDict[gid]["running"]:
                Thread(target=handle_lobby, args=(gid,)).start()

            # ensures that the client pid is unique
            while data["pid"] in GameDict[gid]["players"]:
                data["pid"] += "1"
            pid = data["pid"]

            # if the lobby was empty entitles the player as the drawer
            if not GameDict[gid]["players"]:
                GameDict[gid]["drawing"] = pid

            # initial communication
            gd = GameDict[gid]
            send_msg(cipher_aes, conn, {"gid": gid, "pid": pid, "points": GameDict[gid]["points"]})
            to_send = {"drawing": gd["drawing"], "points": gd["points"], "chat_log": gd["chat_log"],
                       "answer": gd["answer"], "last_won": gd["last_won"], "clear": gd["clear"]}
            send_msg(cipher_aes, conn, to_send)
            GameDict[gid]["players"][pid] = (conn, cipher_aes)
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
            gdict = copy(GameDict)
            for lobby in gdict.values():
                lobby["players"] = {}
            with open("back_up.pickle", "wb") as file:
                print("backing up")
                pickle.dump(gdict, file)
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
    # start backup thread
    Thread(target=backup).start()

    # start client handling
    Thread(target=accept_client_connections).start()

    # look out for client input
    while server_running:
        cmnd = input(">")
        if cmnd == "close":
            server_running = False
    # writs a human readable log if the client closes the server
    with open("server_log.txt", "w") as file:
        print("writing log")
        file.write(pformat(GameDict))
    print("done")
    # backup before exit
    backup(True)
    exit()
