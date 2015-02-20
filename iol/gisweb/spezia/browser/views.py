from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api
from zope.event import notify
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from iol.gisweb.spezia.IolApp import IolApp
from five import grok
from Products.CMFPlomino.interfaces import IPlominoDocument

# 
class clonaFiera(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self,anno='',fiera='',nuovo_anno=''):
        doc = self.aq_parent
        db = doc.getParentDatabase()
        idx = db.getIndex()      
        fiera = self.request.get('fiera')        
        anno = self.request.get('anno')        
        
               
        result = idx.dbsearch({'Form':'frm_fiera','fiera':fiera,'anno':int(anno)})
        
        if len(result)>0:
            nuovo_anno = self.request.get('nuovo_anno') 
            doc_old = result[0].getObject().getId()
                   
            iApp = IolApp(doc)
            doc_old = db.getDocument(doc_old)     
                      
            return iApp.clonaFiera(doc_old,anno,fiera,nuovo_anno)
        else:
            return 'vuoto'

class numerazione(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self,item_name='',query={}):
        doc = self.aq_parent
        item_name = self.request.get('item_name')
        query = self.request.get('query') or {}
        iApp = IolApp(doc)
        return iApp.numerazione(doc,item_name,query)

