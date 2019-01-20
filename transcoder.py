#!/usr/bin/env python3
# -*- encoding:utf-8 -*-

__author__ = 'Adrian Wang'

import ffmpy
import os
import sys


# magic = 0x79706762
head_len = 10
par_head_len = 12
flv_header = b'\x46\x4C\x56\x01\x05\x00\x00\x00\x09\x00\x00\x00\x00'
flv_ext = '.flv'


def trans(filename):
    if not os.path.exists(filename):
        print('Invalid file ' + filename + ': not exists!')
        return 1
    size = os.path.getsize(filename)
    if size <= 10:
        print('Invalid file ' + filename + ': too small!')
        return 1
    f = open(filename, 'rb')
    if not validate_head(f):
        print('Invalid file ' + filename + ': unrecognized format!')
        return 1
    print('Start to transcode ' + filename + ', file size: ' + str(size))
    ret = do_trans(f, size, handle_name(filename))
    assert ret == 0
    return do_merge()


def handle_name(filename):
    names = filename.split('.')
    len_names = len(names)
    position = 0 if len_names < 2 else len_names - 2
    simple_name = names[position]
    assert len(simple_name) > 0, 'empty name'
    return simple_name


def do_merge():
    return


def do_trans(f, size, out_file):
    pos = seek_next(f, head_len, size)
    seg_cnt = 0

    def seg_name():
        return '{0:03d}'.format(seg_cnt + 1)

    out = open(out_file + seg_name() + flv_ext, 'wb')
    out.write(flv_header)
    while pos != 0:
        # TODO seg_cnt fixed length
        seg_len = seg_size(f, pos)
        f.seek(pos)
        # print('Segment ' + seg_name() + ' length ' + str(seg_len))
        out.write(f.read(seg_len))
        # print(str(seg_len) + ' bytes written.')
        mark = f.read(1)
        pos += seg_len
        if mark == b'':
            break
        elif mark == '0':
            out.close()
            print("writing another temp file")
            out = open(out_file + seg_name() + flv_ext, 'wb')
            out.write(flv_header)
            pos = seek_next(f, pos, size)
        # for next seg
        seg_cnt += 1
    out.close()
    f.close()
    return 0


def seg_size(f, offset):
    f.seek(offset)
    data = f.read(4)
    ssize = (data[1] << 16) | (data[2] << 8) | (data[3])
    return ssize + 15


def seek_next(f, offset, size):
    while offset + par_head_len < size:
        f.seek(offset)
        par_head = f.read(par_head_len)
        if not par_head[0] == 9 and not par_head[0] == chr(9): # TODO python2 compatible
            offset += 1
        elif par_head[1:4] == 0x0:
            offset += 4
        elif not par_head[4:11] == b'\x00\x00\x00\x00\x00\x00\x00':
            offset += 1
        elif par_head[11] == 0:
            offset += 1
        else:
            print('... found segment header at: ' + str(offset))
            return offset
    return 0


def validate_head(f):
    # print(f.read(head_len))
    f.seek(0)
    return f.read(head_len) == b'QIYI VIDEO'


def main():
    filename = 'tester-long.qsv'
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    # seek_next(open(filename, 'rb'), 7728, 4941647)
    trans(filename)


main()
