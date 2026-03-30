import socket

HOST = "0.0.0.0"   #aceita qualquer IP
PORT = 2307

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))

    print(f"Servidor UDP rodando em {HOST}:{PORT}")

    while True:
        data, addr = server_socket.recvfrom(1024)

        print(f"Recebido de {addr}: {data}")

        response = b"ok"
        server_socket.sendto(response, addr)

if __name__ == "__main__":
    start_server()