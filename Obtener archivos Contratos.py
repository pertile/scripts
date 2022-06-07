from shareplum import Site
from requests_ntlm import HttpNtlmAuth
from shutil import copyfile, copyfileobj
import urllib, requests, json

import xml.etree.ElementTree as ET
import base64, os

f = open("d:\Python\Contratos.txt", "r")
ns = {'my': 'http://schemas.microsoft.com/office/infopath/2003/myXSD/2018-10-01T13:48:26'}
headers = {'accept': "application/json;odata=verbose","content-type": "application/json;odata=verbose"}
auth = HttpNtlmAuth('fiduciaria\\fpertile', 'laBitacora5')
root_url = "http://sp01/gdo"
site = Site('http://sp01/gdo', auth=auth)
def getToken():
    contextinfo_api = root_url+"/_api/contextinfo"
    response = requests.post(contextinfo_api, auth=auth,headers=headers)
    response =  json.loads(response.text)
    digest_value = response['d']['GetContextWebInformation']['FormDigestValue']
    return digest_value
headers['X-RequestDigest']=getToken()

for x in f:
    queryContrato = {'Where': [('Eq', 'ID', x)]}
    sp_listContrato = site.List('Detalles de contrataciones')
    fieldsContrato = ['ID', 'Clave']
    sp_data_contrato = sp_listContrato.GetListItems(fields=fieldsContrato, query=queryContrato)
	
    nuevaCarpeta = sp_data_contrato[0]["Clave"]
    nuevaCarpeta = nuevaCarpeta[nuevaCarpeta.find("#")+1:]
    os.mkdir(nuevaCarpeta)
    path = os.getcwd() + "\\" + nuevaCarpeta
	

    i = 0
    adjuntos = sp_listContrato.GetAttachmentCollection(x)

    for adjunto in adjuntos:
        testfile = requests.get(adjunto, auth=auth, headers=headers)
        
        open(path + "\\Contrato" + str(i) + ".pdf", 'wb').write(testfile.content)
        i = i +1

    r = requests.get("http://sp01/gdo/_api/web/lists/GetByTitle('Servicio%20mensual%20contratado')/items?$select=ID,Constataci_x00f3_n,Contrato/Id&$expand=Contrato/Id&$filter=Contrato/Id%20eq%20" + x, auth=auth, headers=headers)

    for servicio in r.json()["d"]["results"]:
        print(servicio["Constataci_x00f3_n"])
