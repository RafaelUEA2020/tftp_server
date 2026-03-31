import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b'\x00\x02arquivo.txt\x00octet\x00', ("127.0.0.1", 69))

data, _ = client.recvfrom(1024)
print(data)