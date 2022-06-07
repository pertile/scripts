import glob
import os
import time
import csv
#import pwd
#from typing import Union
#from pathlib import Path
#import subprocess
import win32api
import win32con
import win32security

import pandas as pd
import numpy as np
from PyPDF2 import PdfFileReader
from datetime import date
from datetime import timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


###

def owner_win32(filename):
    sd=win32security.GetFileSecurity(filename, win32security.OWNER_SECURITY_INFORMATION)
    owner_sid= sd.GetSecurityDescriptorOwner()
    name, domain, type = win32security.LookupAccountSid(None, owner_sid)
    return (name)

def test_modified(filename):
    delta=time.time()-os.path.getctime(filename)
    delta=delta/(60*60*24)
    if delta < 180:
        return True
    return False

ubicacion='C:\\Auto\\Contadortest\\'

current_time=time.time()
modified_files=list()

output_csv='C:\\Auto\\Contadortest\\output_lastrun.csv'

####
###tomo todos los pdfs del directorio pdf_dir
pdf_dir='\\\\10.0.0.15\\Digitalizacion'
pdf_files=glob.glob("%s\\**\\*.pdf" % pdf_dir, recursive=True)

##comparo lista de todos los pdf en dir con fecha X, si cumple las guardo en lista
##\\\\\\\COMENTAR EN DEBUG SI TIRA ERROR CORRUPTO PDF, TRY CATCH ERROR NO SE PUDO IMPLEMENTAR
for file in pdf_files:
    time_delta=current_time-os.path.getctime(file)
    time_delta_days=time_delta/(60*60*24)
    if time_delta_days < 32:
        modified_files.append(file)
#        print(file)
#print(modified_files)
#####guardo lista a csv para control si surgen dudas o problemas
with open(output_csv,'w') as myfile:
    for item in modified_files:
       myfile.write(item + '\n')
#####]\]\\\\\\\\\\\SACAR COMENMTARIO IMPORANTE
####SOLAMENTE DEBUG CON ARCHIVO GENERADO 
#with open(output_csv,'r') as f:
#    modified_files=[line.strip() for line in f]

#print(modified_files)
#print(mfiles)

df=pd.DataFrame(modified_files)


######Lectura
lector=[]
carp=[]
owner_list=[]

for x in modified_files:
    fol=x.split('\\')[4]
    if fol is None:
        #print(None)
        fol='0'
    if fol == 0:
        fol='0'
    print(fol)
    try:
        print(x)
        pdf=PdfFileReader(open(x, 'rb'),strict=False)
        pag=pdf.getNumPages()
        own=owner_win32(x)
        lector.append(pag)
        carp.append(fol)
        owner_list.append(own)
    except (FileNotFoundError, IOError):
        pag=0
        own='0'
        lector.append(pag)
        carp.append(fol)
        owner_list.append(own)
        pass

df['Fideicomiso'] = carp
df['Paginas'] = lector
df['User'] = owner_list

df['Fideicomiso']=df['Fideicomiso'].str.replace('Ãº','ú')
df['Fideicomiso']=df['Fideicomiso'].str.replace('Ã³','ó')
##Hay un caracter invisible despues de la A al leer en latin-1
df['Fideicomiso']=df['Fideicomiso'].str.replace('Ã­','í')
df['Fideicomiso']=df['Fideicomiso'].str.replace('Ã©','é')
df['Fideicomiso']=df['Fideicomiso'].str.replace('Ã¡','á')

print(df)

hoy=date.today().strftime('%Y-%m-%d')
suma = df.groupby(['User','Fideicomiso']).agg({'Paginas': 'sum'})
print(suma)
total= df.groupby(['User']).agg({'Paginas': 'sum'})
print(total)

suma.to_csv(ubicacion+'suma-'+hoy+'.csv')

total.to_csv(ubicacion+'total-'+hoy+'.csv')


#####----------------------------------------------------
## MAIL

#####----------------------------------------------------

#sendto = ['ezlachevsky@fiduciariadelnorte.com.ar']
sendto = ['tecno@fiduciariadelnorte.com.ar','maguilar@fiduciariadelnorte.com.ar']
user= 'info@fiduciariadelnorte.com.ar'
smtpsrv = "smtp.office365.com"
smtpserver = smtplib.SMTP(smtpsrv,587)
smtpserver.ehlo()
password = 'Fidu2021*'
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(user, password)
# header = 'To:' + sendto + 'n' + 'From: ' + user + 'n' + 'Subject:testing n'
 
today = date.today()
first = today.replace(day=1)
lastMonth = first - timedelta(days=1)
mes=lastMonth.strftime("%m-%Y")

sumamail=pd.read_csv(ubicacion+'suma-'+hoy+'.csv', encoding='latin-1', sep=',')
sumamail=sumamail[sumamail.Paginas != 0]

###ODIO CODIFICACION PARTE2
sumamail['Fideicomiso']=sumamail['Fideicomiso'].str.replace('Ãº','ú')
sumamail['Fideicomiso']=sumamail['Fideicomiso'].str.replace('Ã³','ó')
##Hay un caracter invisible despues de la A al leer en latin-1
sumamail['Fideicomiso']=sumamail['Fideicomiso'].str.replace('Ã­','í')
sumamail['Fideicomiso']=sumamail['Fideicomiso'].str.replace('Ã©','é')
sumamail['Fideicomiso']=sumamail['Fideicomiso'].str.replace('Ã¡','á')

totalmail=pd.read_csv(ubicacion+'total-'+hoy+'.csv', encoding='latin-1', sep=',')
totalmail=totalmail[totalmail.Paginas != 0]


mensaje = MIMEMultipart()
mensaje['From'] = user
mensaje['To'] = ", ".join(sendto)
mensaje['Subject'] = 'Estadistica mensual de escaneos Mes: ' + mes+ '.'

html = """\
<html>
<head></head>
<body>
    <p>Estadisticas:<br>
        Paginas escaneadas por fideicomiso:<br>
        {0}
        <br>Paginas totales escaneadas por usuario:<br>
        {1}
        <br>Si no se visualiza correctamente la tabla por favor avisar a Sistemas.<br>
        </p>
</body>
</html>
""".format(sumamail.to_html(), totalmail.to_html())

partHTML = MIMEText(html, 'html')
mensaje.attach(partHTML)

smtpserver.sendmail(user, sendto, mensaje.as_string())
smtpserver.close()
