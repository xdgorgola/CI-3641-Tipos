from Manejador import ManejadorTipos

# Tokens programa
TOKEN_DESCRIBIR = "DESCRIBIR"
TOKEN_ATOMICO = "ATOMICO"
TOKEN_STRUCT = "STRUCT"
TOKEN_UNION = "UNION"
TOKEN_SALIR = "SALIR"

run : bool = True
manejador : ManejadorTipos = ManejadorTipos()

def simulator_usage():
    print("Uso:\n\tATOMICO <NOMBRE> <REP> <ALI>")
    print("\t\tDefine tipo atomico de nombre <NOMBRE> que ocupa" \
        + " <REP> bytes y se alinea a <ALI> bytes")

    print("\n\tSTRUCT <NOMBRE> [<TIPO>]")
    print("\t\tCrea un registro de nombre <NOMBRE> con campos con tipo y orden [<TIPO>]")

    print("\n\tUNION <NOMBRE> [<TIPO>]")
    print("\t\tCrea un registro variante de nombre <NOMBRE> con campos con tipo y orden [<TIPO>]")

    print("\n\tDESCRIBIR <NOMBRE>")
    print("\t\tMuestra el tamano, alineacion y cantidad de bytes desperdiciados" \
        + " del tipo con nombre <NOMBRE> en los siguientes casos:")

    print("\t\t-Cuando el lenguaje guarda registros y registros variantes sin empaquetar.")
    print("\t\t-Cuando el lenguaje guarda registros y registros variantes empaquetados.")
    print("\t\t-Cuando el lenguaje guarda registros y registros vaariantes reordenando los")
    print("\t\t campos de manera óptima (minimizando la memoria, sin violar reglas de alineación).")

    print("\n\tSALIR\n\t\tMata\\sale del programa.")


def wrong_params():
    print("Parametro invalido o numero de parametros incorrecto.")
    simulator_usage()


def comando_atomico(tokens : list[str]) -> None:
    if (len(tokens) < 3):
        wrong_params()
        return
    
    if (not all(map(str.isnumeric, tokens[1::]))):
        wrong_params()
        return
    
    manejador.definir_atomico(tokens[0], int(tokens[1]), int(tokens[2]))


def comando_struct(tokens : list[str]) -> None:
    if (len(tokens) < 2):
        wrong_params()
        return
    
    manejador.definir_struct(tokens[0], tokens[1::])


def comando_union(tokens : list[str]) -> None:
    if (len(tokens) < 2):
        wrong_params()
        return
    
    manejador.definir_union(tokens[0], tokens[1::])


def comando_describir(tokens : list[str]) -> None:
    if (len(tokens) != 1):
        wrong_params()
        return
    
    manejador.mostrar_info_tipo(tokens.pop())

while (run):
    tokens : list[str] = input("Introduce un comando>").split()
    if (len(tokens) == 0):
        print("Comando no valido.")
        continue

    comando : str = tokens.pop(0).upper()
    if (comando == TOKEN_ATOMICO):
        comando_atomico(tokens)
    elif (comando == TOKEN_STRUCT):
        comando_struct(tokens)
    elif (comando == TOKEN_UNION):
        comando_union(tokens)
    elif (comando == TOKEN_DESCRIBIR):
        comando_describir(tokens)
    elif (comando == TOKEN_SALIR):
        run = False
    else:
        wrong_params()