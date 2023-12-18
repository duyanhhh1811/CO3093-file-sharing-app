import json
import threading
import socket
from abc import abstractmethod

# the format in which encoding and decoding will occur

FORMAT = "utf-8"
BUFFER_SIZE = 2048

class Base():
    def __init__(self, serverhost='192.168.3.140', serverport=40000, listen_num=100):
        # host and listening port of network peers/central server
        hostname = socket.gethostname()   
        self.serverhost = socket.gethostbyname(hostname)  
        self.serverport = int(serverport)
        
        print(f'\ninit at Base: serverhost: {serverhost}, serverport: {serverport}')
        print(f"self.serverhost: {self.serverhost}, self.serverport:{self.serverport}")
        
        # create server TCP socket (for listening)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to our local address
        self.socket.bind((self.serverhost, self.serverport))
        self.socket.listen(listen_num)
        
        # peerlist: dict with key is peer name and value is tuple (host,port) 
        # Child class CentralServer: connected peers of a network peer
        # Child class NetworkPeer: list of registered peers managed by central server
        self.peerlist = {}
        # used for mapping from MESSAGE TYPE to corresponding function
        self.handlers = {}

    def add_handler(self, msgtype, function): 
        self.handlers[msgtype] = function
        #print(f'\n{self.handlers}, msgtype: {msgtype}, function: {function}, self.handlers[msgtype]: {self.handlers[msgtype]}')

    def function_mapper(self, message):
        _type = message['msgtype']
        _data = message['msgdata']
        self.handlers[_type](_data)
        print(f'\nat function_mapper, message: {message}, self.handlers[_type](_data): {self.handlers[_type](_data)}')

    def recv_input_stream(self, conn):
        # receive from client 
        buf = conn.recv(BUFFER_SIZE)
        message = buf.decode(FORMAT)  
        # deserialize (json type -> python type)
        message = json.loads(message)
        # map into function
        print(f'\nat recv_input_stream, message: {message}, conn: {conn}')
        self.function_mapper(message)

    def input_recv(self):
        while True:
            # wait until receive a connection request -> return socket for connection from client
            conn, addr = self.socket.accept()
            input_stream = threading.Thread(target=self.recv_input_stream, args=(conn,))
            input_stream.daemon = True
            input_stream.start()

    @abstractmethod
    def run(self):
        pass

    @staticmethod
    def client_send(address, msgtype, msgdata):
        # msgtype for mapping into corresponding function
        # msgdata contains sent data
        message = {'msgtype': msgtype, 'msgdata': msgdata}
        # serialize into JSON file for transmitting over network
        message = json.dumps(message).encode(FORMAT)
        # create client TCP socket
        
        print('\nat client_send:')
        print(f'address: {address}, msgtype: {msgtype}, msgdata: {msgdata}')
        print(f'message: {message}')
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # request connection
            s.connect(address)
        except ConnectionRefusedError as e:
            print(e)
            print('Connection Error: Your Peer Refused')
            raise
        else:
            s.sendall(message)
        finally:
            s.close()
        # s.connect(address)
