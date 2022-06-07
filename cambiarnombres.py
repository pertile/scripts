import os
# assign directory
directory = r'\\fs02\Digitalizacion\1000-Fiduciaria del Norte SA\OP1500 2018'
 
# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    name = filename.split(".")[0]
    extension = filename.split(".")[1]
    if name.isnumeric():
        numero = int(name)
        if numero < 1500000 or numero > 1599999:
            nuevoNumero = 1500000 + int(name[2:])
            os.rename(directory + "\\" + filename, directory + "\\" + str(nuevoNumero) + "." + extension)
            print(f"Renombrado de {name} a {nuevoNumero}.{extension}")
    else:
        print("no es numero " + name)