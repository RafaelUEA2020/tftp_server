current_file = None
sessions = {}
class TFTPSession:
    def __init__(self, filename, mode, addr):
        self.addr = addr
        self.filename = f"server_{filename}"
        self.mode = mode  # 'RRQ' ou 'WRQ'
        self.file_handle = open(self.filename, "rb" if mode == 'RRQ' else "wb")
        self.next_block = 1
        self.completed = False

class SessionManager:
    def __init__(self):
        self.sessions = {}

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def handle_packet(self, data, addr, sock):
        opcode = int.from_bytes(data[:2], "big")

        # NOVO PEDIDO (RRQ ou WRQ)
        if opcode in [1, 2]:
            filename = data[2:].split(b'\x00')[0].decode()
            mode = 'RRQ' if opcode == 1 else 'WRQ'
            
            print(f"Nova sessão {mode} iniciada para {addr} - Arquivo: {filename}")
            
            # Se já existir uma sessão para este IP/Porta, fecha a antiga antes
            if addr in self.sessions:
                self.sessions[addr].file_handle.close()

            self.sessions[addr] = TFTPSession(filename, mode, addr)
            
            if mode == 'WRQ':
                sock.sendto(b'\x00\x04\x00\x00', addr) # ACK 0
            else:
                # Início da lógica de envio (RRQ)
                self.send_next_block(addr, sock, 1)

        # DADOS RECEBIDOS (DATA - Opcode 3)
        elif opcode == 3:
            if addr in self.sessions:
                session = self.sessions[addr]
                block_num = data[2:4]
                content = data[4:]
                
                session.file_handle.write(content)
                sock.sendto(b'\x00\x04' + block_num, addr) # Envia ACK do bloco

                if len(content) < 512:
                    print(f"Transferência (Upload) de {addr} finalizada.")
                    session.file_handle.close()
                    del self.sessions[addr]
            else:
                print(f"Aviso: Dados recebidos de {addr} sem sessão ativa.")

        # CONFIRMAÇÃO DE RECEBIMENTO (ACK - Opcode 4)
        elif opcode == 4:
            if addr in self.sessions:
                # Aqui você implementaria o envio do PRÓXIMO bloco no caso de RRQ
                pass       

def get_filename(data):
    parts = data[2:].split(b'\x00')
    return parts[0].decode()

def get_opcode(data):
    """
    Extrai os 2 primeiros bytes da mensagem e converte para inteiro.
    """
    return int.from_bytes(data[:2], byteorder="big")

def handle_session(data, addr, server_socket):
    opcode = int.from_bytes(data[:2], "big")

    # CASO 1: É um novo pedido (RRQ ou WRQ)
    if opcode in [1, 2]:
        filename = get_filename(data)
        print(f"Nova sessão iniciada para {addr} - Arquivo: {filename}")
        
        # Criamos um "contexto" para esse cliente específico
        sessions[addr] = {
            'filename': "server_" + filename,
            'handle': open("server_" + filename, "wb" if opcode == 2 else "rb"),
            'block': 0 if opcode == 2 else 1,
            'type': 'PUT' if opcode == 2 else 'GET'
        }

        if opcode == 2: # WRQ (Escrever)
            server_socket.sendto(b'\x00\x04\x00\x00', addr) # Envia ACK 0
        else: # RRQ (Ler)
            # Aqui você enviaria o Bloco 1 do arquivo...
            pass

    # CASO 2: É um pacote de DATA (Opcode 3) de uma sessão que já existe
    elif opcode == 3:
        if addr in sessions:
            context = sessions[addr]
            block_number = data[2:4]
            file_content = data[4:]

            # Escreve no arquivo específico DESTE cliente
            context['handle'].write(file_content)
            
            # Responde o ACK para ESTE cliente
            ack = b'\x00\x04' + block_number
            server_socket.sendto(ack, addr)

            # Finalização
            if len(file_content) < 512:
                print(f"Transferência concluída para {addr}")
                context['handle'].close()
                del sessions[addr] # Remove a sessão do dicionário
        else:
            print(f"Erro: Recebi dados de {addr}, mas não há sessão aberta.")



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