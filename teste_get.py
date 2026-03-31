import socket

print("Iniciando cliente GET...")

server_address = ("127.0.0.1", 69)
filename = "arquivo.txt"
mode = "octet"

rrq = b"\x00\x01" + filename.encode() + b"\x00" + mode.encode() + b"\x00"

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(5)

try:
    print("Enviando RRQ...")
    client.sendto(rrq, server_address)

    while True:
        data, addr = client.recvfrom(516)
        print("Pacote recebido:", data)

        opcode = int.from_bytes(data[:2], "big")

        if opcode == 3:
            block = data[2:4]
            content = data[4:]

            print("Bloco recebido:", int.from_bytes(block, "big"))
            print("Conteúdo:", content.decode(errors="ignore"))

            ack = b"\x00\x04" + block
            client.sendto(ack, addr)
            print("ACK enviado")

            if len(content) < 512:
                print("Transferência finalizada.")
                break

        elif opcode == 5:
            print("Erro recebido do servidor:", data)
            break

        else:
            print("Opcode inesperado:", opcode)
            break

except socket.timeout:
    print("Timeout: o servidor não respondeu.")
finally:
    client.close()
    print("Cliente encerrado.")
    