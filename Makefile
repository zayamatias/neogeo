# (GNU) Makefile for a simple Hello World program
# from "Neo-Geo Assembly Programming for the Absolute Beginner" by freem
# http://ajworld.net/neogeodev/beginner/
# Adaptations by @zayamatias
################################################################################
# tool binaries #
#################
# CP - copy tool

CP=cp
############################################
# TOOLS Definitions                        #
############################################


# TOOL_VASM68K - filename and/or path to vasm (m68k with mot syntax)
TOOL_VASM68K = ~/NeoGeoDev/Tools/vasmm68k_mot
# TOOL_VASMZ80 - filename and/or path to vasm (z80 with oldstyle syntax)
TOOL_VASMZ80 = ~/NeoGeoDev/Tools/vasmz80_oldstyle
# TOOL_MKISOFS - filename and/or path to mkisofs
TOOL_MKISOFS = mkisofs
# TOOL_CHDMAN - filename and/or path to chdman
TOOL_CHDMAN = chdman
# TOOL_ROMWAK - filename and/or path to romwak
TOOL_ROMWAK = ~/NeoGeoDev/Tools/romwak
# TOOL_NEOSPRCONV - filename and/or path to NeoSprConv
TOOL_NEOSPRCONV = ~/NeoGeoDev/Tools/neosprconv
# TOOL_EMULATOR
TOOL_EMULATOR = mame neogeo
# TOOL_MAME SETUP
TOOL_MAME_SETUP = python ~/NeoGeoDev/Tools/mame_hash.py

############################################
# Variables definitios                     #
############################################

#PUBLISHER (FOR MAME)
PUBLISHER = "@ZayaMatias"
GAME_NAME = HelloWorld

############################################
# File Locations                           #
############################################

#MAME HASH FILE
MAME_HASHFILE =/usr/share/games/mame/hash/neogeo.xml
# SOURCE_68K, SOURCE_Z80 - base paths for source code directories
SOURCE_68K = src_68k
SOURCE_Z80 = src_z80
# INPUT_68K - filename of main 68K code file
INPUT_68K = $(SOURCE_68K)/main.asm
# INPUT_Z80 - filename of main Z80 code file
INPUT_Z80 = $(SOURCE_Z80)/simple.asm
# INPUT_SPR - filename of Sprite tile data file (4BPP SMS/GG/WSC format)
INPUT_SPR = spr/HELLO.sms


# INPUT_FIX - filename of Fix layer tile data file
INPUT_FIX = fixed


##########################
# intermediate filenames #
##########################

# INTERMEDIATE_68K - Intermediate file for 68K code (cart only)
INTERMEDIATE_68K = out.p
# INTERMEDIATE_SPR_CART - Intermediate file for converting sprite data to cart format
INTERMEDIATE_SPR_CART = $(GAME_NAME).c0

################################################################################
# output paths and filenames #
##############################

# OUTPUT_CART, OUTPUT_CD - base output paths for cart and CD targets
BASE_PATH = ~/NeoGeoDev/Projects/
OUTPUT_CART = $(BASE_PATH)$(GAME_NAME)/_cart
OUTPUT_CD   = _cd
# OUTPUT_PRG_CART, OUTPUT_PRG_CD
OUTPUT_PRG_CART=$(OUTPUT_CART)/$(GAME_NAME)-p1.p1
OUTPUT_PRG_CD=$(OUTPUT_CD)/$(GAME_NAME).PRG
# OUTPUT_FIX_CART, OUPUT_FIX_CD - output paths for Fix file/S1 ROM.
OUTPUT_FIX_CART=$(OUTPUT_CART)/
OUTPUT_FIX_CD=$(OUTPUT_CD)/
# OUTPUT_Z80_CART, OUTPUT_Z80_CD - output paths for Z80 driver/M1 ROM.
OUTPUT_Z80_CART=$(OUTPUT_CART)/$(GAME_NAME)-m1.m1
OUTPUT_Z80_CD=$(OUTPUT_CD)/$(GAME_NAME).Z80
# OUTPUT_SPR_CART1, OUTPUT_SPR_CART2 - output paths for .c ROMs
OUTPUT_SPR_CART1=$(OUTPUT_CART)/$(GAME_NAME)-c1.c1
OUTPUT_SPR_CART2=$(OUTPUT_CART)/$(GAME_NAME)-c2.c2
# OUTPUT_SPR_CD - output path for SPR file
OUTPUT_SPR_CD=$(OUTPUT_CD)/$(GAME_NAME).SPR
# OUTPUT_PCM_CART, OUTPUT_PCM_CD - output path for PCM/.v ROMs
OUTPUT_PCM_CART=$(OUTPUT_CART)/$(GAME_NAME)-v1.v1
OUTPUT_PCM_CD=$(OUTPUT_CD)/$(GAME_NAME).PCM

