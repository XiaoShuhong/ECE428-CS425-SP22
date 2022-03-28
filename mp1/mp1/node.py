from platform import node
import sys 
import socket
from threading import Thread
import json


ALL_CONNECTED=0
id=0      
node_name=''
msg_see_before=[]
connection_bulid=[]
tcp_socket_dict=dict()
timestamp=0
class Myqueue:
    def __init__(self):
        self.queue=[]
        self.numitem=0
        self.recv_feedback=dict()
    def insert_msg(self,msg):
        if self.numitem==0:
            self.queue.append(msg)
            self.recv_feedback[msg.MessageID]=[]
            self.numitem+=1
        else:
            for i in range(self.numitem):
                msg_node=msg.sequence_number.split('.')[0]
                msg_t=msg.sequence_number.split('.')[1]
                cur_node=self.queue[i].sequence_number.split('.')[0]
                cur_t=self.queue[i].sequence_number.split('.')[1]
                if msg_t<cur_t or (msg_t==cur_t and msg_node<cur_node):
                    self.queue.insert(i,msg)
                    self.recv_feedback[msg.MessageID]=[]
                    self.numitem+=1
                    break
                else:
                    if i==self.numitem-1:
                        self.queue.append(msg)
                        self.recv_feedback[msg.MessageID]=[]
                        self.numitem+=1
                        
    def find_msg_index(self,msg):
        if self.numitem==0:
            return -1
        else:
            for i in range(self.numitem):
                if self.queue[i].MessageID==msg.MessageID:
                    return i
        return -1
    
    def delete_msg(self,msg):
        if self.numitem==0:
            return -1
        else:
            index=self.find_msg_index(msg)
            del self.queue[index]
            del self.recv_feedback[msg.MessageID]
            self.numitem-=1
            return 0
    
    def update_msg_priority_and_reorder(self,msg):
        if self.numitem==0:
            return -1
        else:
            index=self.find_msg_index(msg)
            msg_node=msg.sequence_number.split('.')[0]
            msg_t=msg.sequence_number.split('.')[1]
            cur_node=self.queue[index].sequence_number.split('.')[0]
            cur_t=self.queue[index].sequence_number.split('.')[1]
            if msg_t>cur_t or (msg_t==cur_t and msg_node>cur_node ):
                self.queue[index].sequence_number=msg.sequence_number
            for i in range(self.numitem):
                cur_node=self.queue[i].sequence_number.split('.')[0]
                cur_t=self.queue[i].sequence_number.split('.')[1]
                tar_node=self.queue[index].sequence_number.split('.')[0]
                tar_t=self.queue[index].sequence_number.split('.')[1]
                if tar_t<cur_t or (tar_t==cur_t and tar_node<cur_node):
                    temp=self.queue[i]
                    self.queue[i]=self.queue[index]
                    self.queue[index]=temp
                    break
                else:
                    if i==self.numitem-1:
                        temp=self.queue[i]
                        self.queue[i]=self.queue[index]
                        self.queue[index]=temp
                
            
                
    def update_msg_recv_feedback(self,msg,nodename):
        if msg.MessageID not in self.recv_feedback.keys():
            return -1
        else: 
            self.recv_feedback[msg.MessageID].append(nodename)
            return 0
        
def msgobj_2_json(msg):
    return {
        "SenderNodeName":msg.SenderNodeName,
        "Content":msg.Content,
        "MessageID":msg.MessageID,
        "sequence_number":msg.sequence_number
    }    
def json_2_msgobj(d):
    return Message(d['SenderNodeName'],d['Content'],d['MessageID'],d['sequence_number'])    
    

myqueue=Myqueue()
class Message:
    def __init__(self,SenderNodeName,Content,MessageID,sequence_number):
        self.SenderNodeName = SenderNodeName
        self.Content = Content
        self.MessageID = MessageID   # "node1.1"  id = node name + message timestamp when sending
        self.sequence_number = sequence_number  # the priority "node1.1"


        
def read_config(filename):
    with open(filename) as f:
        node_num=int(f.readline())
        # print(node_num)
        node_info=[]
        for _ in range(node_num):
            node_info.append(f.readline())
        #print(node_info)
    return node_num,node_info

