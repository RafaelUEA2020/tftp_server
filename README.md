# tftp_server

Servidor dedicado à implementação do protocolo **TFTP (Trivial File Transfer Protocol)**, desenvolvido para a disciplina de **Tópicos Avançados em Computação I**.

## Integrantes
- Alicia Benedetto
- Daffiny Gomes
- Rafael Santos

## Descrição
Este projeto implementa um **servidor TFTP em Python**, utilizando comunicação via **UDP**, com suporte às operações principais de:

- **WRQ (Write Request / PUT)** → envio de arquivo do cliente para o servidor
- **RRQ (Read Request / GET)** → envio de arquivo do servidor para o cliente

O servidor foi desenvolvido para receber requisições de clientes TFTP e processar transferências de arquivos por blocos, conforme a lógica básica do protocolo TFTP.

## Como executar o servidor

Execute o servidor com:

```bash
python udp_server.py
```
##Como testar

- Teste de upload (PUT)

Envia um arquivo do cliente para o servidor:
```bash
tftp -i 127.0.0.1 PUT seuarquivo.txt
```
- Teste de download (GET)

Baixa um arquivo do servidor para o cliente:
```bash
tftp -i 127.0.0.1 GET seuarquivo.txt
```