########################
# CD layout and output #
########################
# FLAGS_MKISOFS - Flags for mkisofs
# Mode 1 ISO (-iso-level 1); pad to multiple of 32K (-pad); Omit version number (-N)
FLAGS_MKISOFS=-iso-level 1 -pad -N
# NGCD_IMAGENAME - output image/ISO name
NGCD_IMAGENAME=HelloTut
# NGCD_DISCLABEL - Disc label (8 characters maximum)
NGCD_DISCLABEL=HELLOTUT
# CDFILES - the list of files to include on the CD (used with mkisofs)
CDFILES = \
	$(OUTPUT_CD)/ABS.TXT \
	$(OUTPUT_CD)/BIB.TXT \
	$(OUTPUT_CD)/CPY.TXT \
	$(OUTPUT_CD)/IPL.TXT \
	$(OUTPUT_FIX_CD) \
	$(OUTPUT_PCM_CD) \
	$(OUTPUT_PRG_CD) \
	$(OUTPUT_SPR_CD) \
	$(OUTPUT_Z80_CD)
# OUTPUT_CDIMAGE - output path for .iso image
OUTPUT_CDIMAGE=$(NGCD_IMAGENAME).iso
# OUTPUT_CHDFILE - output path for .chd image
OUTPUT_CHDFILE=$(NGCD_IMAGENAME).chd

################
# CHD settings #
################
# CHDMAN_ACTION - action for chdman
CHDMAN_ACTION = createcd

################################################################################
# target flags #
################
# FLAGS_TARGET_* - Define flags used for building each target
FLAGS_TARGET_CART = TARGET_CART
FLAGS_TARGET_CD   = TARGET_CD

###########
# targets #
###########

# .PHONY determines what targets don't correspond to a real path/filename.
.PHONY: all clean distclean cart cd chd prg cdprg z80 cdz80 fix cdfix spr cdspr

#==============================================================================#
# all - build all targets (chd implies cd)
all: cart chd

