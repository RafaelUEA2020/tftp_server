import socket
from request_handler import handle_request

HOST = "0.0.0.0"   #aceita qualquer IP
PORT = 69

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print(f"Servidor UDP rodando em {HOST}:{PORT}")

    while True:
        data, addr = server_socket.recvfrom(1024)

        handle_request(data, addr, server_socket)

if __name__ == "__main__":
    start_server()