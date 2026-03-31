# tftp_server
Server dedicado a implementação do server de TFTP do grupo da disciplina de Topicos avançados de Engenharia de Software.

roda com qualquer IP (o teu local ou o da internet que tu tá conectado)

1. roda o servidor primeiro com
python udp_server.py

2. testa com
tftp -i 127.0.0.1 PUT seuarquivo.txt
tftp -i 127.0.0.1 GET seuarquivo.txt