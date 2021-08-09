#!/usr/bin/python3
import os
import sys
import socket
import json

status = {
    "OK": {"status": "OK"},
    "WARN": {"status": "WARNING"},
    "ERR": {"status": "ERROR"}
    }

def nginx_pid():
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            with open("/proc/{}/comm".format(pid), encoding = 'utf-8') as f:
                if "nginx" in f.readline():
                    return pid

def nginx_load_sockets(pid):
    inodes = []
    try:
        for fd in os.listdir("/proc/{}/fd".format(pid)):
            fd_info = os.readlink("/proc/{}/fd/{}".format(pid, fd))
            if fd_info.split(":")[0] == "socket":
                inode = json.loads(fd_info.split(":")[1])[0]
                inodes.append(inode)
    except PermissionError:
        sys.exit("Must run as root")
    return inodes


def inodes_for_port(port = 80):
    INODE_PORT_MAP = {}
    with open("/proc/net/tcp", encoding = 'utf-8') as f:
        f.readline() # skip column names
        for line in f:
            data = line.split()
            LOCAL_ADDRESS_PORT_HEX = data[1]
            PORT = int(LOCAL_ADDRESS_PORT_HEX.split(':')[1], 16)
            INODE = int(data[9])
            if PORT == port:
                INODE_PORT_MAP[INODE] = PORT
    return INODE_PORT_MAP

def main(port = 80):
    pid = nginx_pid()

    # Check if nginx is really listening on target port
    error = True
    for inode in nginx_load_sockets(pid):
        if inode in inodes_for_port(port):
            error = False
    if error:
        exit(json.dumps(status["ERR"]))

    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    location = ("127.0.0.1", port)
    result_of_check = a_socket.connect_ex(location)

    if result_of_check == 0:
        print(json.dumps(status["OK"]))
    else:
        # Possible firewall or configuration issue
        print(json.dumps(status["WARN"]))

if __name__ == "__main__":
    main()
