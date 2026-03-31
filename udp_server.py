import socket
import sys
from request_handler import SessionManager

HOST = "0.0.0.0"
PORT = 69

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        server_socket.bind((HOST, PORT))
        manager = SessionManager()
        print(f"Servidor TFTP rodando em {HOST}:{PORT}")
        print("Pressione Ctrl+C para encerrar o servidor com segurança.")

        while True:
            # Definimos um timeout curto para o socket não travar o loop
            # Isso permite que o Python "perceba" o Ctrl+C mais rápido
            server_socket.settimeout(1.0) 
            
            try:
                data, addr = server_socket.recvfrom(1024)
                manager.handle_packet(data, addr, server_socket)
            except socket.timeout:
                # O timeout aconteceu, voltamos ao topo do while para checar o sinal
                continue

    except KeyboardInterrupt:
        print("\n[INFO] Interrupção detectada (Ctrl+C).")
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro inesperado: {e}")
    finally:
        # Aqui garantimos que tudo seja fechado antes de sair
        print("[INFO] Fechando conexões e arquivos... Até logo!")
        server_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    start_server()