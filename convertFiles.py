import re
import PIL.Image
import os
import sys
import glob

#Ficticious palette, remember that no ROM holds the actual palette
palette = []
colcomp = 0
for colidx in range (0,16):
    color = (colcomp,colcomp,colcomp)
    colcomp = colcomp + 16
    palette.append(color)

def main():
    args=sys.argv
    if len(args)<=2 :
        print ("Missing arguments, please use:\nconvertFiles.py <inputfile> <outputfile> <image_width (default 1024) and divisible by 16px>\n")
        #sys.exit(1)
    inFile = args[1]
    outFile = args[2]
    try:
        fileWidth = int(args[3]) 
    except:
        fileWidth=1024
    #Detect what kind of file we're dealing with
    filetypes = [["FIXED","[a-zA-Z]*[_\-][sS][0-9].*"],["SPRITES","[a-zA-Z]*[_\-][cC][0-9].*"]]
    convert = ""
    for filetype in filetypes:
        m = re.search(filetype[1], inFile)
        if m is not None:
            convert = filetype [0]
    if convert == "FIXED":
        convertFixed (inFile,outFile,fileWidth)
        print ("Conversion done")
        sys.exit(0)
    if convert == "SPRITES":
        convertSprites (inFile,outFile,fileWidth)
        print ("Conversion done")
        sys.exit(0)
    else:
        print ("Cannot seem to find the type of ROM you wish to use")
        sys.exit(1)

def convertSprites(inFile,outFile,xsize):
    print ("I shall convert your sprites into an image!")
    ### Find all sprite files
    # First find where the sequence number is located
    pe = re.compile ("[_-][cC]")
    m = pe.search(inFile)
    searchFile = list(inFile)
    searchFile[m.span()[1]]="?"
    searchFile="".join(searchFile)
    numFiles = int(len(glob.glob(searchFile))/2)
    fileNum= 1
    outFileNum = 1
    for fileCount in range (numFiles):
        oddFileName = list(inFile)
        oddFileName[m.span()[1]]=str(fileNum)
        oddFileName = "".join(oddFileName)
        evenFileName = list(inFile)
        evenFileName[m.span()[1]]=str(fileNum+1)
        evenFileName = "".join(evenFileName)
        oddFile = open(oddFileName,'rb')
        evenFile = open(evenFileName,'rb')
        statinfo = os.stat(oddFileName)
        fileSize = statinfo.st_size
        tileXsize = 16
        tileYsize = 16
        ysize = int(int(fileSize/64)/int(xsize/tileXsize))*tileYsize #Each 1 bytes is 4 pixels!!
        tiles =[]
        tileQty = int((xsize/tileXsize)*(ysize/tileYsize))
        byteNum = 0
        oddBytes =  oddFile.read()
        evenBytes = evenFile.read()
        for sprites in range(0,int(fileSize/64)):
            tile = [[0 for i in range(tileYsize)] for i in range (tileXsize)]
            print (sprites,end="\r")
            for tileNum in range(4):
                for row in range(int(tileYsize/2)):
                    oddByte0 = oddBytes[byteNum]
                    oddByte1 = oddBytes[byteNum+1]
                    evenByte0 = evenBytes[byteNum]
                    evenByte1 = evenBytes[byteNum+1]
                    bitplane0 = list(format(oddByte0,'08b'))
                    bitplane1 = list(format(oddByte1,'08b'))
                    bitplane2 = list(format(evenByte0,'08b'))
                    bitplane3 = list(format(evenByte1,'08b'))
                    if tileNum == 0:
                        for col in range (8,16):
                            pixColor = (int(bitplane3[col-8])<<3) | (int(bitplane2[col-8])<<2) | (int(bitplane1[col-8])<<1) | (int(bitplane0[col-8])) 
                            tile[row][col] = pixColor
                    if tileNum == 1:
                        for col in range (8,16):
                            pixColor = (int(bitplane3[col-8])<<3) | (int(bitplane2[col-8])<<2) | (int(bitplane1[col-8])<<1) | (int(bitplane0[col-8])) 
                            tile[row+8][col] = pixColor
                    if tileNum == 2:
                        for col in range (0,8):
                            pixColor = (int(bitplane3[col])<<3) | (int(bitplane2[col])<<2) | (int(bitplane1[col])<<1) | (int(bitplane0[col])) 
                            tile[row][col] = pixColor
                    if tileNum == 3:
                        for col in range (0,8):
                            pixColor = (int(bitplane3[col])<<3) | (int(bitplane2[col])<<2) | (int(bitplane1[col])<<1) | (int(bitplane0[col])) 
                            tile[row+8][col] = pixColor 
                    byteNum = byteNum + 2
            tiles.append(tile)
        byteNum = 0
        fileNum = fileNum + 2
        outImage = outFile
        fileStrNum = str(outFileNum)+"."
        outImage = outImage.replace(".",fileStrNum)
        AltWriteImage(outImage,xsize,ysize,tileXsize,tileYsize,tiles)
        outFileNum = outFileNum + 1

