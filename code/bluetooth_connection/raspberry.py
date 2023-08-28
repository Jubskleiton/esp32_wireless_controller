from random import randint
import socket
import pickle
import threading
from time import sleep

CLIENT_ID = randint(0, 100)

HEADER = 1024
DISCONNECT_MESSAGE = "!DISCONNECT"
FORMAT = 'utf-8'
MAC_ADDRESS = "b4:8c:9d:5b:7d:ee" #
CHANNEL = 4 # 1 - 20
ADDR = (MAC_ADDRESS, CHANNEL)

NICKNAME = "Raspberry"


def send(data, head=HEADER):
    # serialize data
    message = pickle.dumps(data)
    # measure message size
    msg_len = len(message)
    print(msg_len)
    # convert message length to bytes
    send_len = msg_len.to_bytes(head, byteorder='big')
    # send length
    client.send(send_len)
    # send message
    client.send(message)

def receive(head=HEADER):
    # receive message length
    send_len = client.recv(head)
    msg_len = int.from_bytes(send_len, byteorder='big')
    # verify connection message (effectively None message)
    if msg_len:
        # receive message and deserialize
        return pickle.loads(client.recv(msg_len))
    else:
        return {}

def terminal_input():
    while True:
        method = input("1: Send log message\n2: Send power level\3e: Exit\nWhat to do: ")
        match  method:
            case "1":
                send({"method":"log", "log":input("log: ")})
            case "2":
                send({"method":"RGB", "R":input("R: "), "G":input("G: "), "B":input("B: ")})
            case "e":
                send({"method": DISCONNECT_MESSAGE})
                exit()


client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

print("reaching to connect")
client.connect(ADDR)
print("connected")
print("initializing")
sleep(1)
receive_data_thread = threading.Thread(target=terminal_input, daemon=True)
receive_data_thread.start()

send({"nickname": NICKNAME})

while True:
    data = receive()
    if data.get("method") == DISCONNECT_MESSAGE:
        break
    else:
        if data.get("method") == "log":
            print(data.get("log"))
        elif data.get("method") == "RGB":
            print(f'R: {data.get("R")} G: {data.get("G")} B: {data.get("B")}')
        else:
            print(f"{data.get('method')} method received was not expected, ignoring command")


client.close()
print("exited")
exit()