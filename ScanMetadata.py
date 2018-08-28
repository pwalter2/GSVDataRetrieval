# DownloadPics.py
# Downloads pictures from a formatted text file
# Each line in the input text file specifies a pano_id
# with an associated google street view image to download


import requests
import math
import datetime

class UserInput:
    def __init__(self):
        start = input('Input "Lat,Lng" of NW corner:').split(',')
        for elem in start[:]:
            start.append(float(elem))
            start.remove(elem)
        self.start = tuple(start)
        end = input('Input "Lat,Lng" of SE corner:').split(',')
        for elem in end[:]:
            end.append(float(elem))
            end.remove(elem)
        self.end = tuple(end)
        self.key = input('Input google API key:')
        print("Default increment is 0.00005")
        self.increment = float(input('Input coordinate increment:'))
        if self.increment == '':
            self.increment = 0.00005
        print("example pathname /Users/paulwalter/Desktop")
        self.fPath = input('Input file path for output location:')
    def numRequests(self):
        span1 = abs(self.start[0] - self.end[0])
        span2 = abs(self.end[1] - self.start[1])
        xReq = math.floor(span1 / self.increment) + 1
        yReq = math.floor(span2 / self.increment) + 1
        return xReq * yReq

class MetaInfo:
    error = 0
    noResult = 0
    counter = 0
    notGoogle = 0
    repeat = 0
    seenPanos = ""

#returns date difference in years
def dateDiff(r):
    d1 = datetime.date.today()
    d1 = d1.year + d1.month / 12
    d2 = float(r['date'][:4]) + float(r['date'][5:]) / 12
    return d1 - d2

def isGoodResponse(r, metaInfo):
    if r['status'] == 'ZERO_RESULTS':
        metaInfo.noResult += 1
        return False
    if r['status'] != 'OK':
        metaInfo.error += 1
        return False
    if r['pano_id'] + "," in metaInfo.seenPanos:
        metaInfo.repeat += 1
        return False
    metaInfo.seenPanos += r['pano_id'] + ","
    if r['copyright'] != '© Google, Inc.':
        metaInfo.notGoogle += 1
        return False
    return True

def finalReport(metaInfo, outFile):
    outFile.write("############################################\n")
    outFile.write("SCAN STATISTICS:\n")
    outFile.write("Number of Requests: " + str(metaInfo.counter) + "\n")
    outFile.write("error: " + str(metaInfo.error) + "\n")
    outFile.write("No Result: " + str(metaInfo.noResult) + "\n")
    outFile.write("Repeated: " + str(metaInfo.repeat) + "\n")
    outFile.write("Not Google: " + str(metaInfo.notGoogle) + "\n")
    outFile.write("Note: Filtration sequence is listed top to bottom...\n")
    outFile.write("############################################\n")

def scanGrid(outFile, inputFromUser):
    metaBaseUrl = "https://maps.googleapis.com/maps/api/streetview/metadata"
    latCoord = inputFromUser.start[0]
    lngCoord = inputFromUser.start[1]
    params = {'location': None, 'key': inputFromUser.key}
    metaInfo = MetaInfo();
    while latCoord >= inputFromUser.end[0]:
        while lngCoord <= inputFromUser.end[1]:
            params['location'] = str(latCoord) + "," + str(lngCoord)
            try:
                r = requests.get(metaBaseUrl, params=params).json()
            except Exception:
                outFile.write("WARNING: " + str(Exception) + "\n")
                outFile.write("Last Request Coords: " + params['location'] + "\n")
                finalReport(metaInfo, outFile)
                return
            metaInfo.counter += 1
            if isGoodResponse(r, metaInfo):
                outFile.write(r['pano_id'] + ",\n")
            lngCoord += inputFromUser.increment
        latCoord -= inputFromUser.increment
        lngCoord = inputFromUser.start[1]
    finalReport(metaInfo, outFile)

def main():
    inputFromUser = UserInput()
    print("HTTP Requests to make: " + str(inputFromUser.numRequests()))
    with open(inputFromUser.fPath + "/output.txt", "w+") as outFile:
        scanGrid(outFile, inputFromUser)
