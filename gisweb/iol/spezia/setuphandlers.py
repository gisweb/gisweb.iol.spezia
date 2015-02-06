from plone.app.controlpanel.security import ISecuritySchema
from plone import api
from Products.Five.utilities.marker import mark
from .interfaces import IIolDocument
import logging

PROFILE_ID = 'gisweb.iol.spezia.replication:default'
logger = logging.getLogger('gisweb.iol.spezia')

def initPackage(context):
    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(portal_type='PlominoDatabase')
    for brain in brains:
        db = brain.getObject()
        for doc in db.getAllDocuments():
            if not IIolDocument.providedBy(doc):
                mark(doc,IIolDocument)

