from platform import node
from re import L
import sys 
import socket
from threading import Thread,Lock
import json
import time

ALL_CONNECTED=0
id=0      
node_name=''
msg_see_before=[]
connection_bulid=[]
tcp_socket_dict=dict()
timestamp=0
timestamp_lock=Lock() 
tcp_connect_lock=Lock()
msg_see_before_lock=Lock()
myqueue_lock=Lock()
connection_bulid_lock=Lock()
tcp_socket_dict_lock=Lock()
class Myqueue:
    def __init__(self):
        self.queue=[]
        self.numitem=0
        self.recv_feedback=dict()
        self.balance_dict=dict()   # dictionary to keep track of balance of all node
    def insert_msg(self,msg,original_SenderNodeName):
        if self.numitem==0:
            self.queue.append(msg)
            self.recv_feedback[msg.MessageID]=[]   # dictionary, put in the nodename that has given a reply
            self.recv_feedback[msg.MessageID].append(original_SenderNodeName)
            self.numitem+=1
        else:
            # insert the message to the proper place it should be at
            for i in range(self.numitem):
                msg_node=msg.sequence_number.split('.')[0]   # node id
                msg_t=int(msg.sequence_number.split('.')[1])    # timestamp
                cur_node=self.queue[i].sequence_number.split('.')[0]
                cur_t=int(self.queue[i].sequence_number.split('.')[1])
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

    def delete_recv_feedback(self,msg):
        if msg.MessageID not in self.recv_feedback.keys():
            return -1
        else:
            del self.recv_feedback[msg.MessageID]

    def update_msg_priority_and_reorder(self,msg):
        #update priority
        if self.numitem==0:
            return -1
        else:
            index=self.find_msg_index(msg)
            msg_node=msg.sequence_number.split('.')[0]
            msg_t=int(msg.sequence_number.split('.')[1])
            cur_node=self.queue[index].sequence_number.split('.')[0]
            cur_t=int(self.queue[index].sequence_number.split('.')[1])
            if msg_t>cur_t or (msg_t==cur_t and msg_node>cur_node ):
                self.queue[index].sequence_number=msg.sequence_number

                # reorder
            for i in range(self.numitem):
                cur_node=self.queue[i].sequence_number.split('.')[0]
                cur_t=int(self.queue[i].sequence_number.split('.')[1])
                tar_node=self.queue[index].sequence_number.split('.')[0]
                tar_t=int(self.queue[index].sequence_number.split('.')[1])
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
    file= {
        "SenderNodeName":msg.SenderNodeName,
        "Content":msg.Content,
        "MessageID":msg.MessageID,
        "sequence_number":msg.sequence_number,
        "p": "0"
    }    
    file['p']=" "*(129-len(str(file)))
    # print(file)
    # print(len(str(file)))
    return file
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
    tcp_server_socket.listen()
   
    return tcp_server_socket
     
          
# def tcp_recvdata(tcp_server_socket):
#     while True:
#         client_socket,clientAddr = tcp_server_socket.accept()
#         recv_data=client_socket.recv(128)
#         if recv_data:
#             recv_data=recv_data.decode("utf-8")
        
    
def tcp_connect(target_ip,target_port,tcp_socket_dict,node_id):
    global ALL_CONNECTED
    while True:
        try:
            tcp_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_addr=(target_ip,target_port)
            connect_return = tcp_socket.connect_ex(server_addr)

            if (connect_return==0):   # 0 = success
                tcp_connect_lock.acquire()   ##add lock to avoid bug1
                ALL_CONNECTED+=1      #######potential bug1: a possibility that many connection update on the same ALL_CONNECTED to make it just +1 instead of +n ############
                tcp_connect_lock.release()  
                break
        except:
            continue
    tcp_socket_dict_lock.acquire()
    tcp_socket_dict[node_id]=tcp_socket
    tcp_socket_dict_lock.release()
    
    return tcp_socket

