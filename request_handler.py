class TFTPSession:
    def __init__(self, filename, mode, addr):
        self.addr = addr
        self.filename = f"server_{filename}"
        self.mode = mode  # 'RRQ' ou 'WRQ'
        self.file_handle = open(self.filename, "rb" if mode == "RRQ" else "wb")
        self.next_block = 1
        self.completed = False


class SessionManager:
    def __init__(self):
        self.sessions = {}

    def send_error(self, sock, addr, error_code, message):
        error_packet = (
            b"\x00\x05"
            + error_code.to_bytes(2, "big")
            + message.encode("utf-8")
            + b"\x00"
        )
        sock.sendto(error_packet, addr)

    def send_next_block(self, addr, sock, block_number=None):
        session = self.sessions[addr]

        if block_number is None:
            block_number = session.next_block

        file_data = session.file_handle.read(512)
        data_packet = b"\x00\x03" + block_number.to_bytes(2, "big") + file_data
        sock.sendto(data_packet, addr)

        print(
            f"Enviado DATA bloco {block_number} "
            f"({len(file_data)} bytes) para {addr}"
        )

        session.next_block = block_number

        if len(file_data) < 512:
            session.completed = True

    def handle_packet(self, data, addr, sock):
        opcode = int.from_bytes(data[:2], "big")

        # NOVO PEDIDO (RRQ ou WRQ)
        if opcode in [1, 2]:
            filename = data[2:].split(b"\x00")[0].decode()
            mode = "RRQ" if opcode == 1 else "WRQ"

            print(f"Nova sessão {mode} iniciada para {addr} - Arquivo: {filename}")

            if addr in self.sessions:
                self.sessions[addr].file_handle.close()
                del self.sessions[addr]

            try:
                self.sessions[addr] = TFTPSession(filename, mode, addr)
            except FileNotFoundError:
                print(f"Arquivo não encontrado: server_{filename}")
                self.send_error(sock, addr, 1, "Arquivo nao encontrado")
                return
            except Exception as error:
                print(f"Erro ao abrir arquivo da sessão: {error}")
                self.send_error(sock, addr, 0, "Erro interno do servidor")
                return

            if mode == "WRQ":
                sock.sendto(b"\x00\x04\x00\x00", addr)  # ACK 0
            else:
                self.send_next_block(addr, sock, 1)

        # DADOS RECEBIDOS (DATA - Opcode 3) -> upload/PUT
        elif opcode == 3:
            if addr in self.sessions:
                session = self.sessions[addr]
                block_num = data[2:4]
                content = data[4:]

                session.file_handle.write(content)
                sock.sendto(b"\x00\x04" + block_num, addr)  # ACK do bloco

                if len(content) < 512:
                    print(f"Transferência (Upload) de {addr} finalizada.")
                    session.file_handle.close()
                    del self.sessions[addr]
            else:
                print(f"Aviso: Dados recebidos de {addr} sem sessão ativa.")
                self.send_error(sock, addr, 0, "Sessao inexistente")

        # CONFIRMAÇÃO DE RECEBIMENTO (ACK - Opcode 4) -> download/GET
        elif opcode == 4:
            if addr in self.sessions:
                session = self.sessions[addr]
                ack_block = int.from_bytes(data[2:4], "big")

                print(f"ACK bloco {ack_block} recebido de {addr}")

                if session.mode == "RRQ":
                    if session.completed and ack_block == session.next_block:
                        print(f"Transferência (Download) para {addr} finalizada.")
                        session.file_handle.close()
                        del self.sessions[addr]
                    elif ack_block == session.next_block:
                        next_block = ack_block + 1
                        self.send_next_block(addr, sock, next_block)
            else:
                print(f"Aviso: ACK recebido de {addr} sem sessão ativa.")

        elif opcode == 5:
            print(f"Pacote ERROR recebido de {addr}")

        else:
            print(f"Opcode desconhecido recebido de {addr}: {opcode}")
            