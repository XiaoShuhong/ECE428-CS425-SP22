from socket import *
import sys
from threading import Thread
import time
import csv
def main():
    if len(sys.argv)!=2:
        print("logger missing parameter")
        return 
    else:
        port = int(sys.argv[1])
        #create socket
        with socket(AF_INET,SOCK_STREAM) as s:
            s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        #local info
            local_ip='127.0.0.1'
            address=(local_ip,port)
            #bind
            s.bind(address)
            #negative listen
            s.listen(SOMAXCONN)
            #keep waiting client
            while True:
                client_socket,clientAddr = s.accept()
                #for each event, open a new thread to process
                new_event=Thread(target=log,args=(client_socket,))
                new_event.start()
def log(s):
    #receive data from client socket, decode back to string
    while True:
        recv_data = s.recv(128).decode("utf-8")
        
        if len(recv_data)!=0:
            print(recv_data)
            rece_list=recv_data.split(" ")
            if len(rece_list)==3:
                node= rece_list[1]
                gene_time=float(rece_list[0])
                rece_time=time.time()
                delay=(rece_time-gene_time)*1000
                bandwidth=len(recv_data)/delay
                csv_data=[node,delay,bandwidth]
                
                w.writerow(csv_data)
            # print(recv_data.split(" "))
            # # if recv_data.split(" ")[1]!="-":
            #     cur_time=time.time()
            #     generate_time=float(recv_data.split(" ")[0])
            #     if recv_data.split(" ")[1]=="-":

            #         node=recv_data.split(" ")[2]
            #     else:
            #         node=recv_data.split(" ")[1]
            #     delay=cur_time-generate_time
            #     # print(node,delay)
           
    
        
        # gen_time=recv_data.split(" ")[0]
        
    
    


if __name__ == '__main__':
    with open("data.csv",mode="w") as f:
        w=csv.writer(f)
        h=['node','delay[sec]','bandwidth[bytes/sec]']
        w.writerow(h)
        main()
    