def deliver_queue_head(msg):   # deliver the queue head to application layer and delete it from the queue
    global connection_bulid
    global myqueue
    print("point 31")
    myqueue_lock.acquire()
    feed_back_recv= myqueue.recv_feedback[msg.MessageID]
    print("feed_back_recv is:",feed_back_recv)
    myqueue_lock.release()
    flag=1
    connection_bulid_lock.acquire()
    print("point 32")
    for conn in connection_bulid:
        if conn not in feed_back_recv:
            flag=0 
    connection_bulid_lock.release()
    print("point 33")
    if flag==1:
        print("point 34")
        update_balances(msg)
        print("point 35")
        myqueue_lock.acquire()
        print("point 36")
        myqueue.delete_msg(msg)
        print("point 37")
        myqueue.delete_recv_feedback(msg)
        print("point 38")
        myqueue_lock.release()
        print("point 39")
    
def update_balances(msg):
    global myqueue

    operation = msg.Content.split()[0]
    if operation == 'DEPOSIT':
        myqueue_lock.acquire()
        if msg.Content.split()[1] not in myqueue.balance_dict.keys():
            myqueue.balance_dict[msg.Content.split()[1]]=0
        myqueue.balance_dict[msg.Content.split()[1]] += int(msg.Content.split()[2])
        myqueue_lock.release()

    elif operation == 'TRANSFER':
        myqueue_lock.acquire()
        if myqueue.balance_dict[msg.Content.split()[1]]>=int(msg.Content.split()[4]):
            myqueue.balance_dict[msg.Content.split()[1]] -= int(msg.Content.split()[4])
            myqueue.balance_dict[msg.Content.split()[3]] += int(msg.Content.split()[4])
            myqueue_lock.release()
        else:
            myqueue_lock.release()
            print('No enough balance for TRANSFER in ',msg.Content.split()[1],'!')
            return -1
    else:
        print('Invalid operation! Please input DEPOSIT or TRANSFER!')
        return -1

    # update self balance
    myqueue_lock.acquire()
    BALANCES_log = 'BALANCES '
    for account_id in myqueue.balance_dict.keys():
        BALANCES_log = BALANCES_log + str(account_id) + ':' + str(myqueue.balance_dict[account_id]) + ' '
    print(BALANCES_log)
    myqueue_lock.release()


def deliver(msg):  # upon receive a message
    global msg_see_before
    global myqueue
    global node_name
    global timestamp

    print("point 1")
    # if have seen before and this time is just a R-multicast from someone else
    msg_see_before_lock.acquire()
    if msg.MessageID in msg_see_before:
        print("point 2")
        msg_see_before_lock.release()
        myqueue_lock.acquire()
        myqueue.update_msg_priority_and_reorder(msg)
        myqueue.update_msg_recv_feedback(msg,msg.SenderNodeName)
        myqueue_lock.release()

    # if this is the first time to see this message
    else: 
        print("point 3")
        msg_see_before_lock.release()
        original_SenderNodeName=msg.SenderNodeName
        msg.SenderNodeName=node_name  # self nodename?
        pre_sequence_number=msg.sequence_number
        pre_node=pre_sequence_number.split('.')[0]
        pre_t=int(pre_sequence_number.split('.')[1])
        timestamp_lock.acquire()
        if(timestamp>pre_t or (timestamp==pre_t and node_name>pre_node)):
            msg.sequence_number=node_name+'.'+str(timestamp)
            timestamp+=1
            timestamp_lock.release()
        else:
            timestamp_lock.release()

        msg_see_before_lock.acquire()
        msg_see_before.append(msg.MessageID)
        msg_see_before_lock.release()
        myqueue_lock.acquire()
        myqueue.insert_msg(msg,original_SenderNodeName)
        myqueue_lock.release()


    
