from platform import node
import sys 
import socket
import threading

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
            

    
def main():
    if len(sys.argv) != 4:
        print('Incorrect input arguments')
        sys.exit(0)
    node_name = sys.argv[1]
    port = int(sys.argv[2])
    host = '' # can connect with any ip
    config_fname = sys.argv[3]
    node_info_list=read_config(config_fname)
    for e in node_info_list:
        node_id=e.split(" ")[0]
        node_ip_addr=e.split(" ")[1]
        node_port=int(e.split(" ")[2])
        print(node_id,node_ip_addr,node_port)
    

if __name__ == "__main__":
    main()