def tcp_listen(host,port):
    tcp_server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
    address=(host,port)
    tcp_server_socket.bind(address)
    tcp_server_socket.listen(128)
    return tcp_server_socket
     
          
# def tcp_recvdata(tcp_server_socket):
#     while True:
#         client_socket,clientAddr = tcp_server_socket.accept()
#         recv_data=client_socket.recv(128)
#         if recv_data:
#             recv_data=recv_data.decode("utf-8")
        
    
def tcp_connect(target_ip,target_port):
    global ALL_CONNECTED
    while True:
        tcp_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_addr=(target_ip,target_port)
        connect_return=tcp_socket.connect(server_addr)
        if (connect_return==0):
            ALL_CONNECTED+=1      #######potential bug1#############
            break
    return tcp_socket

def deliver_queue_head():
    
    pass

def deliver(msg):
    global msg_see_before
    global myqueue
    global node_name
    global timestamp
    if msg.MessageID in msg_see_before:
        myqueue.update_msg_priority_and_reorder(msg)
        myqueue.update_msg_recv_feedback(msg,msg.SenderNodeName)
    else: 
        msg.SenderNodeName=node_name
        pre_sequence_number=msg.sequence_number
        pre_node=pre_sequence_number.split('.')[0]
        pre_t=pre_sequence_number.split('.')[1]
        if(timestamp>pre_t or (timestamp==pre_t and node_name>pre_node)):
            msg.sequence_number=node_name+'.'+str(timestamp)
            timestamp+=1
        msg_see_before.append(msg.MessageID)
        myqueue.insert_msg(msg)
    
def multicast(msg):
    global connection_bulid
    global tcp_socket_dict
    local_connect_copy=[]
    for e in connection_bulid:
        local_connect_copy.append(e)
    send_data=json.dumps(msg,default=msgobj_2_json).encode('utf-8')
    for conn in local_connect_copy:
        tcp_socket=tcp_socket_dict[conn]
        send_res=tcp_socket.send(send_data)
        if send_res<0:
            connection_bulid.remove(conn)
            deliver_queue_head()
 
def receive_message(tcp_server_socket):
    global msg_see_before
    global myqueue
    while True:
        client_socket, clientAddr = tcp_server_socket.accept()
        recv_data=client_socket.recv(128).decode('utf-8')
        msg=json.loads(recv_data,object_hook=json_2_msgobj)
        if msg.MessageID in msg_see_before:
            deliver(msg)
            deliver_queue_head()
        else:
            deliver(msg)
            multicast(msg)
            
def get_events():
    global node_name
    global timestamp
    while True:
        for line in sys.stdin:
            if len(line)!=0:
                MessageID=node_name+'.'+str(timestamp)
                sequence_number=node_name+'.'+str(timestamp)
                timestamp+=1
                new_msg=Message(node_name,line,MessageID,sequence_number)
                deliver(new_msg)
                multicast(new_msg)      
    
def main():
    if len(sys.argv) != 4:
        print('Incorrect input arguments')
        sys.exit(0)
    global node_name
    global connection_bulid
    node_name = sys.argv[1]
    port = int(sys.argv[2])
    host = '127.0.0.1' # can connect with any ip
    config_fname = sys.argv[3]
    listen_socket=tcp_listen(host,port)
    node_num,node_info_list=read_config(config_fname)
    global tcp_socket_dict
    global ALL_CONNECTED
    for e in node_info_list:
        node_id=e.split(" ")[0]
        connection_bulid.append(node_id)
        node_ip_addr=e.split(" ")[1]
        node_port=int(e.split(" ")[2])
        #print(node_id,node_ip_addr,node_port)
        new_connect=Thread(target=tcp_connect,args=(node_ip_addr,node_port))
        socket_return=new_connect.start()
        tcp_socket_dict[node_id]=socket_return
    while True:
        if ALL_CONNECTED==node_num:
            break
    # my_listen=Thread(target=tcp_recvdata,args=(listen_socket,))
    # my_listen.start()
    
    pass
    

            

if __name__ == "__main__":
    main()