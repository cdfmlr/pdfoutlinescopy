#!python3

"""
pdfoutlinescopy.py

Copy outlines from one pdf to another pdf.

By: CDFMLR 2022-09-21
"""

USAGE = """Usage: pdfoutlinescopy <src> <dst> [offset]

       Copy outlines from one pdf (src) to another pdf (dst).

       src str: source pdf file
       dst str: destination pdf file
    offset int: offset (+/-) for page number in dst, default is 0
"""

import re
import sys
from pikepdf import Pdf, Outline, OutlineItem


def copy_outlines(src: Pdf, dst: Pdf, offset: int = 0):
    """copy outline from src to dst
    """
    outlines = []

    with src.open_outline() as s:
        for item in s.root:
            item_copy = copy_outline_item(item, offset)
            outlines.append(item_copy)

    with dst.open_outline() as d:
        d.root.extend(outlines)


def copy_outline_item(item: OutlineItem, offset: int = 0) -> OutlineItem:
    """deep copy OutlineItem, return the copy of item.
    """
    item_copy = OutlineItem(item.title, page_of_item(item, offset))

    for child in item.children:
        item_copy.children.append(copy_outline_item(child, offset))

    return item_copy


def page_of_item(item, offset: int = 0):
    """get page number of item, adding offset for the purposes.
    """
    # item.destination is a complex object.
    # And I can hardly get page number form it.
    #
    # but item.destination.__repr__() is something like:
    #   'pikepdf.Array([ <Pdf.pages.from_objgen(221,0)>, "/Fit" ])'
    # which points to page 221 - 1 = 220.
    page = re.search("^.*?(\d+).*?", item.destination.__repr__()).group(1)
    return int(page) + offset


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(USAGE)
        exit(-1)

    src = Pdf.open(sys.argv[1])
    dst = Pdf.open(sys.argv[2])

    offset = 0
    if len(sys.argv) > 3:
        offset = int(sys.argv[3])

    copy_outlines(src, dst, offset)

    save_path = sys.argv[2] + '.add_outline.pdf'
    dst.save(save_path)
    print(save_path)
