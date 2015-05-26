# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.browser.view import DefaultView
from plone import api
from zope.event import notify
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from iol.gisweb.spezia.IolApp import IolApp
from iol.gisweb.spezia.IolPraticaWeb import IolWSPraticaWeb
from five import grok
from Products.CMFPlomino.interfaces import IPlominoDocument
from AccessControl import ClassSecurityInfo
from datetime import datetime
import random
import simplejson as json
import DateTime

try:
    from iol.gisweb.spezia.configlocal import WS_PRATICAWEB_URL
except:
    from iol.gisweb.spezia.config import WS_PRATICAWEB_URL

class inviaPW(object):

    def __init__(self,context,request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        url = "%s&test=%d" %(WS_PRATICAWEB_URL,random.randint(1,100000))
        wsDoc = IolWSPraticaWeb(doc,url)

        tipo_richiesta = doc.getItem('iol_tipo_richiesta','comunicazione')
        if tipo_richiesta == 'integrazione':
            res = wsDoc.invia_integrazione()
            res = dict(res)
            if res["success"]:
                iApp = IolApp(doc)
                r = iApp.inviaSmtpMail('protocollata_integrazione')
                wftool = getToolByName(doc, 'portal_workflow')
                try:
                    wftool.doActionFor(doc, 'i1_protocolla')
                except:
                    pass
                message = u"La richiesta di integrazione e' stata inviata correttamente al Servizio Edilizia"
                t = 'info'
            else:
                message = u"Si sono verificati alcuni errori durante l'invio della pratica"
                t = 'error'
        elif tipo_richiesta == 'inizio_lavori':
            res = wsDoc.aggiungi_inizio_lavori()
            res = dict(res)
            if res["success"]:
                iApp = IolApp(doc)
                r = iApp.inviaSmtpMail('protocollata_inizio_lavori')
                wftool = getToolByName(doc, 'portal_workflow')
                wftool.doActionFor(doc, 'i1_protocolla')
                message = u"La comunicazione di inizio lavori e' stata inviata correttamente al Servizio Edilizia"
                t = 'info'
            else:
                message = u"Si sono verificati alcuni errori durante l'invio della comunicazione"
                t = 'error'

        elif tipo_richiesta == 'fine_lavori':
            res = wsDoc.aggiungi_fine_lavori()
            res = dict(res)
            if res["success"]:
                iApp = IolApp(doc)
                r = iApp.inviaSmtpMail('protocollata_fine_lavori')
                wftool = getToolByName(doc, 'portal_workflow')
                wftool.doActionFor(doc, 'i1_protocolla')
                message = u"La comunicazione di fine lavori è stata inviata correttamente al Servizio Edilizia"
                t = 'info'
            else:
                message = u"Si sono verificati alcuni errori durante l'invio della comunicazione"
                t = 'error'

        else:
            res = wsDoc.aggiungi_pratica()
            res = dict(res)
            if res["success"]:
                iApp = IolApp(doc)
                r = iApp.inviaSmtpMail('protocollata')
                doc.setItem("numero_pratica",res["numero_pratica"])
                wftool = getToolByName(doc, 'portal_workflow')
                wftool.doActionFor(doc, 'i1_protocolla')
                message = u"La domanda è stata inviata correttamente al Servizio Edilizia con Numero di pratica %s" % res["numero_pratica"]
                t = 'info'
            else:
                message = u"Si sono verificati alcuni errori durante l'invio della pratica"
                t = 'error'
        api.portal.show_message(message=message, type=t, request=doc.REQUEST)
        port = api.portal.get()
        doc.REQUEST.RESPONSE.redirect(port['scrivania-protocolli'].absolute_url())
        #doc.REQUEST.RESPONSE.redirect(doc.absolute_url())

class inviaDomanda(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent
        tipo_richiesta = doc.getItem('iol_tipo_richiesta','comunicazione')
        if tipo_richiesta == 'inizio_lavori':
            iApp = IolApp(doc)
            res = iApp.inviaSmtpMail('invia_domanda_inizio')
        elif tipo_richiesta == 'fine_lavori':
            iApp = IolApp(doc)
            res = iApp.inviaSmtpMail('invia_domanda_fine')
        elif tipo_richiesta == 'integrazione':
            iApp = IolApp(doc)
            res = iApp.inviaSmtpMail('invia_domanda_integrazione') 
        else:
            iApp = IolApp(doc)
            res = iApp.inviaSmtpMail('invia_domanda')
        if res['success']==0:
            error = res["message"]
            api.portal.show_message(message=error, type="warning", request=doc.REQUEST)
        else:
            doc.setItem('data_presentazione',DateTime.DateTime())
            api.portal.show_message(message=u"Il messaggio è stato inviato correttamente", type="info", request=doc.REQUEST)

        api.content.transition(doc,'h1_presenta')
        api.portal.show_message(message=u"Il domanda è stata presentata correttamente", type="info", request=doc.REQUEST)
        doc.REQUEST.RESPONSE.redirect(doc.absolute_url())

# Returns Info about Wizard Workflow
class wfWizardInfo(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.state = api.content.get_state(obj=self.aq_parent)

    def __call__(self):
        doc = self.aq_parent
        aDoc = IolApp(doc)
        res = aDoc.getWizardInfo()
        #doc.REQUEST.RESPONSE.headers['Content-Type'] = 'application/json'
        return json.dumps(res)

class infoProcedimento(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request


    def __call__(self):
        doc = self.aq_parent
        url = "%s&test=%d" %(WS_PRATICAWEB_URL,random.randint(1,100000))
        wsDoc = IolWSPraticaWeb(doc,url)
        res = wsDoc.infoProcedimento()
        return json.dumps(res,default=DateTime.DateTime.ISO,use_decimal=True)


########## FIERE ##########################################
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

class stampaFattura(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        doc = self.aq_parent        
        iApp = IolApp(doc)
        return iApp.stampaFattura()


security = ClassSecurityInfo()
security.declarePublic('stampaElencoFattureFile')

class stampaElencoFattureFile(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
    
    def __call__(self,inizio,fine):                 
        db = self.aq_parent       
               
        inizio = int(self.request.get('inizio'))
        fine = int(self.request.get('fine'))        
        idx = db.getIndex()
        results = idx.dbsearch({'Form':'frm_posteggio','numero_fattura':{'query':[inizio,fine],'range':'min:max'}},sortindex='numero_fattura')

        campi = ['occupante_cognome','occupante_nome','occupante_indirizzo','occupante_cap','occupante_comune','occupante_cf','occupante_piva','','','numero_fattura','data_fattura','fattura_print','fiera_descrizione','quota_perc_iva_print','iva_print','imponibile_print','quota_esente_posta','','','','','','','','',''] 
                          
        header = '''COGNOME;NOME;INDIRIZZO;CAP;CITTA;CODICE_FIS;PARTITAIVA;MOD_PAG;RIF_PROVV;NUM_FATT;DATA_FATT;TOTALE_FAT;DESCRIZ;PERC_IVA_1;IMPORTO_IVA;IMPONIB_1;QUOTA_POSTALE;PERC_IVA_2;IMPOSTA_2;IMPONIB_2;PERC_IVA_3;IMPOSTA_3;IMPONIB_3;DATA_SCAD;CDR;SEZ_IVA'''
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
                    if doc.getItem(campo,"")!=None:    
                        if campo == 'data_fattura':
                            data_fattura = doc.getItem(campo) 
                            if data_fattura:
                                data_fat = data_fattura.strftime('%d/%m/%Y')  
                            else:
                                data_fat = ""                     
                         
                            row.append(data_fat)
                        else:
                            val = doc.getItem(campo,"")    
                            if isinstance(val,basestring):
                                row.append(val)
                            else: 
                                row.append(str(val))
                    else:
                        row.append("")      
                elif campo in itemsFiera:
                    if doc.getItem(campo,"")!=None:    
                        row.append("%s" %(doc.getItem(campo,"")))
                    else:
                        row.append("")   
                else:
                    row.append("")
            tot.append(row)

        st = '%s\n' %(header)   
        for i in tot:    
            st += '%s\n' %(';'.join(i))
        self.request.RESPONSE.headers['Content-type']='application/vnd.ms-excel' 
        self.request.RESPONSE.headers['Content-Disposition']='attachment;filename=elenco_fatture.csv'  
        return st