def convertFixed(inFile,outFile,xsize):
    readFile = open(inFile,'rb')
    statinfo = os.stat(inFile)
    fileSize = statinfo.st_size

    ysize = int(fileSize / xsize)*2 #Each byte is 2 pixels!!

    tileXsize = 8
    tileYsize = 8
    tiles =[]
    tileQty = int((xsize/tileXsize)*(ysize/tileYsize))
    pixelPos = [4,6,0,2]
    fileBytes =  readFile.read()
    bytePos = 0
    for thisTile in range(tileQty):
        #Go to the start of the tile in the file
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
    AltWriteImage(outFile,xsize,ysize,tileXsize,tileYsize,tiles)

def WriteImage(imgName,xsize,ysize,tileXsize,tileYsize,tiles):
    #Save image
    img = PIL.Image.new('RGB',(xsize, ysize))
    pixels = img.load()
    tilesPerRow = int(xsize/tileXsize)
    print (len(tiles))
    for pixel in range(0,int(xsize*ysize)):
        imageRow = int(pixel/xsize)
        imageCol = int(pixel%xsize)
        tileRow = int(imageRow/tileYsize)
        tileCol = int(imageCol/tileXsize)
        tileNum = (tileRow*tilesPerRow)+tileCol
        rowNum = imageRow-(tileYsize*tileRow)
        colNum = imageCol-(tileXsize*tileCol)
        try:
            pixelToInsert = tiles[tileNum][rowNum][colNum]
        except:
            print (tileNum,rowNum,colNum,len(tiles))
            sys.exit(1)
        try:
            pixels[imageCol,imageRow]=palette[pixelToInsert]
        except:
            print (imageCol,imageRow,pixelToInsert)
            sys.exit(1)
    img.save(imgName)

def AltWriteImage(imgName,xsize,ysize,tileXsize,tileYsize,tiles):
    #Save image
    print (len(tiles))
    img = PIL.Image.new('RGB',(xsize, ysize))
    pixels = img.load()
    tilesPerRow = int(xsize/tileXsize)
    py = 0
    for tRow in range(int(ysize/tileYsize)):
        for row in range (tileYsize):
            px = 0
            for col in range (tilesPerRow):
                currTile = (tRow*tilesPerRow)+col
                for x in range (tileXsize):
                    try:
                        color = tiles[currTile][row][x]
                    except:
                        print ("1",tRow,tilesPerRow,currTile,row,x)
                        sys.exit(1)
                    try:
                        pixels[px,py]=palette[color]
                    except:
                        print ("2",px,py,color)
                        sys.exit(1)
                    px=px+1
            py=py+1
        tRow=tRow+1
    img.save(imgName)

if __name__ == '__main__':
    main()
