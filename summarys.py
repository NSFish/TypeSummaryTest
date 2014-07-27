#!/usr/bin/python

def Rectangle_summary (valobj,internal_dict):
    height_val = valobj.GetChildMemberWithName('_height')
    width_val = valobj.GetChildMemberWithName('_width')
    height = height_val.GetValueAsUnsigned(0)
    width = width_val.GetValueAsUnsigned(0)
    area = height*width
    return 'Area: ' + str(area)