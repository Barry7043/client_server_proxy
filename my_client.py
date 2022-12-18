from socket import *
import datetime

def legal_IP(IP):
    temp = ''
    count_of_dot = 0
    for n in IP:
        if n.isdigit():
            temp += n
        elif n == '.':
            count_of_dot += 1
            if int(temp) > 255 or int(temp) < 0 or count_of_dot > 3:
                return False
            temp = ''
        else:
            return False
    if count_of_dot != 3 or temp == '' or int(temp)>255:
        return False
    return True



# Recieve user input from keyboard
web = input('Input website:')



#process the input
#assume the start of input is http://
# --- IP input checking ---
index = 7
IP = ''
while index<len(web) and web[index]!=':':
    IP += web[index]
    index += 1

#print('IP: ',IP)

if(not legal_IP(IP)) or index >= len(web)-1:
    print ('wrong input IP address')
    exit()

# --- port input checking ---
port = ''
index += 1
while index<len(web) and web[index]!='/':
    if not web[index].isdigit():
        print ('wrong input port')
        exit()
    port += web[index]
    index += 1

if port == '':
    print ('no input port')
    exit()

#print('Port: ',port)

# --- page input checking ---

page = ''
while(index<len(web)):
    page += (web[index])
    index += 1
#print('Page: ',page)
#page might be empty


print('1 - Normal Request\n2 - Test for Request Timed Out\n3 - Test for Bad Request\n4 - Ask if Modified Since ...\n')
option = input('Option 1/2/3/4: ')


# ---- make http request ----
request_message = ''
my_HTTP_version = 'HTTP/1.1'
if option == '1':
    request_message += 'GET '+ page + ' ' + my_HTTP_version + '\r\n'
    request_message += 'Host: ' + IP + ':' + port + '\r\n'
    request_message += 'User-Agent: my_client\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 115\r\nConnection: keep-alive\r\n'
    request_message += '\r\n'
    #print('Request message:\n' + request_message)
elif option == '2':
    request_message += 'TRTO '+ page + ' ' + my_HTTP_version + '\r\n'
    request_message += 'Host: ' + IP + ':' + port + '\r\n'
    request_message += 'User-Agent: my_client\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 115\r\nConnection: keep-alive\r\n'
    request_message += '\r\n'

elif option == '3':
    request_message += 'TEG '+ page + ' ' + my_HTTP_version + '\r\n'
    request_message += 'tosH: ' + IP + ':' + port + '\r\n'
    request_message += 'errorrrrrrrrrrrrrrrrrrr'
    request_message += '\r\n'

elif option == '4':
    time = input('Since Month/Day/Year Hr:Min:Seconds\n(Sample: 09/19/18 13:55:26)\nTime in UTC: ')
    time_d = datetime.datetime.strptime(time, '%m/%d/%y %H:%M:%S')
    time_d_with_tz = datetime.datetime(
        year=time_d.year,
        month=time_d.month,
        day=time_d.day,
        hour=time_d.hour,
        minute=time_d.minute,
        second=time_d.second,
        tzinfo=datetime.timezone.utc)

    time_datetime = time_d_with_tz.strftime("%a, %d %b %Y %H:%M:%S %Z")
    request_message += 'GET '+ page + ' ' + my_HTTP_version + '\r\n'
    request_message += 'Host: ' + IP + ':' + port + '\r\n'
    request_message += 'User-Agent: my_client\r\nAccept: text/html,application/xhtml+xml\r\nAccept-Language: en-us,en;q=0.5\r\nAccept-Encoding: gzip,deflate\r\nAccept-Charset: ISO-8859-1,utf-8;q=0.7\r\nKeep-Alive: 115\r\nConnection: keep-alive\r\n'
    request_message += 'If-Modified-Since: '+time_datetime+'\r\n'
    request_message += '\r\n'
else:
    print('Wrong option')
    exit()
    
# ---- send request ----

# Specify Server Address
serverName = IP
serverPort = int(port)

# Create TCP Socket for Client
clientSocket = socket(AF_INET, SOCK_STREAM)

# Connect to TCP Server Socket
clientSocket.connect((serverName,serverPort))

clientSocket.send(request_message.encode())


clientSocket.settimeout(5)
    
try:
    response = clientSocket.recv(1024)
except Exception as e:
    print('\n408 Request Timed Out\n')
    clientSocket.close()

else:
    # Print out the received string
    clientSocket.settimeout(None)
    print ('\nFrom Server:\n'+ response.decode())
    # Close the socket
    clientSocket.close()

# Code   Message
# 200    OK
# 304    Not Modified
# 400    Bad request
# 404    Not Found
# 408    Request Timed Out
