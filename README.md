# neogeo tools
Some neogeo tools (for testing purposes) - All information you can find here is "inspired" by the follwoing unvaluable resources:

* http://www.ajworld.net/neogeodev/
* https://wiki.neogeodev.org

As soon as I can I will add some information on "HOWTO" setup a proper development environment for the NeoGeo.

I generally use Linux to do my stuff, but I'll try to keep it as Windows compatible as possible.

## mame_hash.py

This file will insert the "ROM" into the mame hash file for easier excution of your code. It will look up the files in the cart (please respct naming convention of P,S,V,C,M roms) and add it to the mame hash file for neo geo so mame will execute the ROM easily.

_Parameters are_
* gameName : name of the game to compile and execute, required
* cartPath : path where the final builds will be stored (usually a MAME accesible ROM directory), required
* hashFile : Location of the MAME Hash file (neogeo.xml), required
* publisher: publisher of the game (usually you), optional

Needs Python to execute!

## Makefile

This file is an adaptation of the original makefile that can be found here http://www.ajworld.net/neogeodev/beginner/, it has only been tested in linux and requires install/build of the following tools:

* Vasm Assembler (http://sun.hasenbraten.de/vasm/)
* ROMWak (https://github.com/freem/romwak)

## convertfiles.py

Will convert from Neogeo format to image and viceversa, 3 parameters are needed:
<inFile> -> The file to read, it will look for the C or S pattern for (C=Sprites, S=Fixed Tiles), otherwise it will be treated as an image
<outFile> -> Same as outFile, with same pattern detection
<imageWidth> -> The desired width of the resulting image when exporting to an image
  
The image will have a 16 color grayscale, the rom files do not store palettes. In the same way, the resulting roms will be have an indexed palette from 0 to 15, meaning that if you have more than 16 colours they will be indexed to teh corresponding 0-15 range. Up to you to assign the proper palette in the code.
