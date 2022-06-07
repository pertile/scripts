import pymssql
stmt = "Select NombreArchivo, Archivo from ResumenesDetalle;"
conn = pymssql.connect(server="sp01",user="excel",password="excel",database="indicadores")
cursor = conn.cursor()
cursor.execute(stmt)
row = cursor.fetchall()
for i in row:
    try:
        with open(i[0], 'wb') as outfile:
            outfile.write(i[1])
            outfile.close()
            print("Filename Saved as: " + i[0])
    except:
        pass