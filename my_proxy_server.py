# Include Python's Socket Library
from socket import *
import datetime
import time
import os,sys

my_http_version = 'HTTP/1.1'
is_self = False
#print(os.path.exists(sys.path[0] + '/192.168.1.71/12000/test.html'))
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

def get_my_ip():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

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

# Specify Proxy Server Port
proxy_serverPort = 12001

# Create TCP welcoming socket
proxyServerSocket = socket(AF_INET,SOCK_STREAM)
proxyServerSocket.bind(('',proxy_serverPort))
proxyServerSocket.listen(1)
proxyIP = get_my_ip()
print ('The server is ready to receive')

while True: # Loop forever
    # Server waits on accept for incoming requests.
    # New socket created on return
    connectionSocket, addr = proxyServerSocket.accept()
    
    # Read from socket (but not address as in UDP)
    message = connectionSocket.recv(1024).decode()
    print(message)
    devided_message = message.split()
#     print (devided_message)
    if devided_message[0] == 'GET':
        if(devided_message[3] != 'Host:'):
            res_type = '400 Bad request'
            res = pack_response(res_type,0,0)
            connectionSocket.send(res.encode())
            connectionSocket.close()
            continue
        
        page = ''
        is_self = False
        if proxyIP+':'+str(proxy_serverPort) == devided_message[4]:
            page = devided_message[1][1:]
            is_self = True
            # print(page)
        else:
            page = devided_message[4].split(':')[0]+'/'+devided_message[4].split(':')[1]+devided_message[1]
        
        data = ''
        modified_time = 0
                    
#        print(proxyIP+':'+str(proxy_serverPort))
        if not os.path.exists(sys.path[0]+'/'+page):
            # ======= send request to the origin server =======
            ori_info = page.split('/',2)
            ori_IP = ori_info[0]
            ori_port = ori_info[1]
            file = '/' + ori_info[2]
            request_message = 'GET '+ file + ' ' + my_http_version + '\r\n'
            request_message += 'Host: ' + ori_IP + ':' + ori_port + '\r\n'
            request_message += 'User-Agent: my_client\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 115\r\nConnection: keep-alive\r\n'
            request_message += '\r\n'
            serverName = ori_IP
            serverPort = int(ori_port)
            # Create TCP Socket for Client
            clientSocket = socket(AF_INET, SOCK_STREAM)
            # Connect to TCP Server Socket
            clientSocket.connect((serverName,serverPort))
            clientSocket.send(request_message.encode())
            ori_response = clientSocket.recv(1024)
            ori_message = ori_response.decode()
#                print(ori_message)
            connectionSocket.send(ori_message.encode())
            connectionSocket.close()
            devided_ori_message = ori_message.split('\r\n')
            if devided_ori_message[0].split()[1] == '200':
                # send back and save file
                o_m_index = 0
                while devided_ori_message[o_m_index] != '':
                    o_m_index += 1
                o_m_index += 1
                # now o_m_index is the data in string type
                path_data_saved = sys.path[0] + '/' + ori_IP + '/' + ori_port
                if not os.path.exists(path_data_saved):
                    os.makedirs(path_data_saved)
                new_file = open(path_data_saved + file, 'w')
                new_file.write(devided_ori_message[o_m_index])
                new_file.close()
            
        else:
            
            # the file is in the proxy server
            # not know if it is modified yet
            ori_info = page.split('/',2)
            ori_IP = ori_info[0]
            ori_port = ori_info[1]
            file = '/' + ori_info[2]
            index = 0
            modified_ask_datetime = 0
            while index<len(devided_message) and devided_message[index] != 'If-Modified-Since:':
                index += 1
            
            route = ''
            
            if is_self:
                route = sys.path[0] + '/' + page
            else:
                route = sys.path[0] + '/' + ori_IP+'/'+ori_port+'/'+page
            mtime = time.ctime(os.path.getmtime(route))
            m_datetime = datetime.datetime.strptime(mtime, "%a %b %d %H:%M:%S %Y")
            local_modified_ask_datetime = datetime.datetime(
                year=m_datetime.year,
                month=m_datetime.month,
                day=m_datetime.day,
                hour=m_datetime.hour,
                minute=m_datetime.minute,
                second=m_datetime.second,
                tzinfo=datetime.timezone.utc)
            
            if index < len(devided_message):
                # request with asking If-Modified-Since
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
            
            else:
                modified_ask_datetime = local_modified_ask_datetime
            
            modified_time = local_modified_ask_datetime.strftime("%a, %d %b %Y %H:%M:%S %Z")

            # build request and send to the origin server
            
            time_datetime = modified_ask_datetime.strftime("%a, %d %b %Y %H:%M:%S %Z")
            request_message = 'GET '+ file + ' ' + my_http_version + '\r\n'
            request_message += 'Host: ' + ori_IP + ':' + ori_port + '\r\n'
            request_message += 'User-Agent: my_client\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 115\r\nConnection: keep-alive\r\n'
            request_message += 'If-Modified-Since: '+time_datetime+'\r\n'
            request_message += '\r\n'
            
            serverName = ori_IP
            serverPort = int(ori_port)
            # Create TCP Socket for Client
            clientSocket = socket(AF_INET, SOCK_STREAM)
            # Connect to TCP Server Socket
            clientSocket.connect((serverName,serverPort))
            clientSocket.send(request_message.encode())
            clientSocket.settimeout(3)
                
            try:
                response = clientSocket.recv(1024)
            except Exception as e:
                res_type = '408 Request Timed Out'
                res = pack_response(res_type,0,0)
                connectionSocket.send(res.encode())
                connectionSocket.close()
                continue

            else:
                clientSocket.settimeout(None)
                ori_res_message = response.decode()
                
                # ask the server if it is modified
                # if yes, send back to the client and updated the database
                # else if no, send the client what we got
                # else if error message, send the message stright back to the client
            
                if ori_res_message.split()[1] == '304':
                    f = open(page,encoding = "utf-8")
                    data = f.read()
                    f.close()
                    # print(modified_time)
                    
                    # Send the reply
#                    print('yes')
                    res_type = '200 OK'
                    res = pack_response(res_type,data,modified_time)
                    connectionSocket.send(res.encode())
                    
                    # Close connectiion too client (but not welcoming socket)
                    connectionSocket.close()
                    continue
                
                elif (ori_res_message.split()[1] == '200'):
                    connectionSocket.send(ori_res_message.encode())
                    connectionSocket.close()
                    devided_ori_message = ori_res_message.split('\r\n')
                    o_m_index = 0
                    while devided_ori_message[o_m_index] != '':
                        o_m_index += 1
                    o_m_index += 1
                    # now o_m_index is the data in string type
                    f = open(page,encoding = "utf-8")
                    f.write(devided_ori_message[o_m_index])
                    f.close()
                    continue
                    
                else:
                    connectionSocket.send(ori_res_message.encode())
                    connectionSocket.close()
                    continue

        
    elif devided_message[0] == 'TRTO':
        time.sleep(10)
        connectionSocket.close()

    else:
        res_type = '400 Bad request'
        res = pack_response(res_type,0,0)
        connectionSocket.send(res.encode())
        connectionSocket.close()

