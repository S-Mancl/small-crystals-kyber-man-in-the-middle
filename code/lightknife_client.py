from smallkyber import SmallKyber

from shutil import get_terminal_size
import os
import keyboard
import string
import time
import socket
from sympy.parsing.sympy_parser import parse_expr
import secrets

from AESCipher import AESCipher
from getch import _Getch
getch = _Getch()

status = {
    "logs" : [
        ],
    "messages": [
        ],
    "command" : ":h",
    "mode" : "Command",
    "connstatus": "DISCONNECTED",
    "tmpmessage" : "",
    "KEY": 0,
    "AES": None

}

def logSuccess(msg):
    status["logs"].append(str(int(time.time()))+" [SUCCESS] "+msg)
    DrawFrame()


def logInfo(msg):
    status["logs"].append(str(int(time.time()))+" [INFO]    "+msg)
    DrawFrame()

def logWarning(msg):
    status["logs"].append(str(int(time.time()))+" [WARNING] "+msg)
    DrawFrame()

def logError(msg):
    status["logs"].append(str(int(time.time()))+" [ERROR]   "+msg)
    DrawFrame()

def columns():
    return get_terminal_size().columns
def rows():
    return get_terminal_size().lines

def DrawTitle():
    if columns() < len("LightKnife")+2:
        print("┃" + " "*((columns()-2-len("LK"))//2)+"LK" +  " "*((columns()-2-len("LK"))//2+columns()%2) +"┃")
    elif columns() < len("LightKnife: an elegant chat tool for a more civilized age")+2:
        print("┃" + " "*((columns()-2-len("LightKnife"))//2)+"LightKnife" +  " "*((columns()-2-len("LightKnife"))//2+columns()%2) +"┃")
    else:
        print("┃" + " "*((columns()-2-len("LightKnife: an elegant chat tool for a more civilized age"))//2)+"LightKnife: an elegant chat tool for a more civilized age" +  " "*((columns()-2-len("LightKnife: an elegant chat tool for a more civilized age"))//2+(columns()%2+1)%2) +"┃")

def DrawBar():
    print("┣" + "━"*(columns()-2)+"┫")

def DrawLogs(maximum_length):
    logs = status["logs"]
    # TODO update anche qui la lunghezza dei logs
    if len(logs) > maximum_length:
        len_logs = maximum_length
    else:
        len_logs = len(logs)
    for entry in logs[-len_logs:]:
        print("┃ "+entry[:(columns()-4)]+" "*(columns()-4-min(len(entry),columns()-4)) + " ┃")
    for _ in range(maximum_length-len_logs):
        print("┃"+" "*(columns()-2)+"┃")

def DrawMessages():
    messages = status["messages"]
    val = rows()-7
    # val non può essere > 20 in teoria
    if val > 20:
        val = 20
    for entry in messages[-val:]:
        print("┃ "+entry[:(columns()-4)]+" "*(columns()-4-min(len(entry),columns()-4)) + " ┃")
    for _ in range(max(val-len(messages),0)):
        print("┃"+" "*(columns()-2)+"┃")


def DrawCommands():
    # cosa devo stampare?
    #   - modalità in cui sono
    #   - eventuale comando mezzo typato
    #   - stato della connessione?
    print("┃",end='') # inizio la riga 
    # stato della connessione
    if (columns()-15-8-4-4) > 15:
        if status["connstatus"] == "CONNECTED":
            statusstring = " \x1b[42mCONNECTED   \x1b[0m ┃"
        elif status["connstatus"] == "CONNECTING":
            statusstring = " \x1b[44mCONNECTING  \x1b[0m ┃"
        elif status["connstatus"] == "DISCONNECTED":
            statusstring = " \x1b[41mDISCONNECTED\x1b[0m ┃"
        print(statusstring,end='')
    # TODO renderlo responsive
    # eventuale comando mezzo typato
    if status["mode"] == "Command":
        if (columns()-15-8-4-4) > 15:
            print(" "+status["command"] + " "*(columns()-28-len(status["command"])),end='')
        else:
            print(" " + status["command"] + " "*(columns()-3-len(status["command"])),end='')
    elif status["mode"] == "Insert":
        if (columns()-15-8-4-4) > 15:
            print(" "+status["tmpmessage"] + " "*(columns()-28-len(status["tmpmessage"])),end='')
        else:
            print(" " + status["tmpmessage"] + " "*(columns()-3-len(status["tmpmessage"])),end='')
    else:
        if (columns()-15-8-4-4) > 15:
            print(" "*(columns()-27),end='')
        else:
            print(" "*(columns()-2),end='')

        # status mode is command
        pass
    # TODO
    # modalità in cui sono
    if (columns()-15-8-4-4) > 15:
        if status["mode"] == "Insert":
            statusstring = "┃ \x1b[44mInsert \x1b[0m "
        elif status["mode"] == "Logs":
            statusstring = "┃ \x1b[41mLogs   \x1b[0m "
        elif status["mode"] == "Command":
            statusstring = "┃ \x1b[42mCommand\x1b[0m "
        print(statusstring,end='')

    # TODO 
    print("┃") # finisco la riga


def DrawFooter():
    DrawBar()
    DrawCommands()
    print("╰"+"━"*(columns()-2)+"╯",end='\r')
 
def DrawFooterWrapper():
    print("\033[3F")
    DrawFooter()

def DrawFrame():
    os.system("clear")
    print("╭" + "━"*(columns()-2)+"╮")
    # draw everything
    DrawTitle()
    DrawBar()
    if rows() > 7 + 20: # 20: lunghezza assolutamente arbitraria della parte di chat
        DrawLogs(rows()-7-20)
        DrawBar()
    DrawMessages()
    DrawFooter()

def findOther(name:str):
    if name == "Alderaan":
        return "Tatooine"
    elif name == "Tatooine":
        return "Alderaan"
    else:
        return "Unknown"

"""
interaction with the server
"""

def sendbytes(to_send:bytes) -> bytes:
    HOST = '42.42.42.4'
    PORT = 4242
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        s.sendall(to_send)
        data = b''
        while True:
            tmpdata = s.recv(1024)
            data += tmpdata
            if len(tmpdata)<1024:
                return data

def connect():
    sk = SmallKyber()
    status["connstatus"] = "CONNECTING"

    tipo = int(2).to_bytes(1,'big')
    data = sendbytes(tipo)
    if b'yes' in data:
        logInfo("You can start a conversation. Please exchange params")
        [t,rho],secret = sk.CPA_KeyGen()
        logSuccess("Keys for Kyber.KEM generated")
        # transform t and rho to bytes
        msg = b''
        for item in t:
            msg += str(item).encode() + b','
        msg = msg[:-1]
        msg += b'|||||'+rho.to_bytes(32,'big')
        # END transform t and rho
        tipo = int(4).to_bytes(1,'big')
        data = sendbytes(tipo+msg)
        print("Keys sent")
        while True:
            # continuo a chiedere se l'altro ha incapsulato la chiave... spero di sì, lo spero proprio, nel dubbio continuo a rompere l'anima
            logInfo("Is the encaps ready?")
            tipo = int(6).to_bytes(1,'big')
            data = sendbytes(tipo)
            if b'wait' in data:
                time.sleep(3)
            else:
                logSuccess("The encapsed is ready...")
                break
        # get u,v from message
        u_and_v = data.decode()
        tmp_u,v = u_and_v.split("|||||")
        v = parse_expr(v)
        u = [
                parse_expr(item) for item in tmp_u.split(",") 
            ]
        # END get u,v
        K = sk.Decaps(secret,secrets.randbelow(2**256),t,rho,u,v)
        logSuccess("Decapsulated successfully")
        status["KEY"] = K
        status["connstatus"] = "CONNECTED"

    elif b'no' in data:
        logInfo("We'll let you know when someone tries to connect")
        while True:
            # continuo a cercare di mettermi in contatto usando lo status 3
            #finché mi dice di no vado avanti, altrimenti mi risponde con t e rho
            logInfo("Are keys available?")
            tipo = int(3).to_bytes(1,'big')
            data = sendbytes(tipo)
            if b'wait' in data:
                time.sleep(3)
            else:
                logSuccess("Keys are available")
                break
        # get t and rho from the comm
        [t_temp,rho] = data.split(b'|||||')
        t_temp = t_temp.decode()
        rho = int.from_bytes(rho,'big')
        t = [
                parse_expr(item) for item in t_temp.split(",")
            ]
        # END get t and rho
        u,v, K = sk.Encaps(t,rho)
        logSuccess("Encapsulated key")
        # transform encapsulated to bytes
        msg = b''
        for item in u:
            msg += str(item).encode() + b','
        msg = msg[:-1]
        msg += b'|||||'
        msg += str(v).encode()
        # END transform encapsulated to bytes
        tipo = int(5).to_bytes(1,'big')
        logSuccess("Encapsulated sent")
        data = sendbytes(tipo+msg)
        status["KEY"] = K
        status["connstatus"] = "CONNECTED"

    status["AES"] = AESCipher(status["KEY"])
    logInfo("TEMPORARY: the key is "+str(status["KEY"]))

def sendMessage(msg_:str):
    HOST = '42.42.42.4'
    PORT = 4242
    msg = status["AES"].encrypt(msg_)
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        tipo = int(0).to_bytes(1,'big')
        s.sendall(tipo+msg)
        data = b''
        while True:
            tmpdata = s.recv(1024)
            data += tmpdata
            if(len(tmpdata)<1024):
                break
        if b'done' in data:
            status["messages"].append("["+socket.gethostname()+"] -> ["+findOther(socket.gethostname())+"]: "+msg_)
            logSuccess("message sent")
            DrawFrame()
        else:
            logError("failed to send message")
            DrawFrame()

def getMessages():
    HOST = '42.42.42.4'
    PORT = 4242
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
        tipo = int(1).to_bytes(1,'big') # I want my messages please
        s.sendall(tipo)
        data = b''
        while True:
            tmpdata = s.recv(1024)
            data += tmpdata
            if(len(tmpdata)<1024):
                break
        if len(data) > 0 and not b"NOMESSAGES" in data:
            for msg in [status["AES"].decrypt(i) for i in data.split(b"|||||")]:
                status["messages"].append(
                    "["+findOther(socket.gethostname())+"] -> ["+socket.gethostname()+"]: "+msg
                )
            logSuccess("messages fetched")
            DrawFrame()
        else:
            logError("failed to fetch messages")
            DrawFrame()


def submitCommand():
    #:connect
    if status["command"] in [":connect"]:
        connect()
    #:q/quit/wq/wqa/writequit/writequitall
    if status["command"] in [":q",":quit",":wq",":wqa",":writequit",":writequitall"]:
        os.system("clear")
        os._exit(0)
    #:h/help
    # TODO
    #:r/refresh
    if status["command"] in [":r",":refresh"]:
        getMessages()
        DrawFrame()
    else:
        status["command"] = ""
        DrawFrame()
    pass

def submitMessage():
    if status["tmpmessage"] == "":
        return
    if status["connstatus"] != "CONNECTED":
        logError("You must be connected to send a message")
    else:
        sendMessage(status["tmpmessage"])
    status["tmpmessage"] = ""
    DrawFrame()
    pass

hitTime = 0
def pressed_printable(character):
    if character == '\x1b':
        pressedEsc()
    global status, hitTime
    if time.time() - hitTime < 0.03:
        return
    else:
        hitTime = time.time()
        if status["mode"] == "Command":
            if not status["command"].startswith(":"):
                if ":" in character:
                    status["command"] = ":"
                elif "i" in character:
                    status["mode"] = "Insert"
                elif "l" in character:
                    status["mode"] = "Logs"
                    # TODO interpret as command
                DrawFooterWrapper()
                pass
            elif character in string.ascii_letters or character in string.digits or character in string.punctuation:
                status["command"] += character
                DrawFooterWrapper()
            elif character == " ":
                status["command"] += " "
            elif '\x7f' == character:
                status["command"] = status["command"][:-1]
                DrawFooterWrapper()
            elif character == '\r' or character == '\n':
                submitCommand()
        elif status["mode"] == "Insert":
            if character in string.ascii_letters or character in string.digits or character in string.punctuation:
                status["tmpmessage"] += character
                DrawFooterWrapper()
            elif character == " ":
                status["tmpmessage"] += " "
            elif '\x7f' == character:
                status["tmpmessage"] = status["tmpmessage"][:-1]
                DrawFooterWrapper()
            elif character == '\r' or character == '\n':
                submitMessage()


def pressedEsc():
    global status
    if status["mode"] == "Command":
        status["command"] = ""
    else:
        status["mode"] = "Command"
    #print("\033[3F")
    DrawFooterWrapper()


logInfo("System Starting as "+socket.gethostname()+"...")
DrawFrame()

_rows = rows()
_columns = columns()

while True:
    pressed_printable(getch())
    oldrows = _rows
    oldcolumns = _columns
    if rows() != _rows or columns() != _columns:
        DrawFrame()
        _rows = rows()
        _columns = columns()

    pass
