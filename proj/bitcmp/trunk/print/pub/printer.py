#!/usr/bin/env python
# Developed under python 2.6
#
# Licensed under the MIT license:
#   http://www.opensource.org/licenses/mit-license.php

import sys
import os
import re
import copy

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageOps


printer_base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.append("%s/lib" % printer_base_dir)
#from PyQRNative import *
import PyQRNative
from printer_input import Printer_Run_Conf

    # Not using a real getop here.

if not len(sys.argv) == 2:
    sys.stderr.write("ERROR: Arg $1 should be a valid input file.\n")
    sys.exit(2)

P_OUT   = True    # Produce some bordom killing OUTput.
DO_TICS = False   # Optional mostly to see in the code.

#CSIZE  = [1088,638]  # [w,h]
CSIZE  = [1020,585]   # [w,h]
QRSIZE = [400,400]    # [w,h]
#WMARG  = 450         # width margin
#HMARG  = 300         # height margin
WMARGL  = 80         # width margin
WMARGR  = 80         # width margin
HMARGT  = 110         # height margin
HMARGB  = 110         # height margin
GAP     = 5           # gap - try to make it zero or odd
QR_X    = 590         # relative to card
QR_Y    = 30          # relative to card

csize         = CSIZE       # [w,h]
qrsize        = QRSIZE      # [w,h]
qr_placement  = (QR_X, QR_Y)
txt_placement = (170,485) 

class PrinterRunGeneralFail(Exception):
    """General Failure of this system."""
    pass


def make_qr(text=None):
    """Input text, output QR object (not image.)"""

        # the first arg is some sort of QR quality param or something.
        #  Seems to work fine at this (lowish) setting in all my tests.
        #  See lib and/or web site for more details obviously.

    qr = PyQRNative.QRCode(5, PyQRNative.QRErrorCorrectLevel.L)
    qr.addData(text)
    qr.make()

    return(qr)


def make_txt_img(text=None,fp=None):
    """Input text, output text image"""

    fnt = ImageFont.truetype(fp,50)  # second param is point size.

    #txt=Image.new('L', (1000,100))   # second param is size of text container image
    txt=Image.new('L', (1000,60))   # second param is size of text container image
    d = ImageDraw.Draw(txt)
    d.text( (0, 0), text,  font=fnt, fill=255)
    w = txt.rotate(0,0, expand=1)    # Only because my code example had this :)

    return(w)


    # I want a brand new base card every time, but copy does not work.
    #  Color hard coded for now as a light pinkish.

def blank_card(base_card=None,csize=None,color=(255,230,255,255)):

    if base_card:
        base_card_image = Image.open('%s/media/%s' % (printer_base_dir,base_card))
        base_card_image = base_card_image.resize((csize[0],csize[1]), Image.ANTIALIAS)
    else:
        base_card_image = Image.new('RGBA', (csize[0],csize[1]), color)

    return(base_card_image)


