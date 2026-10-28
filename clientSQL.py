#"clientSQL.py" A program to try to re-create the popular quiz game Kahoot! in python
#Copyright (C) 2026  Alex Inns

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License version 3, as
#published by the Free Software Foundation.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.


import socket
import argparse


def address_family(name: str) -> socket.AddressFamily:
    try:
        return socket.AddressFamily[name.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(
            f"Invalid family {name!r}; choose from "
            f"{', '.join(m.name for m in socket.AddressFamily)}"
        )


def socket_kind(name: str) -> socket.SocketKind:
    try:
        return socket.SocketKind[name.upper()]
    except KeyError:
        raise argparse.ArgumentTypeError(
            f"Invalid kind {name!r}; choose from "
            f"{', '.join(m.name for m in socket.SocketKind)}"
        )
parser = argparse.ArgumentParser(description="Python connection details")
parser.add_argument("--addrFamily",type=address_family,default=socket.AF_INET,help="The address family for the socket")
parser.add_argument("--sockKind",type=socket_kind,default=socket.SOCK_STREAM,help="The protocol for the socket")
parser.add_argument("--enc",type=str,default="utf-8",help="The encoding for data sent through the socket")
args = parser.parse_args()

s = socket.socket(args.addrFamily,args.sockKind)
enc = args.enc
print("Created socket")
HOST = input("Host: ")
PORT = int(input("Port: "))
s.connect((HOST,PORT))
print("Connected to server")
print("Enter your nickname:")
nick = input()
s.send(nick.encode('utf-8'))

while True:
    q = s.recv(1024).decode(enc)
    if q == "Q":
        print("Answer A or B or C:")
        ans = input().lower()
        s.send(ans.encode(enc))
        right = s.recv(1024).decode(enc)
        if right == "correct":
            print("You were correct!")
        else:
            print("You were incorrect!")
    elif q == "e":
        break
place = s.recv(1024).decode(enc)
print("That's the end of the quiz")
print(f"You came in {place}th place")
