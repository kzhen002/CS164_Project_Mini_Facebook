import socket
import sys
import datetime
from thread import *
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error , msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
class Post(object):
    def __init__(self,status,uname):
        self.uname=uname
        self.status=status
        self.likes=0
        self.comments=list()
        #Datetime without microseconds
        self.date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
class User(object):
    def __init__(self,uname):
        self.uname=uname
        self.unReadMsg=list()
        self.friendReq=list()
        self.friends=list()
        self.wall=list()
        self.newsfeed=list()
userList = dict()
userList['kzhen']=User('kzhen')
userList['dtrump']=User('dtrump')
userList['obama']=User('obama')
users= {
    'kzhen':'password1',
    'dtrump':'password2',
    'obama':'password3'
}
online = dict() 
def postStatus(conn,uname):
    conn.sendall('Type in your status below.\n')
    status=conn.recv(1024)
    newPost=Post(status,uname)
    userList[uname].wall.append(newPost)

def seeWall(conn,uname):
    userWall="Your Wall\n"
    for posts in reversed(userList[uname].wall):
        status=posts.status
        status=uname+"\t"+str(posts.date)+"\n"+status+"\n"
        userWall=userWall+status+"\n"
    conn.sendall(userWall)

def seeNewsFeed(conn,uname):
    timeLine=list()
    for friend in userList[uname].friends:
        timeLine=timeLine+userList[friend].wall
    timeLine.sort(key=lambda r: r.date)
    if len(timeLine) > 10:
        timeLine=timeLine[-10:]
    newsFeed="Your Newsfeed\n"
    for posts in reversed(timeLine):
        status=posts.status
        status=posts.uname+"\t"+str(posts.date)+"\n"+status+"\n"
        newsFeed=newsFeed+status+"\n"
    conn.sendall(newsFeed)
    
    
def replyToFriendRequests(conn, uname):
    if not userList[uname].friendReq:
        conn.sendall("You have no friend requestss :( \n")
    for fr in userList[uname].friendReq:
        #print userList[uname].friendReq
        tmpfr,fromUser=fr
        invalid=1
        while(invalid==1):
            conn.sendall(tmpfr)
            reply=conn.recv(1024)
            reply=reply.rstrip('\r\n')
            if reply=='1': #accept
                invalid=0
                if fromUser not in userList[uname].friends:
                    userList[uname].friends.append(fromUser)
                    userList[fromUser].friends.append(uname)
                else:
                    conn.sendall("You're already friends!\n")
                userList[uname].friendReq=userList[uname].friendReq[1:]
            elif reply=='2': #decline
                invalid=0
                userList[uname].friendReq.pop(0)
            else:
                conn.sendall("Unrecognized Command\n")

    userList[uname].friendReq[:]=[]
def sendFriendReqest(toUser, fromUser,conn):
    if toUser not in userList[fromUser].friends:
        friendReq="Friend request from " + fromUser + "\n"
        friendReq=friendReq+"1. Accept\n"
        friendReq=friendReq+"2. Decline\n"
        userList[toUser].friendReq.append((friendReq,fromUser))
        if toUser in online:
            frNotification=fromUser + " has sent you a friend request\n"
            online[toUser].sendall(frNotification)
    else:
        conn.sendall("You're already friends!\n")
        
def sendUserMsg(toUser, fromUser, msg):
    if toUser in online:
        formatMsg="To: " + toUser + "\n"+"Body: "+ msg + "\n"
        formatMsg=formatMsg+"From: " + fromUser + "\n"
        online[toUser].sendall(formatMsg)
        #print msg
    else:
        formatMsg="To: " + toUser + "\n"+"Body: "+ msg + "\n"
        formatMsg=formatMsg+"From: " + fromUser + "\n"
        userList[toUser].unReadMsg.append(formatMsg)
        #print userList[toUser].unReadMsg

def menuPrompt(conn, uname):
    prompt="""1. Logout
2. Change Password
3. Send Message
4. See Unread Messages
5. Send Friend Request
6. Respond to Friend Request
7. Post Status
8. See Timeline
9. See News Feed\n"""
    uname="$"+uname+":"
    prompt+= uname
    conn.sendall(prompt)

def login(conn):
    invalidLogin=1
    while(invalidLogin):
        conn.send('Please enter your username and hit enter\n') #send only takes string
        uname=conn.recv(1024)
        uname=uname.rstrip('\r\n')
        #print 'Username: ' + uname
        conn.sendall('Please enter your password and hit enter\n')
        pwd=conn.recv(1024)
        pwd=pwd.rstrip('\r\n')
        #print 'Password: ' + pwd
        if uname in users and users[uname]==pwd:
            invalidLogin=0
            online[uname]=conn
            numUnreadMsg=len(userList[uname].unReadMsg)
            numFriendReqs=len(userList[uname].friendReq)
            prompt="""1. Logout
2. Change Password
3. Send Message
4. See Unread Messages
5. Send Friend Request
6. Respond to Friend Request
7. Post Status
8. See Timeline
9. See News Feed\n"""
            prompt=prompt+"You have " + str(numUnreadMsg) + " unread messages.\n"
            prompt=prompt+"You have " + str(numFriendReqs) + " unanswered friend requests\n"
            prompt=prompt+ "$"+uname+":"
            conn.sendall(prompt)
            return uname
        else:
            conn.send('Invalid Username/Password Combination\n')
    
#Function for handling connections. This will be used to create threads
def clientthread(conn):
    uname=login(conn)
    msg=conn.recv(1024)
    msg=msg.rstrip('\r\n')
    while(msg != '1'):
        #Receiving from client
        if(msg=='2'): #change pwd
            conn.sendall('Please enter your old password\n')
            oldpwd=conn.recv(1024)
            oldpwd=oldpwd.rstrip('\r\n')
            while(oldpwd != users[uname]):
                conn.sendall('Please enter your old password\n')
                oldpwd=conn.recv(1024)
                oldpwd=oldpwd.rstrip('\r\n')
            conn.sendall('Please enter your new password\n')
            newpwd=conn.recv(1024)
            newpwd=newpwd.rstrip('\r\n')
            users[uname]=newpwd
        elif msg=='3': #send msg
            conn.sendall('Who would you like to send a message to?\n')
            toUname=conn.recv(1024)
            toUname=toUname.rstrip('\r\n')
            conn.sendall('Type in your message below.\n')
            toMsg=conn.recv(1024)
            sendUserMsg(toUname,uname,toMsg)
        elif msg=='4': #see unread msg
            unread='Unread Messages\n'
            for m in userList[uname].unReadMsg:
                m+='\n'
                unread+=m
            userList[uname].unReadMsg[:]=[]
            conn.sendall(unread)
        elif msg=='5': #send friend req
            conn.sendall('Who would you like to send a friend request to?\n')
            toUname=conn.recv(1024)
            toUname=toUname.rstrip('\r\n')
            sendFriendReqest(toUname,uname,conn)
        elif msg=='6': #see and reply friend req 1by1
            replyToFriendRequests(conn,uname)
        elif msg=='7':
            postStatus(conn,uname)
        elif msg=='8':
            seeWall(conn,uname)
        elif msg=='9':
            seeNewsFeed(conn,uname)
        else:
            conn.sendall('Unrecognized Command\n')
        menuPrompt(conn, uname)
        msg = conn.recv(1024)
        msg=msg.rstrip('\r\n')
    online.pop(uname, None)
    conn.sendall('Successfully logged out\n') 
    conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()