def main():

        # data object for run

    ino = Printer_Run_Conf(inp_ffp=sys.argv[1])

        # Easier to work with the list of hash items.

    hdat = ino.give_idata()['hdat']
    hdat.reverse()

    url = ino.give_idata()['url_dom']
    camp = ino.give_idata()['campaign']

    fp = ino.give_idata()['font_path']


        # compute the sheet canvas size

    sheet_w = WMARGL + WMARGR + csize[0] * 2 + GAP
    sheet_h = HMARGT + HMARGB + csize[1] * 5 + GAP * 4
    sheet_size = (sheet_w, sheet_h)


        # correction from when taken from config file
        # TODO - move this crap to conf object...s-why I created it!

    base_card = ino.give_idata()['base_card']

    run_name = ino.give_idata()['run_name']

        # Make a list of spacing coords
        # Also develop the tic-marks (a bulk of the code here.)
        # Rem: csize = card_size [w,h]

    if P_OUT:
        sys.stdout.write("Computing run lists...\n")

    coord_list = []
    line_list = []
    hmarg = HMARGT
    for h in range(5):
        if DO_TICS:
                # left then right tics (horizontal lines)
            line_list.append([0, h * csize[1] + h * GAP + int(GAP/2) + hmarg,
                             75, h * csize[1] + h * GAP + int(GAP/2) + hmarg])
            line_list.append([sheet_size[0] - 75, h * csize[1] + h * GAP + int(GAP/2) + hmarg,
                              sheet_size[0],      h * csize[1] + h * GAP + int(GAP/2) + hmarg])
        for w in range(2):
            if DO_TICS:
                    # top then bottom tics (vertical lines)
                line_list.append([WMARGL + w * csize[0] + w * GAP + int(GAP/2),0,
                                  WMARGL + w * csize[0] + w * GAP + int(GAP/2),75]) 
                line_list.append([WMARGL + w * csize[0] + w * GAP + int(GAP/2),sheet_size[1],
                                  WMARGL + w * csize[0] + w * GAP + int(GAP/2),sheet_size[1] - 75]) 

                # Coordinates for cards (the actual necessary part.)

            coord_list.append((w * csize[0] + WMARGL + GAP * w,
                               h * csize[1] + hmarg  + GAP * h))
            hmarge = 0     # Use it only once.

        # Now add the right and bottom ticks (assume w and h end loop values.)
    if DO_TICS:
    
        line_list.append([0, (h + 1) * csize[1] + h * GAP + int(GAP/2) + HMARGT,
                         75, (h + 1) * csize[1] + h * GAP + int(GAP/2) + HMARGT])
        line_list.append([sheet_size[0] - 75, (h + 1) * csize[1] + h * GAP + int(GAP/2) + HMARGT,
                          sheet_size[0], (h + 1) * csize[1] + h * GAP + int(GAP/2) + HMARGT])
    
        line_list.append([WMARGL + (w + 1) * csize[0] + w * GAP + int(GAP/2),0,
                          WMARGL + (w + 1) * csize[0] + w * GAP + int(GAP/2),75]) 
        line_list.append([WMARGL + (w + 1) * csize[0] + w * GAP + int(GAP/2),sheet_size[1],
                          WMARGL + (w + 1) * csize[0] + w * GAP + int(GAP/2),sheet_size[1] - 75]) 


        # We compute the limit (hard coded to 10 sheets)
        #  then loop to do each sheet

    if P_OUT:
        sys.stdout.write("Looping over sheets...\n")

    lim_sheets = min(10,int(ino.give_idata()['soft_lim_sheets']))
    sheet_num = 0
    start_card = 0
    while sheet_num <= lim_sheets - 1 and len(hdat) > 0:
        start_card = int(sheet_num * start_card + 1)
        sheet_num = sheet_num + 1

            # Create sheet and draw on tick marks...

        sheet_img = Image.new('RGB', (sheet_size[0],sheet_size[1]),
                                            (255, 255, 255, 255))
        if DO_TICS:
            draw = ImageDraw.Draw(sheet_img)
            for lin in line_list:        
                draw.line((lin[0], lin[1], lin[2], lin[3]), fill=100)
            del draw


            # Pop a list of ten items.

        page_hdat_list = []
        while len(page_hdat_list) <= 9 and len(hdat):
            page_hdat_list.append(hdat.pop())

            # Now we loop through each element in the list
            #  of 10 items (or fewer) making a QR for each.
            #  and also text images.

        qr_list  = []
        txt_list = []
        for ha in page_hdat_list:

            text = "%s/%s/%s" % (url,camp,ha)

            qr_list.append(make_qr(text=text))
            txt_list.append(make_txt_img(text=text,fp=fp))


            # Now index loop implanting various images in other images...

        end_card = start_card + len(page_hdat_list) - 1
        for ind in range(len(page_hdat_list)):
            
            if P_OUT:
                sys.stdout.write("%s " % (ind + 1))

                # Obtain a new card image as a call to a function since
                #  deepcopy() does not seem to work here.

            card_img = blank_card(base_card=base_card,csize=csize)

                # Turn QR object into an image and insert it
                #  into the card image.

            qr_img = qr_list[ind].makeImage()
            qr_img = qr_img.resize((qrsize[0],qrsize[1]), Image.BICUBIC) # TODO - research.
            card_img.paste(qr_img, (qr_placement))

                # Obtain a text image and place that on the card
            
            #card_img.paste(txt_list[ind],txt_placement)
            card_img.paste(ImageOps.colorize(txt_list[ind], (0,0,0),(0,0,0)),txt_placement, txt_list[ind])

                # Paste the card image on the sheet using the
                #  properly indexed coordinates.

            sheet_img.paste(card_img,coord_list[ind])

            # Save sheet

        pdf_fname = "%s_%s-%s.pdf" % (run_name, start_card, end_card)
        sheet_img.save("%s/output/%s" % (printer_base_dir,pdf_fname))
        start_card = end_card

        if P_OUT:
            sys.stdout.write("\n")

    sheet_img.show()

    sys.exit(0)


    # name/main thing...

if __name__ == "__main__":
    main()

