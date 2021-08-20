#!/usr/bin/python

from urllib import urlopen
import threading
import re
import datetime
import os
import time
import subprocess

CHECK_INTERVAL = 60 # (1m) Time in seconds between IP checks
ALERT_INTERVAL = 899.5 # (15m) Time in between print statements that IP did not change

# Returns WAN IP as a string. Yeah, it's hacky, but this whole solution is a band-aid anyways
def getPublicIp():
    data = str(urlopen('http://checkip.dyndns.com/').read())
    # data = '<html><head><title>Current IP Check</title></head><body>Current IP Address: 65.96.168.198</body></html>\r\n'

    return re.compile(r'Address: (\d+\.\d+\.\d+\.\d+)').search(data).group(1)

def readIpFromFile():
    with open('address', 'r') as file:
        data = file.read()
        return re.compile(r'http://(\d+\.\d+\.\d+\.\d+):').search(data).group(1)

lastAlert = 0
myIP = readIpFromFile()
print("Starting IP Set to: " + myIP)

# Runs a shell command. retval[0] = return code, retval[1] = output, retval[2] = error output
def runcommand (cmd):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)
    std_out, std_err = proc.communicate()
    return proc.returncode, std_out, std_err

gitPushFailed = False
def updateGitRepo(newIP):
    global myIP
    global gitPushFailed
    if gitPushFailed == False or readIpFromFile() != newIP:
        # If there was a push failure, the commit has already been made but it hasn't been pushed up.
        print("Making a new commit for the updated IP")
        os.system("echo \"http://" + newIP + ":15015\" > address")
        os.system("git add address")
        os.system("git commit -m \"Updated address to " + newIP + "\"")
    # Following command may fail if there are network issues. So check for that.
    pushResult = runcommand("git push origin master")
    if pushResult[0] == 0:
        myIP = newIP
        gitPushFailed  = False
        print(pushResult[1])
    else:
        gitPushFailed = True
        print("!! Failed to upload git! Will try again next interval !!")
        print(pushResult[2])

def checkIP():
    global lastAlert
    threading.Timer(CHECK_INTERVAL, checkIP).start()

    try:
        newIP = getPublicIp()
        if newIP == myIP:
            if (time.time() - lastAlert) >= ALERT_INTERVAL:
                lastAlert = time.time()
                print(str(datetime.datetime.now()) + " | IP didn't change.")
        else:
            print(str(datetime.datetime.now()) + " | IP HAS CHANGED!!")
            print("  OLD IP: " + myIP)
            print("  NEW IP: " + newIP)
            updateGitRepo(newIP)
    except Exception as error:
        print("Failed to get IP.\n" + str(error))

checkIP()
