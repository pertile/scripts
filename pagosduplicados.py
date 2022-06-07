import os, pymssql, pandas as pd
# assign directory
directory = r'c:\temp'
convenios = []


conn = pymssql.connect(server="sp01",user="excel",password="excel",database="fiducred")
cursor = conn.cursor()

query = """
    SELECT *
    from PagosDebitoDirectoDetalle
    where PagosDDEstadoDetalle in(3,4) and 
            PagosDDCabeceraId in(select max(pagosddcabeceraid)
                from PagosDebitoDirecto
                group by PagosDDCabeceraConvenio)
            and PagosDDPeriodo=(select max(PagosDDPeriodo) from PagosDebitoDirectoDetalle)
    order by PagosDDCabeceraId

"""
cursor.execute(query)
row = cursor.fetchall()
df = pd.DataFrame(row)
df["liqcuota"] = df[9].astype(str) + "-" + df[10].astype(str)
print("Las siguientes son las cuotas duplicadas reales en los créditos")
for filename in os.listdir(directory):
    if filename[-3:].upper() == "TXT":
        with open(directory + "\\" + filename, errors='replace') as f:
            lines = f.readlines()
            i = 1
            for line in lines:
                liq = line[562:567]
                cuota = line[559:562]
                
                if liq.isnumeric():
                    liqcuota = f"{liq}-{int(cuota)}"
                    if any(df.liqcuota == liqcuota):
                        print(f"{filename} (línea {i}): {liqcuota}")
                i += 1


# for c in convenios:
#     credito = c

print(convenios)  
# for i in row:
#     try:
#         with open(i[0], 'wb') as outfile:
#             outfile.write(i[1])
#             outfile.close()
#             print("Filename Saved as: " + i[0])
#     except:
#         pass