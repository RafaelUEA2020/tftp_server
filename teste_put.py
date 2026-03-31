import socket

print("Iniciando cliente PUT...")

server_address = ("127.0.0.1", 69)
filename = "teste_put2.txt"
mode = "octet"

with open(filename, "rb") as file:
    file_content = file.read()

wrq = b"\x00\x02" + filename.encode() + b"\x00" + mode.encode() + b"\x00"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(5)

try:
    print("Enviando WRQ...")
    client.sendto(wrq, server_address)

    data, addr = client.recvfrom(516)
    print("Resposta recebida:", data)

    opcode = int.from_bytes(data[:2], "big")
    block = int.from_bytes(data[2:4], "big")

    if opcode == 4 and block == 0:
        print("ACK 0 recebido. Enviando DATA bloco 1...")

        data_packet = b"\x00\x03\x00\x01" + file_content
        client.sendto(data_packet, addr)

        ack_data, _ = client.recvfrom(516)
        print("ACK final recebido:", ack_data)

        print("Upload finalizado.")
    else:
        print("Resposta inesperada do servidor.")

except socket.timeout:
    print("Timeout: o servidor não respondeu.")
finally:
    client.close()
    print("Cliente encerrado.")
    