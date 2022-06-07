import pymssql, pandas as pd

stmt = "Select NombreArchivo, Archivo from ResumenesDetalle;"
# conn = pymssql.connect(server="sp01",user="python",password="tXQD8dAX",database="indicadores")

c = pd.read_excel(r'c:\temp\compras.xlsx', index_col=0)

for f in c:
    print(f[0])

# cursor = conn.cursor()
# cursor.execute(stmt)
# row = cursor.fetchall()
# for i in row:
#     try:
#         with open(i[0], 'wb') as outfile:
#             outfile.write(i[1])
#             outfile.close()
#             print("Filename Saved as: " + i[0])
#     except:
#         pass

# conn = pyodbc.connect('DRIVER={SQL Server};SERVER=sp01;DATABASE=Indicadores;UID=python;PWD=tXQD8dAX')

# cursor = conn.cursor()

# ####execute

# cursor.execute("DELETE FROM OPSAFyC")



 

# cursor.commit()



# for index, row in df.iterrows():

#     print(row)

#     cursor.execute("INSERT INTO OPSAFyC (cuit,Total,Integrado,Disponible,OP,fuente) values (?,?,?,?,?,?)", row.cuit, row.Total, row.Integrado, row.Disponible, row.OP, row.fuente)





# cursor.commit()

# conn.close()