import socket  # Import socket module
from AESCipher import AESCipher
import sys
from smallkyber import SmallKyber
from sympy.parsing.sympy_parser import parse_expr
from AESCipher import AESCipher

oldMessages = {
    "Alderaan":[],
    "Tatooine":[]
}

messagesFor = {
        "Alderaan":[],
        "Tatooine":[]
    }

status = {
        "waiting" : False,
        "keys available": False,
        "key message": b'',
        "encapsed": b'',
        "encapsed available" : False
        }

def nameof(address):
    if '42.42.42.2' in address:
        return "Alderaan"
    elif '42.42.42.3' in address:
        return "Tatooine"
    else:
        return "Unknown"

def notnameof(address):
    if nameof(address) == "Alderaan":
        return "Tatooine"
    elif nameof(address) == "Tatooine":
        return "Alderaan"
    else:
        return "Unknown"

def other(name):
    if name == "Alderaan":
        return "Tatooine"
    elif name == "Tatooine":
        return "Alderaan"
    else:
        return "Unknown"


### LEGAL FUNCTIONS
def prepare_bytes(from_name:str):
    msg = b''
    for item in messagesFor[from_name]:
        msg += item
        msg += b'|'
        oldMessages[from_name].append(msg)
    messagesFor[from_name] = []
    if len(msg)==0:
        msg = b'NOMESSAGES!'
    return msg[:-1]

def appendMessage(data:bytes,from_addr):
    print("😶 Encrypted",data.decode())
    messagesFor[notnameof(from_addr)].append(data)

def evalRequest(data:bytes,from_addr):
    if len(data)<1:
        return b''
    else:
        header = data[0] # può essere fetch o put
        #print(header,type(header),data[1:],type(data[1:]))
        if header == 0:
            print("🪐\x1b[43m"+nameof(from_addr)+"\x1b[0m","I want to push a message")
            appendMessage(data[1:],from_addr)
            return b'done'
        elif header == 1:
            print("\x1b[43m"+nameof(from_addr)+"\x1b[0m","I want my messages")
            return prepare_bytes(nameof(from_addr))
        elif header == 2: # someone?
            print("\x1b[43m"+nameof(from_addr)+"\x1b[0m","Is someone there?")
            if status["waiting"] == 0:
                status["waiting"] = True
                return b'no'
            else:
                status["waiting"] = False
                return b'yes'
        elif header == 3: # keys please?
            print("\x1b[43m"+nameof(from_addr)+"\x1b[0m","Can I have the keys?")
            if status["keys available"] == True:
                status["keys available"] = False
                return status["key message"]
            else:
                return b'wait'
        elif header == 4: # here are the keys
            print("\x1b[43m"+nameof(from_addr)+"\x1b[0m","Here are the keys")
            status["key message"] = data[1:]
            status["keys available"] = True
        elif header == 5: # here is the encapsed
            print("\x1b[43m"+nameof(from_addr)+"\x1b[0m","Here's the encapsed")
            status["encapsed"] = data[1:]
            status["encapsed available"] = True
        elif header == 6: # encaps please?
            print("\x1b[43m"+nameof(from_addr)+"\x1b[0m","Can I have the encapsed?")
            if status["encapsed available"] == True:
                status["encapsed available"] = False
                return status["encapsed"]
            else:
                return b'wait'
        else:
            return b'unrecognized command'
    return data
###


### NOT SO LEGAL FUNCTIONS
t, rho, secret = [0,0,0]
t_rho = 0
K = {}

def setUpEvil():
    global t, rho, secret,t_rho
    sk = SmallKyber()
    [t,rho],secret = sk.CPA_KeyGen()
    # TODO encode into t_rho
    msg = b''
    for item in t:
        msg += str(item).encode() + b','
    msg = msg[:-1]
    msg += b'|'+rho.to_bytes(32,'big')
    t_rho = msg

def edit(plaintext:str):
    return plaintext\
        .replace("evil","goood")\
        .replace("good","evil")\
        .replace("goood","good")

def appendMessageEvil(message,from_addr):
    plaintext = AESCipher(K[nameof(from_addr)]).decrypt(message)
    print("☠️Deathstar",plaintext)
    print("☠️Deathstar",edit(plaintext))
    messagesFor[notnameof(from_addr)].append(AESCipher(K[notnameof(from_addr)]).encrypt(edit(plaintext)))

def evalEvil(data:bytes,from_addr):
    if len(data)<1:
        return b''
    else:
        header = data[0] # può essere fetch o put
        #print(header,type(header),data[1:],type(data[1:]))
        if header == 0: # TODO
            print("🪐\x1b[43m"+nameof(from_addr)+"\x1b[0m","I want to push a message")
            appendMessageEvil(data[1:],from_addr)
            return b'done'
        elif header == 1: # TODO
            print("🪐\x1b[43m"+nameof(from_addr)+"\x1b[0m","I want my messages")
            return prepare_bytes(nameof(from_addr))
        elif header == 2: # someone?
            print("🪐\x1b[43m"+nameof(from_addr)+"\x1b[0m","Is someone there?")
            return b'no'
        elif header == 3: # keys please? send t_rho
            print("🪐\x1b[43m"+nameof(from_addr)+"\x1b[0m","Can I have the keys?")
            return t_rho
        elif header == 4: # here are the keys should not happen
            pass
        elif header == 5: # here is the encapsed: decaps here
            print("🪐\x1b[43m"+nameof(from_addr)+"\x1b[0m","Here's the encapsed")
            # TODO get u,v
            data = data[1:]
            u_and_v = data.decode()
            tmp_u,v = u_and_v.split("|")
            v = parse_expr(v)
            u = [
                    parse_expr(item) for item in tmp_u.split(",") 
                ]
            global K
            K[nameof(from_addr)] = SmallKyber().Decaps(secret,42,t,rho,u,v)
            print("☠️Deathstar: Decapsed from "+nameof(from_addr))
        elif header == 6: # encaps please? should not happen
            pass
        else:
            return b'unrecognized command'
    return data



###
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--evil":
        evil = True
        setUpEvil()
    else:
        evil = False
    port = 4242  # Reserve a port for your service every new transfer wants a new port or you must wait.
    s = socket.socket()  # Create a socket object
    host = "42.42.42.4"  # Get local machine name
    s.bind((host, port))  # Bind to the port
    s.listen(5)  # Now wait for client connection.

    print('LightKnife server listening....')

    while True:
        conn, address = s.accept()  # Establish connection with client.

        try:
            #print('Got connection from', address, nameof(address))
            data = b''
            while True:
                tmpdata = conn.recv(1024)
                data += tmpdata
                if len(tmpdata)<1024:
                    break
            if not evil:
                conn.send(evalRequest(data,address))
            else:
                conn.send(evalEvil(data,address))

        except Exception as e:
            print(e)
            break

    conn.close()

