# -*- coding: utf-8 -*-
import os
from zope.interface import implements

from iol.gisweb.spezia.interfaces import IIolApp

from AccessControl import ClassSecurityInfo
import simplejson as json

from DateTime import DateTime

from base64 import b64encode

from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD
from iol.gisweb.utils.IolDocument import IolDocument
from iol.gisweb.utils import loadJsonFile,dateEncoder
from iol.gisweb.spezia.IolApp import IolApp

class autorizzazioneSuapApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        self.file = 'autorizzazioneSuap'
        self.path = os.path.dirname(os.path.abspath(__file__))

    #Returns new number    
    security.declarePublic('numerazione')
    def NuovoNumeroPratica(self,obj):                               
        db = obj.getParentDatabase()
        massimo = db.resources.numerazione()
        return massimo + 1