# neogeo tools
Some neogeo tools (for testing purposes) - ALl information you can find here is "inspired" by the follwoing unvaluable resources:

* http://www.ajworld.net/neogeodev/
* https://wiki.neogeodev.org

As soon as I can I will add some information on "HOWTO" setup a proper development environment for the NeoGeo.

## mame_hash.py

This file will insert the "ROM" into the mame hash file for easier excution of your code. It will look up the files in the cart (please respct naming convention of P,S,V,C,M roms) and add it to the mame hash file for neo geo so mame will execute the ROM easily.

_Parameters are_
* gameName : name of the game to compile and execute, required
* cartPath : path where the final builds will be stored (usually a MAME accesible ROM directory), required
* hashFile : Location of the MAME Hash file (neogeo.xml), required
* publisher: publisher of the game (usually you), optional

## Makefile

This file is an adaptation of the original makefile that can be found here http://www.ajworld.net/neogeodev/beginner/, it has only been tested in linux and requires install/build of the following tools:

* Vasm Assembler (http://sun.hasenbraten.de/vasm/)
* ROMWak (https://github.com/freem/romwak)

