from itertools import permutations, combinations, combinations_with_replacement
 
# Get all permutations of [1, 2, 3]
perm = permutations([9,8,7,6,5,4,3,2,1,0])

# perm = permutations([1,2,30)
# print(len(list(perm)))
# Print the obtained permutations
j = 0
posibles = {9876543210}
# vacio = ""
for i in list(perm):
    # print (i)
    j = j + 1
    digitos = len(i)
    numero = 0
    cont = 0
    for k in i:
        cont += 1
        numero += k * 10 ** (digitos - cont)
    if i[-1] % 2 == 0 and i[0] != 0:
        posibles.add(numero)
    if j % 1000000 == 0:
        print(j)

print(len(posibles))
for x in range(100):
    maxi = max(posibles)
    probar = maxi // 2
    print(f"Probando {maxi} / 2 = {probar}")
    if probar not in posibles:
        x = [int(a) for a in str(probar)]
        masposibles = permutations(x)

        for m in masposibles:
            if m[-1] % 2 == 0 and m[0] != 0:
                digitos = len(m)
                cont = 0
                numero = 0
                for k in m:
                    cont += 1
                    numero += k * 10 ** (digitos - cont)
                posibles.add(numero)
                    
    posibles.remove(maxi)
    print(f"TOTAL: {len(posibles)}. Se eliminó {maxi}")
# print("LISTO \n\n")
print(len(posibles))