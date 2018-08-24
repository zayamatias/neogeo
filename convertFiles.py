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
        print ("Missing arguments, please use:\nconvertFiles.py <inputfile> <outputfile> <image_width (default 1024) and divisible by 16px> \n")
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
    # Detect Infile Type
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
    # Detect Infile Type
    for filetype in filetypes:
        m = re.search(filetype[1], outFile)
        if m is not None:
            convert = filetype [0]
    if convert == "FIXED":
        convertToFixed (inFile,outFile)
        print ("Conversion done")
        sys.exit(0)
    if convert == "SPRITES":
        convertToSprites (inFile,outFile)
        print ("Conversion done")
        sys.exit(0)

    print ("Cannot seem to find the type of ROM you wish to use")
    sys.exit(1)

def convertToSprites(inFile,outFile):
    print ("Convert To Sprites")
    pe = re.compile ("[0-9]")
    m = pe.search(inFile)
    if (m is not None):
        searchFile = list(inFile)
        searchFile[m.span()[1]-1]="?"
        searchFile="".join(searchFile)
    else:
        searchFile = inFile
    foundFiles = glob.glob(searchFile)
    numFiles = int(len(foundFiles))
    cFileCount = 1
    pe = re.compile ("[_-][cC]")
    m = pe.search(outFile)
    for fileNum in range (numFiles):
        oddFileName = list(outFile)
        oddFileName[m.span()[1]]=str(cFileCount)
        oddFileName = "".join(oddFileName)
        cFileCount = cFileCount + 1
        evenFileName = list(outFile)
        evenFileName[m.span()[1]]=str(cFileCount)
        evenFileName = "".join(evenFileName)
        cFileCount = cFileCount + 1
        oddFile = open(oddFileName,'wb')
        evenFile = open(evenFileName,'wb')
        print ("reading "+foundFiles[fileNum]+" file")
        #I'm assuming correct order ... to be reviewed!! (TODO)
        img = PIL.Image.open(foundFiles[fileNum])
        img = img.convert('RGB')
        #Check if image has a MAX of 16 colours
        RGBColors = img.getcolors()
        #TODO allow for multiple palettes (references to basic colors eventually)
        colors = [0 for i in range (0,len(RGBColors))]
        idx=len((RGBColors))-1
        print (idx)
        #For some reason the colors are inverted in the palette....This need to be further checked: TODO
        for RGBColor in RGBColors:
            colors[idx]=RGBColor[1]
            idx = idx -1
        xsize = img.size[0]
        ysize = img.size[1]
        tileXsize = 16
        tilesPerRow = int(xsize / tileXsize)
        tileYsize = 16
        tilesPerCol = int(ysize/ tileYsize)
        tilesNum = int(tilesPerRow*tilesPerCol)
        for tile in range (tilesNum):
            oddBytes = bytearray(64)
            evenBytes = bytearray(64)
            sprite = []
            for row in range(tileYsize):
                sprRow = [0 for i in range (tileXsize)]
                for col in range(tileXsize):
                    colOff = int(tile%tilesPerRow)
                    rowOff = int(tile/tilesPerRow)
                    pxOff = colOff*tileXsize
                    pyOff = rowOff*tileYsize
                    px = pxOff+col
                    py = pyOff+row
                    pixel = img.getpixel((px,py))
                    colIdx = (colors.index (pixel)%16)
                    if colIdx > 15:
                        print ("the horror!!")
                    sprRow[col] = colIdx
                sprite.append(sprRow)
            for row in range(tileYsize):
                for vTile in range (2):
                    bitplane0 = 0
                    bitplane1 = 0
                    bitplane2 = 0
                    bitplane3 = 0
                    for col in range(int(tileXsize/2)):
                        bitplane = sprite[row][col+(vTile*8)]
                        bitplane0 = bitplane0 << 1
                        bitplane0=  bitplane0 | ((bitplane & 1))
                        bitplane1 = bitplane1 << 1
                        bitplane1=  bitplane1 | ((bitplane & 2)>>1)
                        bitplane2 = bitplane2 << 1
                        bitplane2=  bitplane2 | ((bitplane & 4)>>2)
                        bitplane3 = bitplane3 << 1
                        bitplane3=  bitplane3 | ((bitplane & 8)>>3)
                    destByte = calcDestSpriteByte(row,vTile)
                    oddBytes[destByte]=bitplane0
                    oddBytes[destByte+1]=bitplane1
                    evenBytes[destByte]=bitplane2
                    evenBytes[destByte+1]=bitplane3
            oddFile.write(oddBytes)
            evenFile.write(evenBytes)
        print ("Created "+oddFileName + " & "+evenFileName+" files")

def calcDestSpriteByte(row,vCol):
    destByte = 0
    if (vCol == 0 ):
        #We're in the 3rd or 4th Tile of the sprite
        byteOff= 32
    else:
        byteOff = 0
    row = row * 2 #2 bytes per half row per file
    destByte = row + byteOff
    return destByte



def convertToFixed(inFile,outFile):
    print ("Convert to Fixed")
    img = PIL.Image.open(inFile)
    img = img.convert('RGB')
    #Check if image has a MAX of 16 colours
    RGBColors = img.getcolors()
    if (len(RGBColors))>16:
        print ("Image has more than 16 colors, it cannot be converted\Remember that this conversion will use the palette index as index for the color in the resulting file.")
    colors = [0 for i in range (0,16)]
    idx=15
    #For some reason the colors are inverted in the palette....This need to be further checked: TODO
    for RGBColor in RGBColors:
        colors[idx]=RGBColor[1]
        idx = idx -1
    xsize = img.size[0]
    ysize = img.size[1]
    tileXsize = 8
    tilesPerRow = int(xsize / tileXsize)
    tileYsize = 8
    tilesPerCol = int(ysize/ tileYsize)
    tilesNum = int(tilesPerRow*tilesPerCol)
    byteFile = bytearray()
    byteIdx = [16,16,24,24,0,0,8,8]
    for tile in range (tilesNum):
        byteOutput = bytearray(32)
        for col in range(0,tileXsize,2):
            for row in range(tileYsize):
                colOff = int(tile%tilesPerRow)
                rowOff = int(tile/tilesPerRow)
                pxOff = colOff*tileXsize
                pyOff = rowOff*tileYsize
                px = pxOff+col
                py = pyOff+row
                pixelL = img.getpixel((px,py))
                px = pxOff+col+1
                pixelU = img.getpixel((px,py))
                pixelLIdx = colors.index (pixelL)
                pixelUIdx = colors.index (pixelU)
                byte = (pixelUIdx << 4) | pixelLIdx
                bytePos = byteIdx[col]+row
                byteOutput[bytePos]=byte
        byteFile = byteFile + byteOutput
    f = open(outFile,'wb')
    f.write(byteFile)
    f.close
    print ("Created "+outFile+" file")

def convertSprites(inFile,outFile,xsize):
    print ("Converting sprites to image")
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
        pe = re.compile ("\w\.")
        m = pe.search(outFile)
        if (m is not None):
            outImage = list(outFile)
            outImage.insert(m.span()[1]-1,str(outFileNum))
            outImage="".join(outImage)
        else:
            outImage = outFile
        AltWriteImage(outImage,xsize,ysize,tileXsize,tileYsize,tiles)
        outFileNum = outFileNum + 1

def convertFixed(inFile,outFile,xsize):
    print ("Converting fixe tiles to image")
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
    print ("created ",imgName," file.")
if __name__ == '__main__':
    main()
