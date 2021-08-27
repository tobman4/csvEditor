import re
import argparse

from sys import flags # only used for DBG

Headers = []
Lines = []

mode = 'n'
loadedFile = None

"""

one command is an array of 3 or 4 items
[ {name}, {regex}, {cb}, {help} ]

name:
    prety name of command
regex:
    regex used to match command to input
cb:
    a call back that takes 1 argument that is the groups returnd by the regex. the argument can be null
help:
    a help string used by the help command. this can be null
"""
commands = [
    ["exit",r"^exit$",lambda _ : exit(1),"Exit the program. this dont save anything."],
    ["print",r"^print ?(\d*) ?(\d*)$",lambda args : printLines(*args),"Print lines in the current table. \"print startLine? endLine?\""],
    ["save",r"^save ?(.*)$",lambda args : saveFile(*args), "Save the current table to file. \"save filePath?\""],
    ["load",r"^load ?(.*)$",lambda args : loadFile(*args), "Load a file. \"load filePath\""],
    ["new",r"^new$",lambda _ : startNew(), "Start a new table" ],
    ["write",r"^write$",lambda _ : writeMode(),"Enter write mode to add lines to the current table"],
    ["mod",r"^mod ?(\d*) ?(\d*)$",lambda args :modLine(*args),"Modify a line. \"mod lineIndex fieldIndex?\""],
    ["help",r"^help$", lambda _ : getHelp(), "Get all commands"]
]

def getHelp():
    print("csv editor commands")
    for com in commands:
        line = "%s\t\t%s" % (com[0], com[3] if len(com) == 4 else "No help text")
        print(line)
    return # no help

def _toFancyStr(toPrint,spliter=","):
    dataStr = spliter.join(toPrint)
    return "%s\n%s\n%s" % ("#"*len(dataStr),dataStr,"#"*len(dataStr))


def needFile(): # used to mark method that need Headers to work
    raise Exception("TODO")

def startNew():
    global Headers
    global Lines

    if(len(Headers) != 0):
        print("Clear current data?")
        if(not yesNo):
            return
        Headers = []
        Lines = []

    print("Write headers. !exit to cancel. !done to to complete. !show to show current headers")
    tmpHeaders = []
    while True:
        data = input("new csv table > ")

        if(data == "!exit"):
            return
        elif(data == "!done"):
            break
        elif(data == "!show"):
            print(",".join(tmpHeaders))
        else:
            tmpHeaders.append(data)
    
    if(len(tmpHeaders) == 0):
        print("No headers saved")
        return
    else:
        Headers = tmpHeaders
        print("New headers\n%s" % ",".join(Headers))


def yesNo():
    while True:
        yn = input("y/n > ")
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
        print("Failed to load file. %s" % path)
        return

    print("Loaded %s" % path)
    print("Headers:\n%s" % ",".join(Headers))
    print("%s line" % len(Lines))

def readLine(promt = "> "):
    data = input(promt)
    for com in commands:
        m = re.match(com[1],data)
        if(m):
            com[2](m.groups())
            return
    return data if data != "" else None

def printLines(start=None, end=None):

    start = int(start) if start else 0
    end = int(end) if end else len(Lines)-1

    if(len(Headers) != 0):
        print(_toFancyStr(Headers))
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
    
    if(not line):
        print("modLine $line [$index]")
        return
    elif(type(line) is not int):
        line = int(line)

    if(line >= len(Lines)):
        print("There is no line %s max is %s" % (line,len(Lines)-1))
        return

    start = 0;
    end = len(Headers)-1
    if(field):
        start = int(field)
        end = int(field)

    if(end >= len(Headers)):
        print("Invalid field")
        return


    oldLine = Lines[line].copy()

    print("Moding line %s. dont write anythin to keep old data" % line)
    print(_toFancyStr(oldLine))
    while(start <= end):
        data = input("[%s] %s > " % (line,Headers[start]))

        if(not data.isspace() and data != ""):
            oldLine[start] = data
        start += 1
    
    print("Line changed \n%s\n%s" % (Lines[line],oldLine))
    Lines[line] = oldLine


def writeMode():
    if(len(Headers) == 0):
        raise Exception("TODO") 

    print("Start write mode. use !exit to exit")
    print(_toFancyStr(Headers))

    headIndex = 0
    tmpLine = []
    while(True):
        data = input("[%s] %s > " % (len(Lines),Headers[headIndex]))
        
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
    parser = argparse.ArgumentParser(description='small cli editor for CSV files :)')
    parser.add_argument('--file',"-f", metavar="path", type=str, help="File to load at start")
    args = parser.parse_args()

    if(args.file):
        loadFile(args.file)

    while True:
        res = readLine()
        if(res):
            print("No command \"%s\"" % res)