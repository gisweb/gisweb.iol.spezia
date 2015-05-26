# -*- coding: utf-8 -*-

import simplejson as json
import os

def convert(conv,obj):
    res = dict()
    keys = obj.keys()
    for item_old,item_new in conv.items():
        if item_old in keys:
            res[item_new] = obj[item_old]

    return res

def getConvData(json_file):
    fName = "%s/mapping/%s.json" %(os.path.dirname(os.path.abspath(__file__)),json_file)

    if os.path.isfile(fName):
        json_data=open(fName)
        try:
            data = json.load(json_data)
        except ValueError, e:
            data = str(e)
            json_data.close()
    else:
        return fName
        data = dict()
    return data


class conf(object):
    def __init__(self, entries):
        self.__dict__.update(entries)

class genericTable(object):
    def __init__(self,json_file,entries):
        data = getConvData(json_file)
        if not isinstance(entries,dict):
            data = dict()
        values = convert(data,entries)
        self.__dict__.update(values)




