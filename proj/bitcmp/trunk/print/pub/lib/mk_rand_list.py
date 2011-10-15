"""
This code is used very irregularly to create lists of randomly
selected words which will be used to make unique URLs.  I prefer
words to randomly selected char for 'hashes' since I believe that
they would be easier to type in when the (possible) QR code is not
usable for whatever reason.

The script is not directly executable (#!) because I don't expect
it to be used much, and is also 'hidden' in the lib dir.

The script works by using aspell's dictionary list, and the results
are chunks of 100 hashes each as individual files in the 'var/raw/'
dir.  The idea is that as these lists are used to generate hand-outs,
the source file can be moved to something like 'var/{campaign}/'.
"""

import sys
import os
import re
import time
import math
import random
import subprocess

NR = 100000   # Number of Results desired.


def main():

    out_dir = os.path.normpath("%s/../var/raw" % 
        os.path.dirname(os.path.realpath(sys.argv[0])))

    ts = time.strftime("%Y%m%d%H%M")


    word_re = re.compile('^[a-z]{3,4}$')
    word_list_l = []
    word_list_r = []

    p = subprocess.Popen(["aspell","dump","master"], stdout = subprocess.PIPE)
    for word in p.stdout.readlines():
        sword = word.strip()
        #sys.stdout.write("-->%s<--\n" % sword)
        if word_re.match(sword):
            word_list_l.append(sword)
            word_list_r.append(sword)

    random.shuffle(word_list_l)
    random.shuffle(word_list_r)

        # Theory failed me here but emperical evidence seems
        #  to indicate that this gives me a close number of
        #  elements that we want from each set:

    si = int(math.ceil(NR/len(word_list_l))) + 2


    res = []
    for l in word_list_l:
        r_list = random.sample(word_list_r, si)
        for r in r_list:
            res.append("%s-%s" % (l,r))

        # Shuffle the output also...

    random.shuffle(res)

        # Write out the results in lists of 100 each
        #  in a 'raw' dir.  The idea being that these
        #  chunks can be moved from a raw dir to some
        #  named used dir as they are used to make
        #  hand-outs.

    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    rwl_num = 0
    eg_list = []
    for e in res:
        eg_list.append(e)
        if len(eg_list) >= 100:
            rwl_num = rwl_num + 1
            out_fp = os.path.normpath("%s/rand_wrd_list_100_%05d_%s.txt" %
                                     (out_dir,rwl_num,ts))
            out_fh = open(out_fp, 'w')
            for eg in eg_list:
                out_fh.write("%s\n" % eg)
            out_fh.close()
            eg_list = []


if __name__ == "__main__":
    main()
