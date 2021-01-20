#!/usr/bin/python

from urllib import urlopen
import threading
import re
import datetime
import os

CHECK_INTERVAL = 60 # Time in seconds between IP checks

# Returns WAN IP as a string. Yeah, it's hacky, but this whole solution is a band-aid anyways
def getPublicIp():
    data = str(urlopen('http://checkip.dyndns.com/').read())
    # data = '<html><head><title>Current IP Check</title></head><body>Current IP Address: 65.96.168.198</body></html>\r\n'

    return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)

myIP = getPublicIp()
print("Starting IP Set to: " + myIP)

def updateGitRepo(newIP):
    myIP = newIP
    os.system("echo \"http://" + myIP + ":15015\" > address")
    os.system("git add address")
    os.system("git commit -m \"Updated address to " + myIP + "\"")
    os.system("git push origin master")

def checkIP():
    threading.Timer(CHECK_INTERVAL, checkIP).start()

    newIP = getPublicIp()
    if newIP == myIP:
        print(str(datetime.datetime.now()) + " | IP didn't change.")
    else:
        print(str(datetime.datetime.now()) + " | IP HAS CHANGED!!")
        print("  OLD IP: " + myIP)
        print("  NEW IP: " + newIP)
        updateGitRepo(newIP)


threading.Timer(CHECK_INTERVAL, checkIP).start()