def multicast(msg):
    global connection_bulid
    global tcp_socket_dict
    print("point 4")
    local_connect_copy=[]
    connection_bulid_lock.acquire()
    for e in connection_bulid:
        local_connect_copy.append(e)
    connection_bulid_lock.release()
    print("point 5")
    send_data=json.dumps(msg,default=msgobj_2_json).encode('utf-8')  # the encoded data need to be sent
    for conn in local_connect_copy:
        tcp_connect_lock.acquire()
        #print(tcp_socket_dict)
        tcp_socket=tcp_socket_dict[conn]
        # print("tcp_socket:",tcp_socket)
        # print("type of tcp_socket",type(tcp_socket))
        tcp_connect_lock.release()
        print("point 6")
        print("send data:",send_data,"to",conn)
        send_res=tcp_socket.send(send_data)
        print("point 7")
        if send_res<0:  # if target node failed
            print("point 8")
            connection_bulid_lock.acquire()
            connection_bulid.remove(conn)
            connection_bulid_lock.release()
            deliver_queue_head(msg)
 
def receive_message(tcp_server_socket):
    global msg_see_before
    global myqueue
    while True:
        client_socket, clientAddr = tcp_server_socket.accept()
        recv_data=client_socket.recv(128).decode('utf-8')
        print("point 9")
        
        if len(recv_data)>0:
            print("receive data:",recv_data,"from client socket",client_socket)
            msg=json.loads(recv_data,object_hook=json_2_msgobj)
            msg_see_before_lock.acquire()
            if msg.MessageID in msg_see_before:
                msg_see_before_lock.release()
                print("point 10")
                deliver(msg)
                print("point 11")
                deliver_queue_head(msg)
                print("point 12")
                
            else:
                msg_see_before_lock.release()
                print("point 13")
                deliver(msg)
                print("point 14")
                multicast(msg)
                print("point 15")
            
def get_events():
    global node_name
    global timestamp
    while True:
        for line in sys.stdin:
            if len(line)!=0:
                # print(line)
                timestamp_lock.acquire()
                print("point 21")
                MessageID=node_name+'.'+str(timestamp)
                print("point 22")
                sequence_number=node_name+'.'+str(timestamp)
                print("point 23")
                timestamp+=1
                print("point 24")
                timestamp_lock.release()
                print("point 25")
                new_msg=Message(node_name,line,MessageID,sequence_number)
                print("point 26")
                deliver(new_msg)  # deliver to self
                print("point 27")
              
                multicast(new_msg)  # send to others
                print("point 28")
   

def main():
    if len(sys.argv) != 4:
        print('Incorrect input arguments')
        sys.exit(0)
    global node_name
    global connection_bulid
    global tcp_socket_dict
    global ALL_CONNECTED
    node_name = sys.argv[1]
    port = int(sys.argv[2])
    host = '127.0.0.1' # can connect with any ip
    config_fname = sys.argv[3]

    #### update: open a new thread for listening (there may be bugs), since main thread is used to read stdin ########
    ### no need to run with a new thread, tcp_listen end quickly
    
    node_num,node_info_list=read_config(config_fname)
    for e in node_info_list:
        node_id=e.split(" ")[0]
        connection_bulid_lock.acquire()
        connection_bulid.append(node_id)
        connection_bulid_lock.release()
        node_ip_addr=e.split(" ")[1]
        node_port=int(e.split(" ")[2])
        new_connect=Thread(target=tcp_connect,args=(node_ip_addr,node_port,tcp_socket_dict,node_id))
        new_connect.start()
        
    
    time.sleep(5)
    listen_socket=tcp_listen(host,port)
    my_listen=Thread(target=receive_message,args=(listen_socket,))
    my_listen.start()
        
    while True:
        tcp_connect_lock.acquire()
        if ALL_CONNECTED==node_num:   ##### bug!!!! ##### 
            tcp_connect_lock.release()
            break
        tcp_connect_lock.release()
 
    # Normal working process
    while True:
        # print("success")
        
        get_events()


    # pass
    

            

if __name__ == "__main__":
    main()