# DownloadPictures.py
# Downloads pictures from a formatted text file
# Each line in the input text file specifies a pano_id
# with an associated google street view image to download

import requests

def downloadPics(inLines, params):
    fPathOut = input("Input file path to the output folder: ")
    baseURL = "https://maps.googleapis.com/maps/api/streetview"
    headings = ["0", "90", "180", "270"]
    for pan in inLines:
        for heading in headings:
            params["heading"] = heading
            params["pano"] = pan
            print(heading)
            print(pan)
            r = requests.get(baseURL, params=params)
            with open(fPathOut+"/"+pan+"_"+heading+".png", "w+b") as oFile:
                oFile.write(r.content)

def main():
    fPath = input("Input file path to source file (include 'fName.txt'): ")
    key = input("Input API key with billing enabled: ")
    inLines = []
    params = {"pano" : None, "key" : key, "pitch" : "25",
              "heading" : None, "fov" : "120", "size" : "640x640"}
    #expects a text file with all pano_id's separated by a newline
    #ONLY pano_id's should be present in input file
    with open(fPath) as inFile:
        inLines = inFile.read().split("\n")
    i = 1
    while True:
        if inLines[len(inLines) - i] == "":
            del inLines[len(inLines) - i]
            i += 1
        else:
            break
    print("NOTICE:")
    print("Expected Cost: " + str(len(inLines) * 4 / 1000 * 7) + " USD")
    print("Expected Mem: " + str(50 * 4 * len(inLines) / 1000000) + " GB")
    print("Expected Time: " + str(len(inLines) * 4 / 2 / 3600) + " hours")
    ans = input("Would you like to continue? ENTER = NO: ")
    if ans:
        downloadPics(inLines, params)
