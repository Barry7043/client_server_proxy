# Include Python's Socket Library
from socket import *
import datetime
import time
import os.path,sys
import threading

my_http_version = 'HTTP/1.1'

# =============== test for modify time of test.html ======================
# route = sys.path[0] + "/test.html"
# mtime = time.ctime(os.path.getmtime(route))
# print(mtime)
# trans = datetime.datetime.strptime(mtime, "%a %b %d %H:%M:%S %Y")
# trans_with_tz = datetime.datetime(
#     year=trans.year,
#     month=trans.month,
#     day=trans.day,
#     hour=trans.hour,
#     minute=trans.minute,
#     second=trans.second,
#     tzinfo=datetime.timezone.utc)
# print(trans_with_tz)
# date = datetime.datetime.now(datetime.timezone.utc)
# if trans_with_tz < date:
#     print('yes')


def pack_response(res_type, data, modified_time):
    date = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %Z")
    res = my_http_version + ' ' + res_type + '\r\n' + 'Date: ' + date + '\r\nServer: my_web_server\r\n'
    if res_type == "200 OK":
        res += 'Last-Modified: ' + modified_time + '\r\nETag: "00000-000-00000000"\r\nAccept-Ranges: bytes\r\nContent-Length: '+str(len(data)) + '\r\nConnection: Keep-Alive\r\nContent-Type: text/html; charset=ISO-8859-1\r\n\r\n'
        res += data
    else:
        res += 'Connection: Keep-Alive\r\nKeep-Alive: Undefined\r\nETag: "00000-000-00000000"\r\n\r\n'
    # HTTP/1.1 200 OK\r\n
    # Date: Sun, 26 Sep 2010 20:09:20 GMT\r\n
    # Server: my_web_server\r\n
    # Last-Modified: Tue, 30 Oct 2007 17:00:02 GMT\r\n
    # ETag: "00000-000-00000000"\r\n
    # Accept-Ranges: bytes\r\n
    # Content-Length: 2652\r\n
    # Keep-Alive: timeout=10, max=100\r\n
    # Connection: Keep-Alive\r\n
    # Content-Type: text/html; charset=ISO-8859-1\r\n
    # \r\n
    # data
    return res

# Specify Server Port
serverPort = 12000

# Create TCP welcoming socket
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(5)
print ('The server is ready to receive')
threads = []

def handle_request(connectionSocket):
    time.sleep(2)
    message = connectionSocket.recv(1024).decode()
#    print(message)
    devided_message = message.split()
#     print (devided_message)
    if devided_message[0] == 'GET':
        if(devided_message[3] != 'Host:'):
            res_type = '400 Bad request'
            res = pack_response(res_type,0,0)
            connectionSocket.send(res.encode())
            connectionSocket.close()
            print('responded')
            return
            
        page = devided_message[1][1:]
        # print(page)
        data = ''
        modified_time = 0
        try:
            f = open(page,encoding = "utf-8")
        except OSError as reason:
            res_type = '404 Not Found'
            res = pack_response(res_type,0,0)
            connectionSocket.send(res.encode())
            connectionSocket.close()
            print('responded')
            return
        else:
            index = 0
            modified_ask_datetime = 0
            while index<len(devided_message) and devided_message[index] != 'If-Modified-Since:':
                index += 1
            if index < len(devided_message):
                modified_ask_time = devided_message[index+1] + ' ' + devided_message[index+2] + ' ' + devided_message[index+3] + ' ' + devided_message[index+4] + ' ' + devided_message[index+5] + ' ' + devided_message[index+6]
                modified_ask_d_time = datetime.datetime.strptime(modified_ask_time, "%a, %d %b %Y %H:%M:%S %Z")
                modified_ask_datetime = datetime.datetime(
                    year=modified_ask_d_time.year,
                    month=modified_ask_d_time.month,
                    day=modified_ask_d_time.day,
                    hour=modified_ask_d_time.hour,
                    minute=modified_ask_d_time.minute,
                    second=modified_ask_d_time.second,
                    tzinfo=datetime.timezone.utc)
            
            route = sys.path[0] + "/" + page
            mtime = time.ctime(os.path.getmtime(route))
            m_datetime = datetime.datetime.strptime(mtime, "%a %b %d %H:%M:%S %Y")
            m_datetime_with_tz = datetime.datetime(
                year=m_datetime.year,
                month=m_datetime.month,
                day=m_datetime.day,
                hour=m_datetime.hour,
                minute=m_datetime.minute,
                second=m_datetime.second,
                tzinfo=datetime.timezone.utc)
            modified_time = m_datetime_with_tz.strftime("%a, %d %b %Y %H:%M:%S %Z")

            if modified_ask_datetime != 0 and modified_ask_datetime >= m_datetime_with_tz:
                f.close()
                res_type = '304 Not Modified'
                res = pack_response(res_type,0,0)
                connectionSocket.send(res.encode())
                connectionSocket.close()
                print('responded')
                return


            data = f.read()
            f.close()
            # print(modified_time)
            
        
            

            # Send the reply
            # print(mesage)
            res_type = '200 OK'
            res = pack_response(res_type,data,modified_time)
            connectionSocket.send(res.encode())
            
            # Close connectiion too client (but not welcoming socket)
            connectionSocket.close()
    elif devided_message[0] == 'TRTO':
        time.sleep(10)
        connectionSocket.close()

    else:
        res_type = '400 Bad request'
        res = pack_response(res_type,0,0)
        connectionSocket.send(res.encode())
        connectionSocket.close()
    
    print('responded')


while True: # Loop forever
    # Server waits on accept for incoming requests.
    # New socket created on return
    connectionSocket, addr = serverSocket.accept()
    print('accepted')
    p = threading.Thread(target=handle_request,args=[connectionSocket,])
    threads.append(p)
    p.start() # start the thread.
    
    
