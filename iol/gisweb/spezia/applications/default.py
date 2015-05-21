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

class defaultApp(object):
    implements(IIolApp)
    security = ClassSecurityInfo()
    def __init__(self):
        pass
    def __call__(self, *args, **kwargs):
        pass

    

    security.declarePublic('NuovoNumeroPratica')
    def NuovoNumeroPratica(self,obj):        
        idx = obj.getParentDatabase().getIndex()
        query = dict(IOL_NUM_FIELD = dict(query=0, range='min'))
        brains = idx.dbsearch(query, sortindex=IOL_NUM_FIELD, reverse=1, only_allowed=False)
        if not brains:
            nuovoNumero = 1
        else:
            nuovoNumero = (brains[0].getObject().getItem(IOL_NUM_FIELD,0) or 0) +1

        return nuovoNumero

    security.declarePublic('numerazione')
    def numerazione(self,doc,item_name,query):
        if isinstance(query, basestring):
            query = json_loads(query)
        query.update({item_name: dict(query=0, range='min')})
        import pdb; pdb.set_trace()        
        db = doc.getParentDatabase()
        res = db.getIndex().dbsearch(query, sortindex=item_name, reverse=1, only_allowed=False)
        massimo = max([0]+[getattr(i, item_name) for i in res])
        return massimo + 1
    
    security.declarePublic('stampaElencoFattureFile')
    def stampaElencoFattureFile(self,obj,inizio='',fine=''):
        inizio = int(obj.REQUEST.get('inizio'))
        fine = int(obj.REQUEST.get('fine'))
        db = obj.getParentDatabase()
        idx = db.getIndex()
        results = idx.dbsearch({'Form':'frm_posteggio','numero_fattura':{'query':[inizio,fine],'range':'min:max'}})

        campi= ['occupante_cognome','occupante_nome','occupante_indirizzo','occupante_cap','occupante_comune','occupante_cf','occupante_piva','','','numero_fattura','data_fattura ','fattura','fiera_descrizione','quota_perc_iva','','imponibile','','','','','','','','','','']
                          
        header = '''COGNOME;NOME;INDIRIZZO;CAP;CITTA;CODICE_FIS;PARTITAIVA;MOD_PAG;RIF_PROVV;NUM_FATT;DATA_FATT;TOTALE_FAT;
        DESCRIZ;PERC_IVA_1;IMPOSTA_1;IMPONIB_1;PERC_IVA_2;IMPOSTA_2;IMPONIB_2;PERC_IVA_3;IMPOSTA_3;IMPONIB_3;DATA_SCAD;CDR;SEZ_IVA'''
        tot=[]
        for res in results:
            ob = res.getObject()
            docId = ob.getId()
            doc = db.getDocument(docId)
            posteggio = db.getForm('frm_posteggio')
            fiera = db.getForm('frm_fiera')
            row = []
            for indx,campo in enumerate(campi):
                 itemsPosteggio = [i.getId() for i in posteggio.getFormFields(includesubforms=True)]
                 itemsFiera = [i.getId() for i in fiera.getFormFields(includesubforms=True)]
                 if campo in itemsPosteggio:
                     if doc.getItem(campo,'')!=None:    
                         row.append(str(doc.getItem(campo,'')))
                     else:
                         row.append('')      
                 elif campo in itemsFiera:
                     if doc.getItem(campo,'')!=None:    
                         row.append(str(doc.getItem(campo,'')))
                     else:
                         row.append('')   
                 else:
                     row.append('')
            tot.append(row)
        st = '%s\n\r' %(header) 
        for i in tot:    
            st += '%s\n\r' %(';'.join(i))
        doc.REQUEST.RESPONSE.headers['Content-type']='application/vnd.ms-excel' 
        doc.REQUEST.RESPONSE.headers['Content-Disposition']='attachment;filename=elenco_fatture.csv'  
        return st


            

#############################################################################
app = defaultApp()
gsm = component.getGlobalSiteManager()
gsm.registerUtility(app, IIolApp, 'default')