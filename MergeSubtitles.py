#!/usr/bin/python
# Usage: merge-subtitles.py input1.srt input2.srt output.srt offset
# Offset is in MS, time on file2 minus time on file 1
#
# If you are expecting more text in one file over other, use that as file1
# For instance, when watching German movie, English subs might contain text
# that translates on-screen text such as store names, newspaper headlines, etc
#
# Useful when learning a new language


import codecs,re,sys,time

class timeClass:
    # This class translates time string in format 01:23:45,678 into separate 
    # variables for hrs, min, sec, ms, plus a total MS variable
    # this variable can be used to easily change offset
    def __init__(self,timeStr):
        self.timeStr  = timeStr
        self.timeList = re.split("\:|\.|\,",timeStr)
        self.timeNoMs = re.split(",",timeStr)[0]
        self.hrs = int(self.timeList[0])
        self.min = int(self.timeList[1])
        self.sec = int(self.timeList[2])
        self.ms  = int(self.timeList[3])
        self.totalMs = self.ms + (self.sec * 1000) + \
            (self.min * 60000) + (self.hrs * 3600000)
    
    # This method allows you to supply totalMS variable and set the rest 
    # calculated from that value, including time string in subtitle-friendly
    # format
    def msToStr(self,totalMs):
        self.totalMs = totalMs
        self.hrs     = self.totalMs // 3600000
        self.min     = (self.totalMs % 3600000) // 60000 
        self.sec     = (self.totalMs % 3600000) % 60000 // 1000
        self.ms      = (self.totalMs % 3600000) % 60000 % 1000
        self.timeStr =  str(self.hrs).zfill(2) + ":" + \
                        str(self.min).zfill(2) + ":" + \
                        str(self.sec).zfill(2) + "," + \
                        str(self.ms).zfill(3)
        self.timeNoMs = re.split(",",self.timeStr)[0]
        
def timeOffset(timeStr,offset):
    # This function accepts time string, calls the class to convert it to MS,
    # applies the provided offset, and returns a string based on that offset
    oldTime = timeClass(timeStr)
    #print(oldTime.timeStr)
    oldTime.msToStr(oldTime.totalMs + int(offset))
    print(oldTime.timeStr)
    newTime = oldTime.timeStr
    return(newTime)

def ClassTest():
    # TEST function to test the Class. Not used in main script
    currentTime = timeClass("00:12:34,234")
    print("Time is {hrs} hrs {min} mins {sec} secs and {ms} ms".format(
        hrs=currentTime.hrs,
        min=currentTime.min,
        sec=currentTime.sec,
        ms=currentTime.ms))
    print("Total ms is: %s" % currentTime.totalMs)
    print("Old time is %s" % currentTime.timeStr)
    currentTime.msToStr(currentTime.totalMs - 200)
    print("New time is %s " % currentTime.timeStr)


def PrintChar(line):
    # Test function for UTF testing. Not used in main script
    for char in list(line):
        #print(codecs.encode(str.encode(line),"hex"))
        print(str.encode(line))

def GetDeutsch(file,timeStr):
    # Go through the second file looking for a specific timecode, and 
    # return all text associated with that timecode
    lineNumber = 0
    relevantLine = 0
    thisOutput = ""
    for line in file:
        if (re.search(r"^%s" % timeStr,line)): #, re.UNICODE)):
            relevantLine = lineNumber
            #print("YES! :: %s" % relevantLine)
            print("%s :: %s" % (timeStr,line))
            break
        lineNumber += 1
    
    i = 1
    if (relevantLine != 0):
        while (file[lineNumber + i] != ""):
            print(file[lineNumber + i])
            thisOutput += (file[lineNumber + i]) + "\n"
            i += 1
    return(thisOutput)
    
def MergeFiles(fileEng,fileDeu,subOffset):
    # Go through the first file, look up every single time code in the second 
    # file, merge text from both files for each individual time code
    # Second file timecode is looked up after calculating the offset
    patternNumber = re.compile("^([0-9])+", re.UNICODE) # match
    patternTime = re.compile("^([0-9])+:([0-9])+:([0-9])+,([0-9])+", re.UNICODE) # match
    patternShortTime = re.compile("^([0-9])+:([0-9])+:([0-9])+,([0-9])+", re.UNICODE)
    patternText = re.compile("([a-zA-Z])+", re.UNICODE) # search
    output = list()
    lastLine = "empty"
    lastTime = ""
    for line in fileEng:
        if lastLine == "empty":
            if (patternNumber.match(line)):
                output.append(line)
                lastLine = 'number'
                print(line)
        elif (lastLine == 'number'):
            if (patternTime.match(line)):
                output.append(line)
                lastTime = patternShortTime.match(line).group(0)
                lastLine = 'time'
            else:
                lastLine = "empty"
            print(line)
        elif (lastLine == 'time') or (lastLine == 'text'):
            if (patternText.search(line)):
                output.append(line)
                lastLine = 'text'
            else:
                timeCode = timeOffset(lastTime,subOffset).split(",")[0]
                output.append(
                    GetDeutsch(
                        fileDeu,timeCode
                    )
                )
                lastLine = 'empty'
            print(line)
        else:
            lastLine = "empty"
    return(output)

def MainExecutionBlock():
    # Main execution block
    fileNameEng = sys.argv[1]
    fileNameDeu = sys.argv[2]
    fileNameOut = sys.argv[3]
    subOffset   = sys.argv[4]
    #print(fileNameEng)
    #print(fileNameDeu)
    
    with codecs.open(fileNameEng,'r',encoding='utf-8') as file1PointerVar:
        contentEng = file1PointerVar.read()
    with codecs.open(fileNameDeu,'r',encoding='utf-16') as file2PointerVar:
        contentDeu = file2PointerVar.read()
    contentOut = MergeFiles(contentEng.splitlines(),contentDeu.splitlines(),subOffset)
    with open(fileNameOut,'w') as outFilePointerVar:
        outFilePointerVar.write('\n'.join(contentOut))



if __name__ == "__main__":
    MainExecutionBlock()
    #ClassTest()
