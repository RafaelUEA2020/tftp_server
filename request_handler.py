current_file = None

def get_filename(data):
    parts = data[2:].split(b'\x00')
    return parts[0].decode()

def get_opcode(data):
    """
    Extrai os 2 primeiros bytes da mensagem e converte para inteiro.
    """
    return int.from_bytes(data[:2], byteorder="big")


def handle_request(data, addr, server_socket):
    """
    Identifica o tipo da mensagem TFTP recebida.
    """
    opcode = get_opcode(data)

    if opcode == 1:
        print(f"{addr} → RRQ (read request)")

        try:
            filename = get_filename(data)
            server_filename = "server_" + filename
            with open(server_filename, "rb") as f:
                file_data = f.read(512)

            data_packet = b'\x00\x03\x00\x01' + file_data
            server_socket.sendto(data_packet, addr)

            print(f"Enviado DATA bloco 1 ({len(file_data)} bytes)")

        except FileNotFoundError:
            print("Arquivo não encontrado")

    elif opcode == 2:
        print(f"{addr} → WRQ (write request)")

        global current_file
        filename = get_filename(data)
        server_filename = "server_" + filename

        current_file = open(server_filename, "wb")
        print(f"Salvando como: {server_filename}")

        ack = b'\x00\x04\x00\x00'
        server_socket.sendto(ack, addr)

    elif opcode == 3:
        print(f"{addr} → DATA")

        block_number = int.from_bytes(data[2:4], "big")
        file_data = data[4:]

        print(f"Bloco: {block_number}, Bytes: {len(file_data)}")
        if current_file:
            current_file.write(file_data)

        ack = b'\x00\x04' + data[2:4]
        server_socket.sendto(ack, addr)

        if len(file_data) < 512:
            print("Transferência finalizada")

            if current_file:
                current_file.close()
                current_file = None

    elif opcode == 4:
        print(f"{addr} → ACK")

    elif opcode == 5:
        print(f"{addr} → ERROR")

    else:
        print(f"{addr} → opcode desconhecido: {opcode}")