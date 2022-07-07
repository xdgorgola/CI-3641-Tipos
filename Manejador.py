from __future__ import annotations
import itertools
from math import lcm
import math

"""
• El lenguaje guarda registros y registros viariantes sin empaquetar.
• El lenguaje guarda registros y registros viariantes empaquetados.
• El lenguaje guarda registros y registros viariantes reordenando los campos de
    manera óptima (minimizando la memoria, sin violar reglas de alineación).
"""
class Tipo:
    #first es tamano
    #second es alineacion
    #third es desperdiciados
    naked : tuple[int, int, int] = (0,0,0)
    empaq : tuple[int, int, int] = (0,0,0)
    optim : tuple[int, int, int] = (0,0,0)

    def __init__(self : Tipo, name : str) -> None:
        self.name : str = name
    

    def imprimir_info(self : Tipo) -> None:
        print("INFO TAMANO EMPAQUETADO")
        print("-" * 30)
        print(f"Bytes que ocupa {self.empaq[0]}")
        print(f"Alineacion {self.empaq[1]}")
        print(f"Bytes desperdiciados {self.empaq[2]}")
        print("-" * 30 + "\n")

        print("INFO TAMANO SIN EMPAQUETAR")
        print("-" * 30)
        print(f"Bytes que ocupa {self.naked[0]}")
        print(f"Alineacion {self.naked[1]}")
        print(f"Bytes desperdiciados {self.naked[2]}")
        print("-" * 30 + "\n")

        print("INFO TAMANO OPTIMIZADO")
        print("-" * 30)
        print(f"Bytes que ocupa {self.optim[0]}")
        print(f"Alineacion {self.optim[1]}")
        print(f"Bytes desperdiciados {self.optim[2]}")
        print("-" * 30 + "\n")

    
class Atomico(Tipo):

    def __init__(self : Atomico, name : str, bytes : int, alin : int) -> None:
        super().__init__(name)
        self.bytes : int = bytes
        self.alin : int = alin

        self.naked = self.empaq = self.optim = (bytes, alin, 0)


class Struct(Tipo):

    def __init__(self : Struct, name : str, campos : list[Tipo]) -> None:
        super().__init__(name)
        self.campos = campos[::]

        self.empaq = self.info_empaquetada()
        self.naked = self.info_naked()
        self.optim = self.info_opti() # Importante ir de ultima


    def mejor_permutacion(self : Struct) -> tuple[int,int,int]:
        minDesp : int = math.inf
        minPerm : tuple[int,int,int]

        for p in itertools.permutations(self.campos):
            used : int = 0
            desp : int = 0
            b : int = 0
            for i in range(len(p)):
                (s, _, _) = p[i].optim
                used += s

                if (i == len(p) - 1):
                    break
                
                ul : int = b + s
                na : int = p[i+1].optim[1]
                if (ul % na == 0):
                    b += s
                    continue

                nb : int = ul + (na - (ul % na))
                used += nb - ul
                desp += nb - ul
                b = nb
            
            if (desp < minDesp):
                minDesp = desp
                minPerm = (used, p[0].optim[1], desp)
        
        return minPerm


    def info_empaquetada(self : Struct) -> tuple[int,int,int]:
        usados : int = 0
        for i in self.campos:
            usados += i.empaq[0]
        
        # es uno o la alineacion del 1ero?
        return (usados, 1, 0)
    

    def info_naked(self : Struct) -> tuple[int,int,int]:

        used : int = 0
        desp : int = 0
        b : int = 0
        for i in range(len(self.campos)):
            (s, _, _) = self.campos[i].naked
            used += s

            if (i == len(self.campos) - 1):
                break
            
            ul : int = b + s
            na : int = self.campos[i+1].naked[1]
            if (ul % na == 0):
                b += s
                continue

            nb : int = ul + (na - (ul % na))
            used += nb - ul
            desp += nb - ul
            b = nb
        
        return (used, self.campos[0].naked[1], desp)


    def info_opti(self : Struct) -> tuple[int,int,int]:

        if (len(self.campos) <= 6):
            return self.mejor_permutacion()

        used : int = 0
        desp : int = 0
        b : int = 0
        sortCampos : list[Tipo] = sorted(self.campos, \
            key = lambda t:t.optim[1], reverse = True)
        
        for i in range(len(sortCampos)):
            (s, _, _) = sortCampos[i].optim
            used += s

            if (i == len(sortCampos) - 1):
                break
            
            ul : int = b + s
            na : int = sortCampos[i+1].optim[1]
            if (ul % na == 0):
                b += s
                continue

            nb : int = ul + (na - (ul % na))
            used += nb - ul
            desp += nb - ul
            b = nb

         # No usar la nueva configuracion si la configuracion
         # normal es mejor
        if (desp > self.naked[2]):
            return self.naked

        return (used, sortCampos[0].optim[1], desp)
    


