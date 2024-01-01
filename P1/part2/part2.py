import socket
from struct import pack, unpack
import random

# set up global variables
chunk_size = 1024
align = 4
timeout = 3
header = 12

# socket vars
ip   = "127.0.0.1"
port = 12235

# set up socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((ip, port))
print("Listening! (A)")

# set up test vars
default_sec = 0
step = 2

# Bro I despise python why do I have to put this here to use a global var wtf is this
def ClientConnect(message, cip):
    # Part A
    print("Testing part A!")
    plen, psec, temp, id = unpack('>iihh', message[0:header])
    pload = message[header:header + plen]
    
    # Validate part a
    parta = "hello world\0"
    if psec != default_sec:
        # Invalid secret
        print("Invalid secret!")
        return
    if pload != parta.encode():
        # Invalid payload
        print("Invalid payload!")
        return
    if header + len(parta) != len(message) or temp != 1:
        # Invalid length check
        print("Invalid length or step!", plen)
        return
    
    # Part A is validated
    num = random.randint(1, 16)
    length = random.randint(24, 200)
    port = random.randint(20000, 30000)
    secret = random.randint(1, 100)
    res = pack('>iihhiiii', 16, psec, step, id, num, length, port, secret)

    # Send to client
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(res, cip)
    sock.close()

    print("Testing part B!")
    # Build new socket connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    sock.settimeout(timeout)
    print("Listening! (B)")

    # get expected length
    acked = 0
    paylen = align + header + length + ((align - length % align) % align)
    while acked < num:
        # Try to recieve message, get out if fails
        try:
            message = sock.recv(chunk_size)
        except:
            print("Socket closed unexpectedly")
            return
        
        # Get and validate variables
        plen, psec, temp, id2, pid = unpack('>iihhi', message[0: header + align])
        if psec != secret or id2 != id:
            print("Invalid secret to id mapping!")
            return
        if pid != acked or temp != 1:
            print("Packet number or temp not matching!")
            return
        if plen != length + align or len(message) != paylen:
            print("Len not matching! ", plen," ", paylen, " ", len(message), " ", length + align)
            return

        # Build response
        res = pack('>iihhi', align, secret, step, id, pid)
        sock.sendto(res, cip)
        acked = acked + 1

    # Build res msg    
    port =  random.randint(20000, 32000)
    newsecret = random.randint(1, 100)

    res = pack('>iihhii', align, secret, step, id, port, newsecret)
    secret = newsecret

    sock.sendto(res, cip)
    sock.close()

    # Open TCP Port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.bind((ip, port))
    sock.listen()

    print("Listening! (C, D)")
    con, caddr = sock.accept()

    # Build resp msg
    num = random.randint(1, 16)
    length = random.randint(24, 100)
    newsecret = random.randint(1, 100)
    randchar = chr(random.randint(33, 127))

    res = pack('>iihhiii', header + 1, secret, step, id, num, length, newsecret) + randchar.encode("ascii")
    secret = newsecret

    print("Sending Part C!")
    con.sendto(res, caddr)

    print("Validating part D!")
    acked = 0
    explen = header + length + ((align - length % align) % align)
    while acked < num:
        try:
            message = con.recv(explen)
        except:
            return
        
        # Validate msg
        if (len(message) != explen):
            print("Not valid total length!")
            return

        plen, psecret, temp, id2 = unpack('>iihh', message[0:header])

        if (psecret != secret or id2 != id or temp != 1):
            # Secrets, ID, step not matching
            print("Not valid secret, ID, or step!" , id, " ", id2, " ", psecret, " ", secret, " ", temp)
            return
        if plen != length:
            # Length not matching
            print("Payload len not equal to length!")
            return
        for i in message[header:header + length]:
            if chr(i) != randchar:
                print("Not char we asked for!")
                return
        acked = acked + 1
    
    res = pack('>iihhi', align, secret, step, id, random.randint(1, 100))
    con.sendto(res, caddr)

    print("All parts passed!")
    return


# be able to test things multiple times
while True:
    message, cip = sock.recvfrom(chunk_size)
    ClientConnect(message, cip)