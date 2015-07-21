# -*- coding: utf-8 -*-
from zope.interface import Interface, implements, Attribute
from zope.component import adapts
from plone import api
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from Products.CMFPlomino.interfaces import IPlominoDocument, IPlominoForm
from zope.component import getGlobalSiteManager
from iol.gisweb.utils import config
from iol.gisweb.utils.IolDocument import IolDocument
from gisweb.iol.permissions import IOL_READ_PERMISSION, IOL_EDIT_PERMISSION, IOL_REMOVE_PERMISSION
from zope.component import getUtility,queryUtility
from iol.gisweb.spezia.interfaces import IIolPraticaWeb
from suds.client import Client
from DateTime import DateTime
import simplejson as json

try:
    from iol.gisweb.spezia.configlocal import WS_PRATICAWEB_URL
except:
    from iol.gisweb.spezia.config import WS_PRATICAWEB_URL

class IolWSPraticaWeb(object):
    implements(IIolPraticaWeb)
    adapts(IPlominoForm,IPlominoDocument)
    security = ClassSecurityInfo()
    security.declareObjectPublic()

    def __init__(self,obj,service):
        self.document = obj
        self.service = WS_PRATICAWEB_URL
        self.tipo_app = self.document.getItem(config.APP_FIELD,config.APP_FIELD_DEFAULT_VALUE)
        self.client = Client(self.service)
   
    def aggiungi_inizio_lavori(self):
        client = self.client
        doc = self.document
        
        utils = queryUtility(IIolPraticaWeb, name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getComunicazioneInizioLavori' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        lavori = utils.getComunicazioneInizioLavori(self)

        utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getAllegati' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        allegati = utils.getAllegati(self)
        procedimento = client.service.trovaProcedimento(doc.getItem('numero_pratica'))
        result = dict(procedimento)
        if result['id'] != None:
            pratica = result['id'] 
            client.service.comunicazioneInizioLavori(pratica,lavori)

            # aggiunge allegati per ciascuna pratica        
            files_ok = files_err = 0
            for allegato in allegati:

                res = client.service.aggiungiAllegato(pratica,allegato)
                nfiles = len(allegato.files)
                res = dict(res)

            utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
            if not 'getEsecutori' in dir(utils):
                utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)
            soggetti = utils.getEsecutori(self)
            for s in soggetti:
                r = client.service.aggiungiSoggetto(pratica,s,1)

        return result

    def aggiungi_fine_lavori(self):
        client = self.client
        doc = self.document

        utils = queryUtility(IIolPraticaWeb, name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getComunicazioneFineLavori' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        lavori = utils.getComunicazioneFineLavori(self)

        utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getAllegati' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        allegati = utils.getAllegati(self)
        procedimento = client.service.trovaProcedimento(doc.getItem('numero_pratica'))
        result = dict(procedimento)
        if result['id'] != None:
            pratica = result['id']
            client.service.comunicazioneFineLavori(pratica,lavori)

            # aggiunge allegati per ciascuna pratica
            files_ok = files_err = 0
            for allegato in allegati:
                res = client.service.aggiungiAllegato(pratica,allegato)
                nfiles = len(allegato.files)
                res = dict(res)

        return result
 
    def aggiungi_pratica(self):
        client = self.client
        doc = self.document

        utils = queryUtility(IIolPraticaWeb, name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getProcedimento' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        pr = utils.getProcedimento(self)

        utils = queryUtility(IIolPraticaWeb, name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getSoggetti' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)
        soggetti = utils.getSoggetti(self)

        utils = queryUtility(IIolPraticaWeb, name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getIndirizzi' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        indirizzi = utils.getIndirizzi(self)
	indirizzi = indirizzi or list()

        utils = queryUtility(IIolPraticaWeb, name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getNCT' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        nct = utils.getNCT(self)

        utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getNCEU' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        nceu = utils.getNCEU(self)

        utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
        if not 'getAllegati' in dir(utils):
            utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

        allegati = utils.getAllegati(self)
	
        result = client.service.aggiungiPratica(procedimento=pr,soggetti=soggetti,indirizzi=indirizzi,catasto_terreni=nct, catasto_urbano=nceu, allegati=list())

        result = dict(result)
        if result["pratica"]:
            files_ok = files_err = 0
            for allegato in allegati:
                res = client.service.aggiungiAllegato(result["pratica"],allegato)
                nfiles = len(allegato.files)
                res = dict(res)

                #if(res['success']==1):
                #    files_ok += res['cont']
                #    files_err += res['err']
                #else:
                #    files_err += nfiles
            #if files_err:
            #    result['messages'].append("Si sono verificati %d errori nel trasferimento degli allegati" % files_err)
            #if files_ok:
            #    result['messages'].append("Sono stati trasferiti correttamente %d allegati" % files_ok)
        return result

    security.declarePublic('trovaProcedimento')
    def trovaProcedimento(self):
        client = self.client
        doc = self.document
        procedimento = client.service.trovaProcedimento(doc.getItem('numero_pratica'))
        result = dict(procedimento)
        return result

    
    security.declarePublic('invia_integrazione')
    def invia_integrazione(self):
        client = self.client
        doc = self.document
        idoc = IolDocument(doc)        
        procedimento = client.service.trovaProcedimento(doc.getItem('numero_pratica'))
        result = dict(procedimento)
        if result['id'] != None:
            pratica = result['id']
            integrazione = client.factory.create('integrazione')
            integrazione.prot_integ = doc.getItem('numero_protocollo','')
            integrazione.data_integ = doc.getItem('data_protocollo','').strftime('%d/%m/%Y')
            integrazione.note = doc.getItem('descrizione_allegati','')

            res = client.service.aggiungiIntegrazione(pratica,integrazione)

            if res["success"]==1:
                utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
                if not 'getAllegati' in dir(utils):
                    utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)

                allegati = utils.getAllegati(self)
                for allegato in allegati:
                    res = client.service.aggiungiAllegato(pratica,allegato)

                utils = queryUtility(IIolPraticaWeb,name=self.tipo_app, default=config.APP_FIELD_DEFAULT_VALUE)
                if not 'getEsecutori' in dir(utils):
                    utils = getUtility(IIolPraticaWeb, config.APP_FIELD_DEFAULT_VALUE)
                soggetti = utils.getEsecutori(self)
                for sog in soggetti:
                    r = client.service.aggiungiSoggetto(pratica,sog,1)

            return res
   
    security.declarePublic('infoProcedimento')
    def infoProcedimento(self):
        client = self.client
        doc = self.document
        idoc = IolDocument(doc)        
        trova_procedimento = client.service.trovaProcedimento(doc.getItem('numero_pratica'))
        result = dict(trova_procedimento)        
        if result['id'] != None:            
            Procedimento = client.service.infoProcedimento(dict(trova_procedimento)['id'])                    
            res = ''            
            if Procedimento['success']==1:
                res = dict(Procedimento['result'])                
            if res !='':
                procedimento = json.dumps(dict(res['procedimento']))                            
                doc.setItem('procedimento',procedimento)        
                if len(res['progettisti'])>0:
                    progettista =  json.dumps(dict(res['progettisti'][0]))
                    doc.setItem('progettista',progettista)        
                if len(res['richiedenti'])>0:
                    richiedente = json.dumps(dict(res['richiedenti'][0]))
                    doc.setItem('richiedente',richiedente)
                if len(res['direttore_lavori'])>0:
                    direttore_lavori = json.dumps(dict(res['direttore_lavori'][0]))
                    doc.setItem('direttore_lavori',direttore_lavori)
                if len(res['esecutori'])>0:
                    esecutore = json.dumps(dict(res['esecutori'][0]))
                    doc.setItem('esecutore',esecutore)
                if len(res['indirizzi'])>0:
                    elenco_civici = []
                    for ind in res['indirizzi']:
                        elenco_civici.append(dict(ind))               
                    doc.setItem('elenco_civici',json.dumps(elenco_civici))
        
            
        




InitializeClass(IolWSPraticaWeb)
