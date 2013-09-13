#!/usr/bin/env python
# -*- Mode: Python; tab-width: 4 -*-
#
# Cyrus Imapd Skiplist db recovery tool
#
# Copyright (C) 2004-2006 Gianluigi Tiesi <sherpya@netfarm.it>
# Copyright (C) 2004-2006 NetFarm S.r.l.  [http://www.netfarm.it]
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTIBILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
# ======================================================================

__version__= '0.2'
__doc__="""Cyrus skiplist db recover"""

from sys import argv, stdout, stderr, exit as sys_exit
from struct import unpack
from time import localtime, strftime

### TODO: Correct handle COMMIT/DEL stuff
###       right now this tools rougly dumps entries in the skiplist file

### Enable debug mode
debug = 0
###

TIMEFMT ='%a, %d %b %Y %H:%M:%S %z'
MAGIC   = '\xa1\x02\x8b\x0d'
PADDING = '\xff\xff\xff\xff'
INORDER = 1
ADD     = 2
DELETE  = 4
COMMIT  = 255
DUMMY   = 257
HEADER  = -1
MAIN    = -2

types = {
    1:   'INORDER',
    2:   'ADD',
    4:   'DELETE',
    255: 'COMMIT',
    257: 'DUMMY',
    -1:  'HEADER',
    -2:  '*'
    }

def log(rtype, text):
    global debug
    if debug:
        out = '[%s] %s\n' % (types[rtype], text)
        stdout.write(out)
        stdout.flush()

def roundto4(value):
    if value % 4:
        return ((value / 4) + 1) * 4
    return value

def get_header(fp):
    magic = fp.read(4)
    if magic != MAGIC:
        log(HEADER, 'Magic signature mismatch')

    sign = fp.read(16)
    log(HEADER, sign[:-3])

    version = unpack('>I', fp.read(4))[0]
    version_minor = unpack('>I', fp.read(4))[0]

    log(HEADER, 'Version %d,%d' % (version, version_minor))

    maxlevel = unpack('>I', fp.read(4))[0]
    curlevel = unpack('>I', fp.read(4))[0]

    log(HEADER, 'Level %d/%d' % (curlevel, maxlevel))

    listsize = unpack('>I', fp.read(4))[0]
    log(HEADER, 'List size %d' % listsize)

    logstart = unpack('>I', fp.read(4))[0]
    log(HEADER, 'Offset %d' % logstart)

    lastrecovery = localtime(unpack('>I', fp.read(4))[0])
    lastrecovery = strftime(TIMEFMT, lastrecovery)

    log(HEADER, 'Last Recovery %s' % lastrecovery)

    return { 'version'    : [version, version_minor],
             'level'      : [curlevel, maxlevel],
             'listsize'   : listsize,
             'logstart'   : logstart,
             'lastrecover': lastrecovery
             }

def getkeys(fp):
    values = []
    keys = {}
    keystring = ''
    datastring = ''

    while 1:
        log(MAIN, '-' * 78)

        stype = fp.read(4)

        ### EOF
        if len(stype) != 4:
            break

        rtype = unpack('>I', stype)[0]
        if not types.has_key(rtype):
            log(MAIN, 'Invalid type %d' % rtype)
            continue

        log(rtype, 'Record type %s' % types[rtype])

        if rtype == DELETE:
            ptr = unpack('>I', fp.read(4))[0]
            log(rtype, 'DELETE %d (0x%x)' % (ptr, ptr))
            continue

        if rtype == COMMIT:
            continue

        ksize = unpack('>I', fp.read(4))[0]
        log(rtype, 'Key size %d (%d)' % (ksize, roundto4(ksize)))

        if ksize:
            keystring = fp.read(roundto4(ksize))[:ksize]
            log(rtype, 'Key String %s' % keystring)

        datasize = unpack('>I', fp.read(4))[0]
        log(rtype, 'Data size %d (%d)' % (datasize, roundto4(datasize)))

        if datasize:
            datastring = fp.read(roundto4(datasize))[:datasize]
            log(rtype, 'Data String %s' % datastring)

        n = 0
        while 1:
            str_p = fp.read(4)
            if str_p == PADDING:
                break
            spointer = unpack('>I', str_p)[0]
            n = n +1
            if spointer: log(rtype, 'Skip pointer %d' % spointer)

        log(rtype, 'Total Skip pointers: %d' % n)

        if rtype != DUMMY:
            if keystring not in values:
                values.append(keystring)
            keys[keystring] = datastring

    return values, keys

if __name__ == '__main__':
    if len(argv) != 2:
        print 'Usage: %s skiplist.file' % argv[0]
        sys_exit()

    fp = open(argv[1], 'rb')
    header = get_header(fp)
    values, keys = getkeys(fp)
    fp.close()

    if debug: sys_exit()
    for v in values:
        print '%s\t%s' % (v, keys[v])
