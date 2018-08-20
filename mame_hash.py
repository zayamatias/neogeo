
import xml.etree.ElementTree as ET
import datetime
import glob, os,zlib
import sha
import argparse


# SHA1 routine, "stolen" somewhere in the internet
'''def sha1(file):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
            return(hasher.hexdigest())
'''
def sha1(file):
    z = open(file, 'rb')
    sha1 = sha.new(z.read()).hexdigest()
    return (sha1)



# CRC32 - Also "stolen" somewhere in the internet
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
    return (format(csum,'x'))

def main():
    #Initial parameters, Can (and should) be overwritten via command line arguments
    gameName = "Test"
    hashFile = "C:\\Users\\id087082\\Downloads\\neogeo.xml"
    cartPath = "C:\\Users\\id087082\\Downloads\\cart\\"
    publisher = "@ZayaMatias"
    parser = argparse.ArgumentParser(description='Update MAME neogeo hash file')
    parser.add_argument('--gameName', help='name of the game to compile and execute', required=True)
    parser.add_argument('--cartPath', help='path where the final buils will be stored (usually a MAME ROM directory)', required=True)
    parser.add_argument('--hashFile', help='Location of the MAME Hash file', required=True)
    parser.add_argument('--publisher', help='publisher of the game (usually you)')
    args = vars(parser.parse_args())
    gameName=args["gameName"]
    cartPath=args["cartPath"]
    hashFile=args["hashFile"]
    if args["publisher"] != None:
        publisher=args["publisher"]
    else:
        publisher= "Unknown"
    print ("Updating Hash File "+hashFile)
    # XML File
    xmlFile = ET.parse(hashFile)
    e = xmlFile.getroot()
    #Go through all the "software" tags
    for atype in e.findall('software'):
        #If it is exsiting, just delete it
        if atype.get('name') == gameName:
            e.remove (atype)
    #Create new tag "software"
    newGame = ET.SubElement(xmlFile.getroot(), 'software')
    #Name as defined in the config... This should also be the game to execute in MAME
    newGame.attrib['name']=gameName
    #Description of the game
    newGameDescription  = ET.SubElement(newGame,'description')
    newGameDescription.text = "Auto created for game "+gameName
    #Year of creation (current year)
    newGameYear = ET.SubElement(newGame,'year')
    newGameYear.text = str(datetime.datetime.now().year)
    #Publisher
    newGameDescription  = ET.SubElement(newGame,'publisher')
    newGameDescription.text = publisher
    #Not sure what these tags are for
    newSharedFeat  = ET.SubElement(newGame,'sharedfeat')
    newSharedFeat.attrib['name'] = "release"
    newSharedFeat.attrib['value'] = "AES"
    newSharedFeat  = ET.SubElement(newGame,'sharedfeat')
    newSharedFeat.attrib['name'] = "compatibility"
    newSharedFeat.attrib['value'] = "AES"
    #Define this as a neo-geo cart, maybe later also for CD's
    newPart  = ET.SubElement(newGame,'part')
    newPart.attrib['interface'] = "neo_cart"
    newPart.attrib['name'] = "cart"
    #Data Areas, defined here all the data areas that are present in the XML, with the different attributes
    dataAreasDefinitions = [[["endianness","big"],["name","maincpu"],["size","_SIZE_"],["width","16"]],[["name","fixed"],["size","_SIZE_"]],[["name","audiocpu"],["size","_SIZE_"]],[["name","ymsnd"],["size","_SIZE_"]],[["name","sprites"],["size","_SIZE_"]]]
    extensions=[["maincpu","p",0],["fixed","s",0],["audiocpu","m",0],["ymsnd","v",0],["sprites","c",0]]
    os.chdir(cartPath+"/")
    cartFiles = []
    # go through all filetypes and get present files and their sizes (first to sum all)
    for extension in extensions:
        cartFiles.append([extension[0],[]])
        # Check extensions first
        patterns = ["*.["+extension[1]+"]*","*[_-]"+extension[1]+"*.rom","*[_-]"+extension[1]+"*.bin"]
        for pattern in patterns:
            for file in glob.glob(pattern):
                extension[2]=extension[2]+os.path.getsize(cartPath+file)
                cartFiles[len(cartFiles)-1][1].append(file)

    #Create dataarea tags
    for dataAreaDefinition in dataAreasDefinitions:
        newDataArea = ET.SubElement(newPart,"dataarea")
        for element in dataAreaDefinition:
            newDataArea.attrib[element[0]]=element[1]
    #Update Sizes
    for extension in extensions:
        for element in newPart.findall("dataarea"):
            if element.get("name") == extension[0]:
                element.set("size",str(hex(extension[2])))
    #Go through dataareas and include roms
    for element in newPart.findall("dataarea"):
        for fileList in cartFiles:
            if fileList[0]==element.get("name"):
                offset = 0
                sproffset = 0
                odd = True
                for file in fileList[1]:
                    #create each rom element
                    newRom = ET.SubElement(element,"rom")
                    newRom.attrib["name"]=file
                    fileSize = os.path.getsize(cartPath+file)
                    newRom.attrib["size"]=hex(fileSize)
                    newRom.attrib["offset"]=hex(offset)
                    #Sprites are a special case
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
                    # Create CRC and SHA
                    newRom.attrib["crc"]=crc32(cartPath+file)
                    newRom.attrib["sha1"]=sha1(cartPath+file)
                    if fileList[0]=="maincpu":
                        #This is due to the endian formatting
                        newRom.attrib["loadflag"]="load16_word_swap"
    #Update XML file
    xmlFile.write(hashFile)
    print ("Hash File "+hashFile+ "updated succesfully ")

if __name__ == '__main__':
    main()
