import socket
from select import select
from json import dumps,loads
from threading import Thread
from random import randint

GameDict = {}
pid_counter = 0

def handle_client():
    pass

def handle_connection(skt):
    global GameDict, pid_counter
    conn, addr = skt.accept()
    json_dump = loads(conn.recv(1024).decode())
    if json_dump["new"]:
        gid = ""
        for x in range(6):
            gid += str(randint(0, 10))
        gid = int(gid)
    else:
        gid = json_dump["gid"]
    pid = pid_counter
    pid_counter += 1
    conn.sendall(dumps({"gid": gid, "pid": pid}).encode())

if __name__ == "__main__":
    server = socket.socket()
    server.bind(("localhost", 3345))
    server.listen(30)
    Thread(target=handle_connection, args=(server)).start()
    while True:
        pass
