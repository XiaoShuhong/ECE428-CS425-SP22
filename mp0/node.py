from socket import *
import sys
import time

#node.py get exactly 3 argments, 
#The first argument of command node is the node name, and the second and the third arguments 
#are the IP address and the port number of the centralized logger

def main():
    if len(sys.argv) != 4:
        print("node missing parameter")
        return
    else:  
        node = sys.argv[1]
        ip_addr = sys.argv[2]
        port = int(sys.argv[3])
        #create socket
        with socket(AF_INET, SOCK_STREAM) as s:
            #link server
            s.connect((ip_addr,port))
            #connect event,send connect info
            
            msg_connect = "{0} - {1} connected\n".format(time.time(),node)
            #print(msg_connect)
            ## f'{time.time()} - {node} connected'
            s.send(msg_connect.encode("utf-8"),MSG_NOSIGNAL)
            #get event from generator
            flag=1
            while flag:
                for packet in sys.stdin:
                    #print(packet)
                    if len(packet)!=0:
                        t=packet.split(" ")[0]
                        msg=packet.split(" ")[1]
                        # print(t,msg)
                        ## msg_event=f'{t} {node}\n'f'{msg}'
                        msg_event="{0} {1} {2}".format(t,node,msg)
                        #print(msg_event)
                        s.send(msg_event.encode("utf-8"),MSG_NOSIGNAL)
                    
                msg_disconnect = "{0} - {1} disconnected\n".format(time.time(),node)
                s.send(msg_disconnect.encode("utf-8"),MSG_NOSIGNAL)
                flag=0
            print("finish sending")
                        
                    
        
            
            
if __name__ == '__main__':
    main()
    
        
        
          
