from zope.interface import implements
from iol.gisweb.spezia.interfaces import IIolApp
from plone import api
from zope import component
from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import make_uuid
from DateTime import DateTime
import time
from zope.event import notify
from zope.component import getGlobalSiteManager
from Products.CMFPlomino.PlominoEvents import PlominoSaveEvent
from Products.CMFPlomino.PlominoUtils import json_loads
from iol.gisweb.utils.config import USER_CREDITABLE_FIELD,USER_UNIQUE_FIELD,IOL_APPS_FIELD,STATUS_FIELD,IOL_NUM_FIELD,APP_FIELD
from Products.CMFPlomino.PlominoUtils import Now
from iol.gisweb.spezia.IolApp import IolApp
import simplejson as json

class fiereApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass

    security.declarePublic('NuovoNumeroPratica')
    def NuovoNumeroPratica(self,obj):
        idx = obj.getParentDatabase().getIndex()        
        query = {'numero_fattura':{'query':0, 'range':'min'}}        
        brains = idx.dbsearch(query, sortindex='numero_fattura', reverse=1, only_allowed=False)
      
        if not brains:
            nuovoNumero = 1
        else:
            nuovoNumero = (brains[0].getObject().getItem('numero_fattura',0) or 0) +1

        return nuovoNumero

    

        

    security.declarePublic('cloneFiera')
    def clonaFiera(self,doc,anno,fiera,nuovo_anno):    
          
        
        db = doc.getParentDatabase()       
        idx = db.getIndex()
        parentId = doc.getId()                         
        result = idx.dbsearch({'Form':'frm_posteggio','parentDocument':parentId})       
        pdoc = db.plomino_documents
        new_docid = make_uuid() 
        t0 = time.clock()
        if len(result)>0:                
            
            doc_old_fiera = db.getDocument(parentId)
            # clona fiera
            doc_fiera_new = api.content.copy(source=doc_old_fiera, target=pdoc, id=new_docid)
            doc_fiera_new.setItem('anno',int(nuovo_anno))
            for ob in result[:10]:                         
                            
                doc_old = ob.getObject()            
                new_docid = make_uuid()                       
                doc = api.content.copy(source=doc_old, target=pdoc, id=new_docid)
                if nuovo_anno != '':
                    doc.setItem('anno',int(nuovo_anno)) 
                doc.setItem('parentDocument',doc_fiera_new.getId())           
                notify(PlominoSaveEvent(doc))
                t1 = time.clock() - t0
                print '%s %s nuova fiera %s' %(doc.getId(),t1,doc_fiera_new.getId())        
            return printed

    security.declarePublic('stampaFattura')
    def stampaFattura(self,obj):
        doc = obj
        db = doc.getParentDatabase()
        fieldName = "documento_fattura"
        grp = "fatture"
        iDoc = IolApp(doc)
        info = json.loads(iDoc.printModelli(db.getId(),field=fieldName,grp=grp))
        if not doc.getItem('numero_fattura'):
            numero = self.NuovoNumeroPratica(obj)
            doc.setItem('numero_fattura',numero)
        if not doc.getItem('data_fattura'):           
            doc.setItem('data_fattura',Now())
        doc.createDoc(model=info['modello_fiere_spezia.docx']['model'],field=fieldName,grp=grp,redirect_url=doc.absolute_url())
        doc.save()
