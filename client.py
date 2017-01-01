#Socket client example in python
import getpass 
import socket   #for sockets
import sys  #for exit
 
#create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket Created'
#change IP to servers when you run topology
#localhost for testing without running topology
host = '127.0.0.1';
port = 8888;

oldp="Please enter your old password\n"
newp="Please enter your new password\n"
defp="Please enter your password and hit enter\n"
#Connect to remote server
s.connect((host , port))
print 'Socket Connected to ' + host

while 1:
    reply = s.recv(4096)
    print reply,
    if reply==oldp or reply==newp or reply==defp:
        passwd = getpass.getpass()
        s.sendall(passwd)
    elif reply=="Successfully logged out\n":
        sys.exit()
    else:
        #expecting input while message is stuck in queue here
        msg=raw_input()
        s.sendall(msg)