class Union(Tipo):

    def __init__(self: Union, name: str, campos : list[Tipo]) -> None:
        super().__init__(name)
        self.campos = campos[::]

        self.empaq = self.info_empaquetada()
        self.naked = self.info_naked()
        self.optim = self.info_optim()


    def info_empaquetada(self : Union) -> tuple[int,int,int]:
        maxTam : int = 0

        for i in self.campos:
            maxTam = i.empaq[0] if i.empaq[0] > maxTam else maxTam
        
        # es uno o la alineacion del lcm?
        return (maxTam, 1, 0)
    

    def info_naked(self : Union) -> tuple[int,int,int]:
        maxTam : int = 0
        alinea : list[int] = [i.naked[1] for i in self.campos] 

        for i in self.campos:
            maxTam = i.naked[0] if i.naked[0] > maxTam else maxTam

        return (maxTam, lcm(*alinea), 0)


    def info_optim(self : Union) -> tuple[int,int,int]:
        maxTam : int = 0
        alinea : list[int] = [i.optim[1] for i in self.campos] 

        for i in self.campos:
            maxTam = i.optim[0] if i.optim[0] > maxTam else maxTam

        return (maxTam, lcm(*alinea), 0)


class ManejadorTipos:

    def __init__(self : ManejadorTipos) -> None:
        self.atomicos : dict[str, Atomico] = {}
        self.structs : dict[str, Struct] = {}
        self.unions : dict[str, Union] = {}
    

    def existe_tipo(self : ManejadorTipos, nombre : str) -> bool:
        return nombre in self.atomicos or nombre in self.structs or nombre in self.unions

    
    def mostrar_info_tipo(self : ManejadorTipos, nombre : str) -> bool:
        if (not self.existe_tipo(nombre)):
            print(f"El tipo {nombre} no existe")
            return False
        
        if (nombre in self.atomicos):
            self.atomicos[nombre].imprimir_info()
            return True
            
        if (nombre in self.structs):
            self.structs[nombre].imprimir_info()
            return True
        
        self.unions[nombre].imprimir_info()
        return True


    def definir_atomico(self : ManejadorTipos, nombre : str, bytes : int, alin : int) -> bool:
        if (self.existe_tipo(nombre)):
            print(f"Un tipo de nombre {nombre} ya existe.")
            return False
        
        self.atomicos[nombre] = Atomico(nombre, bytes, alin)
        return True
    

    def definir_struct(self : ManejadorTipos, nombre : str, campos : list[str]) -> bool:
        if (self.existe_tipo(nombre)):
            print(f"Un tipo de nombre {nombre} ya existe.")
            return False
        
        for n in campos:
            if (not self.existe_tipo(n)):
                print(f"El tipo de nombre {nombre} no existe.")
                return False
        
        c : list[Tipo] = []
        for i in campos:
            if (i in self.atomicos):
                c.append(self.atomicos[i])
                continue
            
            if (i in self.structs):
                c.append(self.structs[i])
                continue

            c.append(self.unions[i])
        
        self.structs[nombre] = Struct(nombre, c)
        return True


    def definir_union(self : ManejadorTipos, nombre : str, campos : list[str]) -> bool:
        if (self.existe_tipo(nombre)):
            print(f"Un tipo de nombre {nombre} ya existe.")
            return False
        
        for n in campos:
            if (not self.existe_tipo(n)):
                print(f"El tipo de nombre {nombre} no existe.")
                return False
        
        c : list[Tipo] = []
        for i in campos:
            if (i in self.atomicos):
                c.append(self.atomicos[i])
                continue
            
            if (i in self.structs):
                c.append(self.structs[i])
                continue

            c.append(self.unions[i])
        
        self.unions[nombre] = Union(nombre, c)
        return True


#man : ManejadorTipos = ManejadorTipos()
#man.definir_atomico("bool", 1, 2)
#man.definir_atomico("char", 1, 2)
#man.definir_atomico("char2", 2, 2) # array de 2 chars jeje
#man.definir_atomico("int", 4, 4)
#man.definir_atomico("double", 8, 8)
#man.definir_struct("meta", ["int", "char2", "int", "double", "bool"])
##man.mostrar_info_tipo("meta")
#
#man.definir_union("todos_unidos", ["char", "char2", "double", "int"])
##man.mostrar_info_tipo("todos_unidos")
#
#man.definir_atomico("bobo", 1, 16)
#man.definir_atomico("tonto", 3, 7)
#man.definir_struct("xd", ["bobo", "bobo", "bobo", "tonto"])
##man.mostrar_info_tipo("xd")
#
#man.definir_struct("mago", ["bool", "bool", "xd", "tonto", "bool", "bool"])
#man.mostrar_info_tipo("mago")