# -*- coding: utf-8 -*-
"""
Created on Thu Aug  9 09:56:33 2018

@author: id087082
"""

import xml.etree.ElementTree as ET
import datetime
import glob, os,zlib
import hashlib

def sha1(file):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)  
            buf = afile.read(BLOCKSIZE)
            return(hasher.hexdigest())
def crc32(path):
    f = open(path,'rb')
    csum = None
    try:
        chunk = f.read(1024)
        if len(chunk)>0:
            csum = zlib.crc32(chunk)
            while True:
                chunk = f.read(1024)
                if len(chunk)>0:
                    csum = zlib.crc32(chunk, csum)
                else:
                    break
    finally:
        f.close()
    if csum is not None:
        csum = csum & 0xffffffff
    return csum
    
def main():
    gameName = "Test"
    hashFile = "C:\\Users\\id087082\\Downloads\\neogeo.xml"
    cartPath = "C:\\Users\\id087082\\Downloads\\cart\\"
    xmlFile = ET.parse(hashFile) 
    e = xmlFile.getroot()
    for atype in e.findall('software'):
        if atype.get('name') == gameName:
            e.remove (atype)
    newGame = ET.SubElement(xmlFile.getroot(), 'software')
    newGame.attrib['name']=gameName
    newGameDescription  = ET.SubElement(newGame,'description')
    newGameDescription.text = "Auto created for game "+gameName
    newGameYear = ET.SubElement(newGame,'year')
    newGameYear.text = str(datetime.datetime.now().year)
    newGameDescription  = ET.SubElement(newGame,'publisher')
    newGameDescription.text = "New Neo Geo Developper"
    newSharedFeat  = ET.SubElement(newGame,'sharedfeat')
    newSharedFeat.attrib['name'] = "release"
    newSharedFeat.attrib['value'] = "AES"
    newSharedFeat  = ET.SubElement(newGame,'sharedfeat')
    newSharedFeat.attrib['name'] = "compatibility"
    newSharedFeat.attrib['value'] = "AES"
    newPart  = ET.SubElement(newGame,'part')
    newPart.attrib['interface'] = "neo_cart"
    newPart.attrib['name'] = "cart"
    #Data Areas
    dataAreasDefinitions = [[["endianness","big"],["name","maincpu"],["size","_SIZE_"],["width","16"]],[["name","fixed"],["size","_SIZE_"]],[["name","audiocpu"],["size","_SIZE_"]],[["name","ymsnd"],["size","_SIZE_"]],[["name","sprites"],["size","_SIZE_"]]]
    extensions=[["maincpu","p",0],["fixed","s",0],["audiocpu","m",0],["ymsnd","v",0],["sprites","c",0]]
    os.chdir(cartPath)
    cartFiles = []
    for extension in extensions:
        cartFiles.append([extension[0],[]])
        # Check extensions first
        for file in glob.glob("*."+extension[1]+"??"):
            extension[2]=extension[2]+os.path.getsize(cartPath+file)
            cartFiles[len(cartFiles)-1][1].append(file)
        
        #check for .rom files then
        for file in glob.glob("*[_-]"+extension[1]+"*.rom"):
            extension[2]=extension[2]+os.path.getsize(cartPath+file)
            cartFiles[len(cartFiles)-1][1].append(file)
    
        #check for .rom files then
        for file in glob.glob("*[_-]"+extension[1]+"*.bin"):
            extension[2]=extension[2]+os.path.getsize(cartPath+file)
            cartFiles[len(cartFiles)-1][1].append(file)
    
    for dataAreaDefinition in dataAreasDefinitions:
        newDataArea = ET.SubElement(newPart,"dataarea")
        for element in dataAreaDefinition:
            newDataArea.attrib[element[0]]=element[1]
    #Update Sizes        
    for extension in extensions:
        for element in newPart.findall("dataarea"):
            if element.get("name") == extension[0]:
                element.set("size",str(hex(extension[2])))
    
    for element in newPart.findall("dataarea"):
        for fileList in cartFiles:
            if fileList[0]==element.get("name"):
                offset = 0
                sproffset = 0
                odd = True
                for file in fileList[1]:    
                    newRom = ET.SubElement(element,"rom")
                    newRom.attrib["name"]=file
                    fileSize = os.path.getsize(cartPath+file)
                    newRom.attrib["size"]=hex(fileSize)
                    newRom.attrib["offset"]=hex(offset)
                    if fileList[0]=="sprites":
                        if odd:
                            sproffset = sproffset + fileSize
                            offset = offset + 1
                            odd = not odd
                        else:
                            sproffset = sproffset + fileSize
                            offset = sproffset
                            odd = not odd
                        newRom.attrib["loadflag"]="load16_byte"
                    else:
                        offset = offset + fileSize
                    newRom.attrib["crc"]=hex(crc32(cartPath+file))
                    newRom.attrib["sha1"]=sha1(cartPath+file)
                    if fileList[0]=="maincpu":
                        newRom.attrib["loadflag"]="load16_word_swap"
    
    xmlFile.write(hashFile)
    
if __name__ == '__main__':
    main()    
