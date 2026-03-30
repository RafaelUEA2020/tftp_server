import socket

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto(b"teste", ("192.168.0.159", 2307))

data, _ = client.recvfrom(1024)
print(data)