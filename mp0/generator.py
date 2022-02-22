# import sys
# import time 
# import os
# import codecs
# from random import expovariate
# from threading import Timer

# #generator.py get exactly 2 argments, 
# # first as msg_gen_rate refer to the average rate of generated events/messages, 
# # the second  max_msg_num defines the total number of generated events/messages  

# def msd_generator():
   
#     # timestamp=time.time()
#     digits = 32
#     # msg = codecs.encode(os.urandom(digits), 'hex').decode()
#     print(time.time(),codecs.encode(os.urandom(digits), 'hex').decode(),flush=True)
        
# def main():
#     if len(sys.argv) != 3:
#         print("missing parameter")
#         return
#     else:
#         msg_gen_rate = int(sys.argv[1])
#         max_msg_num = int(sys.argv[2])
#         #print(msg_gen_rate,max_msg_num)
    
#     time_delay=[]
#     # base=0
#     for _ in range(max_msg_num):
        
#         time_delay.append(expovariate(msg_gen_rate))
       
#     # print(time_delay)
        
        
#     for delay in time_delay:
#         timer=Timer(delay,msd_generator)
#         timer.start()
#         timer.join()
        
    
            
# if __name__ == '__main__':
#     main()
    
    
from os import urandom
from hashlib import sha256
from random import expovariate
import time
import sys

if len(sys.argv) > 1:
    rate = float(sys.argv[1])
else:
    rate = 1.0          # default rate: 1 Hz

if len(sys.argv) > 2:
    max_events = int(sys.argv[2])
else:
    max_events = None

event_count = 0
while max_events is None or event_count < max_events:
    event_count += 1
    print("%s %s" % (time.time(), sha256(urandom(20)).hexdigest()))
    time.sleep(expovariate(rate))
