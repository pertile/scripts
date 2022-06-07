from shareplum import Site
from requests_ntlm import HttpNtlmAuth
from shutil import copyfile, copyfileobj
import urllib, requests, json

import xml.etree.ElementTree as ET
import base64, os

f = open("c:\Python\Facturas.txt", "r")
ns = {'my': 'http://schemas.microsoft.com/office/infopath/2003/myXSD/2018-10-01T13:48:26'}
headers = {'accept': "application/json;odata=verbose","content-type": "application/json;odata=verbose"}
auth = HttpNtlmAuth('fiduciaria\\fpertile', 'laBitacora7')
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
  nombreArchivo = "\\\\sp01\\contable\\facturas\\" + x[x.rfind("/")+1:]
  nombreArchivo = nombreArchivo.rstrip("\n")
  tree = ET.parse(nombreArchivo)
  root = tree.getroot()
  cuit = root.find('my:CUITFactura', ns).text
  referencia = root.find('my:Referencia', ns).text
  nuevaCarpeta = cuit + '-' + referencia
  os.mkdir(nuevaCarpeta)
  path = os.getcwd() + "\\" + nuevaCarpeta
  with open(path + "\\Factura.pdf", "wb") as fh:
    fh.write(base64.b64decode(root.find('my:Documento', ns).text))
    fh.close()
  servicioMensual = root.find('my:ServicioMensual', ns)
  servicioMensual2 = root.find('my:ServicioMensual2', ns)
  servicioMensual3 = root.find('my:ServicioMensual3', ns)
  fields = ['ID', 'Constatación', 'Contrato']

  if servicioMensual.text is not None:
 
    sp_list = site.List('Servicio mensual contratado')

    if servicioMensual != '':
      query = {'Where': [('Eq', 'ID', servicioMensual.text)]}
      sp_data = sp_list.GetListItems(fields=fields, query=query)

      constatación = sp_data[0]['Constatación']
      constatación = constatación[constatación.rfind("/")+1:]
      archivoConstatación = "\\\\sp01\\gdo\\Constatacin de servicio\\" + urllib.parse.unquote(constatación)
      copyfile(archivoConstatación, path + "\\Certificación.pdf")
      
      contrato = sp_data[0]['Contrato']
      contratoID = contrato[:contrato.find(";")]
      r = requests.get("http://sp01/gdo/_api/web/lists/GetByTitle('Detalles%20de%20contrataciones')/items(" + contratoID + ")/AttachmentFiles", auth=auth, headers=headers)
      i = 0
      for element in r.json()["d"]["results"]:
        print("http://sp01" + element["ServerRelativeUrl"])
        testfile = requests.get("http://sp01" + element["ServerRelativeUrl"], auth=auth, headers=headers)
        open(path + "\\Contrato" + str(i) + ".pdf", 'wb').write(testfile.content)
        i = i +1
      queryContrato = {'Where': [('Eq', 'ID', contratoID)]}
      sp_listContrato = site.List('Detalles de contrataciones')
      fieldsContrato = ['ID', 'Precio', 'Resolución']
      sp_data_contrato = sp_listContrato.GetListItems(fields=fieldsContrato, query=queryContrato)

      reso = sp_data_contrato[0]['Resolución']
      reso = reso[reso.rfind("/")+1:]
      archivoReso = "\\\\sp01\\Secretaría\\Mesa de entradas\\" + reso
      tree2 = ET.parse(archivoReso)
      root2 = tree2.getroot()
      with open(path + "\\Resolución.pdf", "wb") as fh:
        fh.write(base64.b64decode(root2.find('my:Documento', ns).text))
        fh.close()
  else:
    print(x + " no tiene un servicio asociado")
  print(servicioMensual2.text)
  if servicioMensual2.text is not None:
    query = {'Where': [('Eq', 'ID', servicioMensual2.text)]}
    sp_data = sp_list.GetListItems(fields=fields, query=query)
    constatación = sp_data[0]['Constatación']
    constatación = constatación[constatación.rfind("/")+1:]
    archivoConstatación = "\\\\sp01\\gdo\\Constatacin de servicio\\" + urllib.parse.unquote(constatación)
    copyfile(archivoConstatación, path + "\\Certificación2.pdf")
  if servicioMensual3.text is not None:
    query = {'Where': [('Eq', 'ID', servicioMensual3.text)]}
    sp_data = sp_list.GetListItems(fields=fields, query=query)
    constatación = sp_data[0]['Constatación']
    constatación = constatación[constatación.rfind("/")+1:]
    archivoConstatación = "\\\\sp01\\gdo\\Constatacin de servicio\\" + urllib.parse.unquote(constatación)
    copyfile(archivoConstatación, path + "\\Certificación3.pdf")


# Certificación de servicios
  # repetir para Servicios Mensuales Contratados 2 y 3.
# Contrato
  # al agregar $select=Attachments,AttachmentFiles&$expand=AttachmentFiles en el web service
  # descargar todos los adjuntos
# Resolucion
  # por cada Contrato abrir Resolucion
  # descargar Resolucion
  

