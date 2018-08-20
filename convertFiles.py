import re
import PIL.Image
import os
import sys

#Ficticious palette, remember that no ROM holds the actual palette
palette = []
colcomp = 0
for colidx in range (0,16):
    color = (colcomp,colcomp,colcomp)
    colcomp = colcomp + 16
    palette.append(color)

def main():
    args=str(sys.argv)
    print("argume,ts",args)
    inFile = "/home/matias/NeoGeoDev/Projects/OriginalHelloWorld/fixed/fixed_test_s1.rom"
#    inFile = "/home/matias/NeoGeoDev/Projects/OriginalHelloWorld/fixed/203-s1.bin"
    outFile = "/home/matias/NeoGeoDev/Projects/OriginalHelloWorld/fixed/fixed_test_s1.png"
#    outFile = "/home/matias/NeoGeoDev/Projects/OriginalHelloWorld/fixed/203-s1.png"
    #Detect what kind of file we're dealing with
    filetypes = [["FIXED","[a-zA-Z]*[_\-][sS][0-9].*"],["SPRITES","[a-zA-Z]*[_\-][cC][0-9].*"]]
    convert = ""
    for filetype in filetypes:
        m = re.search(filetype[1], inFile)
        if m is not None:
            convert = filetype [0]
    if convert == "FIXED":
        convertFixed (inFile,outFile)
    else:
        print ("for the moment it only supports Fixed Tiles ROMS")
        sys.exit(1)

def convertFixed(inFile,outFile):
    readFile = open(inFile,'rb')
    statinfo = os.stat(inFile)
    fileSize = statinfo.st_size

    xsize = 512
    ysize = int(fileSize / xsize)*2 #Each byte is 2 pixels!!

    tileXsize = 8
    tileYsize = 8
    img = PIL.Image.new('RGB',(xsize, ysize))
    pixels = img.load()
    tiles =[]
    tileQty = int((xsize/tileXsize)*(ysize/tileYsize))
    tileSizeInBytes = 32
    pixelPos = [4,6,0,2]
    fileBytes =  readFile.read()
    bytePos = 0
    for thisTile in range(tileQty):
        #Go to the start of the tile in the file
        #tilePos = thisTile * tileSizeInBytes
        #readFile.seek(tilePos,0)
        tile = [[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0]]
        for bytesToRead in range (0,4):
            for row in range (0,8):
                byte = fileBytes[bytePos]
                bytePos = bytePos + 1
                #read bytes according ot the sequence in pixelPos
                tile[row][pixelPos[bytesToRead]]=byte & 15
                tile[row][pixelPos[bytesToRead]+1]=byte >> 4
        tiles.append(tile)
    #Save image
    pixelCount = 0
    tilesPerRow = int(xsize/tileXsize)
    for pixel in range(0,int(xsize*ysize)):
        imageRow = int(pixel/xsize)
        imageCol = int(pixel%xsize)
        tileRow = int(imageRow/tileYsize)
        tileCol = int(imageCol/tileXsize)
        tileNum = (tileRow*tilesPerRow)+tileCol
        rowNum = imageRow-(tileYsize*tileRow)
        colNum = imageCol-(tileXsize*tileCol)
        pixelToInsert = tiles[tileNum][rowNum][colNum]
        try:
            pixels[imageCol,imageRow]=palette[pixelToInsert]
        except:
            print (imageCol,imageRow,pixelToInsert)
            sys.exit(1)
    img.save(outFile)

if __name__ == '__main__':
    main()
