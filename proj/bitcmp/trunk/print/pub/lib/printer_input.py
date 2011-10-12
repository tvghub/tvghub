"""
This class renders a yaml input file to obtain data necessary
for a run of cards.

The primary reason for breaking this out as a seperate class
is that going forward, may wish to use the same class to write
config files or be able to make programatic mods and so forth.
"""

import sys
import os
import re
import traceback
import exceptions  # remove for python3
import yaml



class PrinterRunConfGeneralFail(Exception):
    """General Failure of this system."""
    pass


class Printer_Run_Conf():

        # Most of the work is error checking and adjustment
        #  in this here initializer.

    def __init__(self,inp_ffp=None):

        if not inp_ffp:
            em = "No input file specified."
            raise PrinterRunConfGeneralFail("%s" % em)

        if not os.path.isfile(inp_ffp):
            em = "Not input file: %s" % inp_ffp
            raise PrinterRunConfGeneralFail("%s" % em)

        try:
            f = open(inp_ffp)
            idata = yaml.load(f)
            f.close()
        except:
            em = "Could not parse conf file."
            traceback.print_exc()
            raise PrinterRunConfGeneralFail("%s" % em)

            # We'll do a fair job of interpreting 'None' in the
            #  config file rather than try to document it...

        none_re = re.compile('^\s*none\s*',re.IGNORECASE)
            
        if none_re.match(idata['base_card']):
            idata['base_card'] = None

        if none_re.match(idata['run_name']):
            idata['run_name'] = None
    
        if not idata['run_name']:
            rn_re = re.compile('^([\w_-]+)\..*$')
            rnm = rn_re.match(os.path.basename(sys.argv[1]))
            if not rnm:
                em = "ERROR:  I want an input file name\n"
                em = em + " with no spaces and one dot.\n"
                em = em + " Failing that, use 'run_name' in the config file."
                raise PrinterRunConfGeneralFail("%s\n" % em)
    
            idata['run_name'] = rnm.group(1)

            # The most critical aspect of this thing...

        self.idata = idata


        # Mostly will just use this at the expense of some
        #  potentially confusing syntax in the caller.

    def give_idata(self):
        return(self.idata)

        
