import re

from sys import flags

Headers = []
Lines = []

mode = 'n'
loadedFile = None

commands = {
    r"^exit$": lambda _ : exit(1),
    r"^print ?(\d*) ?(\d*)$": lambda args : printLines(*args), 
    r"^save ?(.*)$": lambda args : saveFile(*args),
    r"^write$": lambda _ : writeMode()
}

def yesNo():
    while True:
        yn = raw_input("y/n > ")
        if(yn == "y"):
            return True
        elif(yn == "n"):
            return False

def saveFile(path=None):
    if(not path and not loadedFile):
        print("save $path")
        return
    elif(not path):
        print("Save to %s?(will delete old file)" % loadedFile)
        if(yesNo()):
            path = loadedFile
        else:
            return

    outStr = ",".join(Headers)
    
    for l in Lines:
        outStr += "\n" + ",".join(l)

    f = None
    try:
        f = open(path,"wt")
        f.write(outStr)
    except:
        print("Failed to save")
    finally:
        if(f):
            f.close()
    
def loadFile(path):
    global Headers
    global loadedFile
    global Lines
    global Headers

    if(len(Headers) != 0):
        print("Loading a new file will clear all loaded data")
        print("You will lose %s lines" % len(Lines))
        print("Load file?")
        if(not yesNo()):
            return
        Lines = []
        Headers = []


    try:
        f = open(path)
        lines = f.readlines()
        Headers = lines[0].replace("\n","").split(",")
        lines = lines[1::]

        for line in lines:
            Lines.append(line.replace("\n","").split(","))
        
        loadedFile = path

    except:
        print("Failed to load file")
        return

    print("Loaded %s")
    print("Headers:\n%s" % ",".join(Headers))
    print("%s line" % len(Lines))

def readLine(promt = "> "):
    data = raw_input(promt)

    for r in commands.keys():
        m = re.match(r,data)
        if(m):
            commands[r](m.groups())
            return
    return data if data != "" else None

def printLines(start=None, end=None):

    start = int(start) if start else 0
    end = int(end) if end else len(Lines)-1

    if(len(Lines) == 0):
        print("No lines to print")
        return
    if(start < 0 or start > end or end >= len(Lines)):
        print("print $start $end")
        return

    while start <= end:
        print(",".join(Lines[start]))
        start += 1

def modLine(line, field):
    if(len(Lines) == 0):
        print("No lines to change")
        return
    
    start = 0;
    end = 0;
    if(field):
        start = field
        end = field
    
    

def writeMode():
    if(len(Headers) == 0):
        raise Exception("TODO") 

    print("Start write mode. use !exit to exit")
    print("###########")
    print(",".join(Headers))
    print("###########")

    headIndex = 0
    tmpLine = []
    while(True):
        data = raw_input("[%s] %s > " % (len(Lines),Headers[headIndex]))
        
        if(data == "!exit"):
            print("Exit write mode!")
            return
        elif(data == ""):
            continue
            
        tmpLine.append(data)
        if(len(tmpLine) == len(Headers)):
            Lines.append(tmpLine)
            tmpLine = []
            headIndex = 0
        else:
            headIndex += 1



if __name__ == "__main__" and not flags.interactive:
    loadFile("test.csv")
    while True:
        res = readLine()
        if(res):
            print("No command %s" % res)