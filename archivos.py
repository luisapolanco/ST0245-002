with open ("calles_de_medellin_con_acoso.csv") as archivo1:
    texto = archivo1.read()
    
with open ("calles_de_medellin_con_acoso.csv") as archivo2:
    listaLineas = archivo2.readlines()

print(len(  listaLineas))
print( listaLineas [0] )
print( listaLineas [1] )
print( listaLineas [0].split(";"))
print( listaLineas [0].split(";") [5] )