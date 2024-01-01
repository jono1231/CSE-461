import socket
from struct import pack, unpack

# Socket port/dest
port = 12235 
dest = '127.0.0.1' 

# Header things
chunk_size = 1024 
align = 4

# Secret data
id  = 141
secret = 0
step = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# build the message
message = "hello world\0"
header = pack(">iihh", len(message), secret, step, id)
send = header + message.encode()

print("Sending data for part A")
# send message, recieve data
sock.sendto(send,(dest, port))
result = sock.recv(chunk_size)

# extract data from the msg
plen, psec, serv_step, id, num, length, port, secret = unpack('>iihhiiii', result)
print("part 1 secret: ", secret)

print("Sending data for part B")

# Keep track of number of acked and timeout
timeout = 1
acked = 0
while acked < num:
    # Build message
    header = pack(">iihhi", length + align, secret, step, id, acked)
    # print("number acked:", acked)

    # Create alligned thing
    message = bytearray(length + ((align - length % align) % align))
    send = header + message

    # Send to part b
    sock.sendto(send,(dest, port))

    # Get timeout
    try:
        sock.settimeout(timeout)
        ans = sock.recv(chunk_size)
        # man idk python why does acked++ not work :skull:
    except socket.timeout:
        acked = acked - 1
    acked = acked + 1

# all [secret] packets are have been extracted, get the last msg
result = sock.recv(chunk_size)

# extract data from the msg
plen, psec, serv_step, id, port, secret = unpack('>iihhii', result)
print("part 2 secret: ", secret)

# Begin part c - build TCP socket
print("Connecting to part C")
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((dest, port))

# Get the result from pt c
result = sock.recv(chunk_size)

# after 3 hours of googling apparently unpack needs a buffer? idk
plen, psec, serv_step, id, num, length, secret, c = unpack('>iihhiiic', result[0:25])

print("part 3 secret: ", secret)

header = pack('>iihh', length, secret, step, id)

# Python is weird... i have to do this i cant just start with ""
message = c
for i in range(1, length + ((align - length % align) % align)):
    message += c

send = header + message

print ("Sending data for part D")
for i in range(num):
    sock.send(send)

result = sock.recv(chunk_size)

plen, psec, serv_step, id, secret = unpack('>iihhi', ans)

print("part 4 secret: ", secret)