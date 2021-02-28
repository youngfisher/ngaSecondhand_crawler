import subprocess

#this program is to keep another py programm running all the time
#from url:https://www.coder.work/article/1281040

filename = 'crawling_secondhand.py'
while True:
    p = subprocess.Popen('python ' + filename, shell = False).wait()

    #wait()returns p.returncode. search for subprocess
    if p != 0:
        continue 
    else:
        break   