#==============================================================================#
# clean - remove all output files
clean:
	$(RM) $(OUTPUT_CART)/*.*
# $(OUTPUT_PRG_CART) $(OUTPUT_FIX_CART) $(OUTPUT_Z80_CART) $(OUTPUT_SPR_CART1) $(OUTPUT_SPR_CART2)
#	$(RM) $(OUTPUT_PRG_CD) $(OUTPUT_FIX_CD) $(OUTPUT_Z80_CD) $(OUTPUT_SPR_CD)
#	$(RM) $(OUTPUT_CDIMAGE) $(OUTPUT_CHDFILE)

#==============================================================================#
# distclean - remove all files not needed in a packaged distribution
# this should KEEP:
# .Z80/.m1 files
# .SPR/.c* files

distclean:
	$(RM) $(OUTPUT_PRG_CART) $(OUTPUT_FIX_CART)
	$(RM) $(OUTPUT_PRG_CD) $(OUTPUT_FIX_CD)

#==============================================================================#
# cart - cartridge roms
cart: fix prg z80 spr setup_emu emu

#==============================================================================#
# cd - .iso file (for Neo-Geo CD)
cd: cdfix cdprg cdz80 cdspr
	$(TOOL_MKISOFS) $(FLAGS_MKISOFS) -o $(OUTPUT_CDIMAGE) -V "$(NGCD_DISCLABEL)" $(CDFILES)

#==============================================================================#
# chd - MAME .chd file (for testing Neo-Geo CD)
# -f : force
# -i : input filename
# -o : output filename
FLAGS_CHDMAN = -f -i $(OUTPUT_CDIMAGE) -o $(OUTPUT_CHDFILE)

chd: cd
	$(TOOL_CHDMAN) $(CHDMAN_ACTION) $(FLAGS_CHDMAN)

#==============================================================================#
# Shared flags for vasm 68K
#==============================================================================#
# FLAGS_VASM68K - Shared flags for vasm 68K
# -m68000 : compile for Motorola 68000 (and not anything higher)
# -devpac : devpac compatibility mode (used to disable optimizations)
# -Fbin   : set output format to binary

FLAGS_VASM68K = -m68000 -devpac -Fbin

#==============================================================================#
# prg - cartridge program rom

# PROG_SIZE_KB - Program size in kilobytes (used for padding)

PROG_SIZE_KB = 1024

# FLAGS_ROMWAK_PRG_BYTESWAP - Define ROMWak flags and parameters for byteswapping P1.
# /f: flip low/high bytes of a file
# input filename
# output filename

FLAGS_ROMWAK_PRG_BYTESWAP = /f $(INTERMEDIATE_68K) $(OUTPUT_PRG_CART)

# FLAGS_ROMWAK_PRG_PAD - Define ROMWak flags and parameters for padding P1.
# /p: padding
# input filename
# output filename
# Length to pad in Kilobytes
# Value to pad with (Typically 0x00 or 0xFF)

FLAGS_ROMWAK_PRG_PAD = /p $(OUTPUT_PRG_CART) $(OUTPUT_PRG_CART) $(PROG_SIZE_KB) 0

prg:
	$(TOOL_VASM68K) $(FLAGS_VASM68K) -D$(FLAGS_TARGET_CART) -o $(INTERMEDIATE_68K) $(INPUT_68K)
	$(TOOL_ROMWAK) $(FLAGS_ROMWAK_PRG_BYTESWAP)
	$(TOOL_ROMWAK) $(FLAGS_ROMWAK_PRG_PAD)
	$(RM) $(INTERMEDIATE_68K)

#==============================================================================#
# cdprg - cd program file

cdprg:
	$(TOOL_VASM68K) $(FLAGS_VASM68K) -D$(FLAGS_TARGET_CD) -o $(OUTPUT_PRG_CD) $(INPUT_68K)

#==============================================================================#
# Shared flags for vasm z80
#==============================================================================#
# FLAGS_VASMZ80 - Shared flags for vasm Z80
# -Fbin   : set output format to binary
# -nosym  : don't include symbols in output

FLAGS_VASMZ80 = -Fbin -nosym

#==============================================================================#
# z80 - cartridge m1 rom

# FLAGS_ROMWAK_Z80_PAD - Define ROMWak flags and parameters for padding M1.
# /p: padding
# input filename
# output filename
# Length to pad in Kilobytes (e.g. 1 is 1024KB/1MB)
# Value to pad with (Typically 0x00 or 0xFF)

FLAGS_ROMWAK_Z80_PAD = /p $(OUTPUT_Z80_CART) $(OUTPUT_Z80_CART) 64 0

z80:
	$(TOOL_VASMZ80) $(FLAGS_VASMZ80) -D$(FLAGS_TARGET_CART) -o $(OUTPUT_Z80_CART) $(INPUT_Z80)
	$(TOOL_ROMWAK) $(FLAGS_ROMWAK_Z80_PAD)

#==============================================================================#
# cdz80 - cd .z80 file

cdz80:
	$(TOOL_VASMZ80) $(FLAGS_VASMZ80) -D$(FLAGS_TARGET_CD) -o $(OUTPUT_Z80_CD) $(INPUT_Z80)

#==============================================================================#
# Fix Layer Data
#==============================================================================#
# fix - fix layer data

fix:
	$(CP) $(INPUT_FIX)/*.* $(OUTPUT_FIX_CART)

#==============================================================================#
# cdfix - cd fix layer data

cdfix:
	$(CP) $(INPUT_FIX) $(OUTPUT_FIX_CD)

#==============================================================================#
# Sprite Data
#==============================================================================#
# This method is different than my usual technique for a few reasons:
# 1) The hackiness that I need to generate the *.c# files via Make is too much
#    for any normal human to understand.
# 2) There's only going to be one set of sprite graphics anyways, so I can
#    afford to manually create the filenames.
#==============================================================================#
# spr - sprite data
# This one is annoying to handle. See point 2 above, though.

# FLAGS_ROMWAK_SPR - Define ROMWak flags and parameters for splitting SPR.
# /b : split by bytes
# input filename
# output filename 1
# output filename 2

FLAGS_ROMWAK_SPR = /b $(INTERMEDIATE_SPR_CART) $(OUTPUT_SPR_CART1) $(OUTPUT_SPR_CART2)

spr:

	$(TOOL_NEOSPRCONV) $(INPUT_SPR) $(INTERMEDIATE_SPR_CART)
	$(TOOL_ROMWAK) $(FLAGS_ROMWAK_SPR)
	$(RM) $(INTERMEDIATE_SPR_CART)

#==============================================================================#
# cdspr - cd sprite data
# This is the easier one to handle.

# FLAGS_ROMWAK_CDSPR - Define ROMWak flags and parameters for byteswapping SPR.
# /f: flip low/high bytes of a file
# input filename
# output filename

FLAGS_ROMWAK_CDSPR = /f $(OUTPUT_SPR_CD) $(OUTPUT_SPR_CD)

cdspr:
	$(TOOL_NEOSPRCONV) $(INPUT_SPR) $(OUTPUT_SPR_CD)
	$(TOOL_ROMWAK) $(FLAGS_ROMWAK_CDSPR)

## Update Mame File

setup_emu:
	$(TOOL_MAME_SETUP) --gameName $(GAME_NAME) --cartPath $(OUTPUT_CART)/ --hashFile $(MAME_HASHFILE) --publisher $(PUBLISHER)

## Run Emulator
emu:
	$(TOOL_EMULATOR) $(GAME_NAME) -debug
