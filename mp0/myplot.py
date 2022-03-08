import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

text=['0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
Ra=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
maxdelay=[]
mindelay=[]
avgdelay=[]
maxband=[]
minband=[]
avgband=[]
for i in range(len(text)):
    f = "Ra{0}.csv".format(text[i])
    data=np.array(pd.read_csv(f,usecols=['node','delay[sec]','bandwidth[bytes/sec]']))
    delay=data[:,1]
    bandwidth=data[:,2]
    maxdelay.append(np.max(delay))
    mindelay.append(np.min(delay))
    avgdelay.append(np.mean(delay))
    maxband.append(np.max(bandwidth))
    minband.append(np.min(bandwidth))
    avgband.append(np.mean(bandwidth))

plt.figure(1)
L1,=plt.plot(Ra, maxdelay , color="r", linestyle="-")
plt.xlabel('Ra')
plt.ylabel('sec')
plt.legend([L1],['maxdelay'],loc='upper right')
plt.savefig('./maxdelay.jpg')

plt.figure(2)
L2,=plt.plot(Ra, mindelay , color="b", linestyle="-")
plt.xlabel('Ra')
plt.ylabel('sec')
plt.legend([L2],['mindelay'],loc='upper right')
plt.savefig('./mindelay.jpg')

plt.figure(3)
L3,=plt.plot(Ra, avgdelay , color="g", linestyle="-")
plt.xlabel('Ra')
plt.ylabel('sec')
plt.legend([L3],['avgdelay'],loc='upper right')
plt.savefig('./avgdelay.jpg')

plt.figure(4)
L1,=plt.plot(Ra, maxband , color="r", linestyle="-")
plt.xlabel('Ra')
plt.ylabel('bytes/sec')
plt.legend([L1],['maxband'],loc='upper right')
plt.savefig('./maxbandwidth.jpg')

plt.figure(5)
L2,=plt.plot(Ra, minband , color="b", linestyle="-")
plt.xlabel('Ra')
plt.ylabel('bytes/sec')
plt.legend([L2],['minband'],loc='upper right')
plt.savefig('./minbandwidth.jpg')

plt.figure(6)
L3,=plt.plot(Ra, avgband , color="g", linestyle="-")
plt.xlabel('Ra')
plt.ylabel('bytes/sec')
plt.legend([L3],['avgband'],loc='upper right')
plt.savefig('./avgbandwidth.jpg')

