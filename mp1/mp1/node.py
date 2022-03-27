from platform import node
import sys 
import socket
from threading import Thread

# print(sys.argv)

def read_config(filename):
    with open(filename) as f:
        node_num=int(f.readline())
        # print(node_num)
        node_info=[]
        for _ in range(node_num):
            node_info.append(f.readline())
        # print(node_info)
    return node_info

def tcp_listen(host,port):
    tcp_server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    address=(host,port)
    tcp_server_socket.bind(address)
    tcp_server_socket.listen(128)
    while True:
        client_socket,clientAddr = tcp_server_socket.accept()
        new_recv=Thread(target=tcp_recvdata,args=(client_socket,clientAddr))
        new_recv.start()
        
    tcp_server_socket.close()  
          
def tcp_recvdata(client_socket,clientAddr):
    while True:
        recv_data=client_socket.recv(128)
        if recv_data:
            recv_data=recv_data.decode("utf-8")
        else:
            break
    client_socket.close()
    
def tcp_connect(target_ip,target_port):
    while True:
        tcp_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_addr=(target_ip,target_port)
        connect_return=tcp_socket.connect(server_addr)
        if (connect_return==0):
            break
    return tcp_socket
    
    
def main():
    if len(sys.argv) != 4:
        print('Incorrect input arguments')
        sys.exit(0)
    node_name = sys.argv[1]
    port = int(sys.argv[2])
    host = '127.0.0.1' # can connect with any ip
    config_fname = sys.argv[3]
    node_info_list=read_config(config_fname)
    tcp_socket_dict=dict()
    for e in node_info_list:
        node_id=e.split(" ")[0]
        node_ip_addr=e.split(" ")[1]
        node_port=int(e.split(" ")[2])
        #print(node_id,node_ip_addr,node_port)
        new_connect=Thread(target=tcp_connect,args=(node_ip_addr,node_port))
        socket_return=new_connect.start()
        tcp_socket_dict[node_id]=socket_return
        
    

if __name__ == "__main__":
    main()