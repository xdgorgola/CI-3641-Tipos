from __future__ import annotations
from math import lcm, inf
import itertools


class Tipo:
    """
    Esqueleto de una clase representativa de un tipo. Guarda informacion
    sobre los bytes usados, su alineacion y los bytes desperdiciados
    en las tuplas naked, empaq, optim que representan esta informacion 
    respectivamente en los siguientes casos:

    - El lenguaje guarda registros y registros variantes sin empaquetar.
    - El lenguaje guarda registros y registros variantes empaquetados.
    - El lenguaje guarda registros y registros variantes reordenando los campos de
        manera óptima (minimizando la memoria, sin violar reglas de alineación).
    
    La informacion la almacenan en el siguiente orden:
        - Bytes usados
        - Alineacion
        - Bytes desperdiciados
    """


    naked : tuple[int, int, int] = (0,0,0)
    empaq : tuple[int, int, int] = (0,0,0)
    optim : tuple[int, int, int] = (0,0,0)


    def __init__(self : Tipo, name : str) -> None:
        self.name : str = name
    

    def imprimir_info(self : Tipo) -> None:
        """
        Imprime en pantalla la informacion relacionada al tipo
        """

        print(f"DESCRIPCION DEL TIPO {self.name}\n")
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
    """
    Representa un tipo atomico. Solo guarda nombre, espacio en
    bytes que ocupa y su alineacion.
    """


    def __init__(self : Atomico, name : str, bytes : int, alin : int) -> None:
        """
        Constructor

        Arguments:
            name -- Nombre del tipo 
            bytes -- Tamano en bytes que ocupa el tipo
            alin -- Alineaicon del tipo
        """

        super().__init__(name)
        self.bytes : int = bytes
        self.alin : int = alin

        self.naked = self.empaq = self.optim = (bytes, alin, 0)


class Struct(Tipo):
    """
    Representa un tipo registro. Guarda una lista de 
    campos con los tipos que contiene en ese orden.
    """

    
    def __init__(self : Struct, name : str, campos : list[Tipo]) -> None:
        """
        Constructor

        Arguments:
            name -- Nombre del tipo
            campos -- Campos del tipo declarados en orden
        """

        super().__init__(name)
        self.campos = campos[::]

        self.empaq = self.info_empaquetada()
        self.naked = self.info_naked()
        self.optim = self.info_opti() # Importante ir despues de la naked


    def mejor_permutacion(self : Struct) -> tuple[int,int,int]:
        """
        Calcula la mejor permutacion de los campos de la estructura
        para desperdiciar la menor cantidad de bytes posibles.

        Returns:
            La permutacion  que menos bytes desperdicia de los campos de la struct definida
        """

        minDesp : int = inf
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
        """
        Calcula los bytes usados, la alineacion y la cantidad
        de bytes despediciados si se empaqueta la estructura

        Returns:
            Tupla con los bytes usados, la alineacion y la cantidad de 
            bytes desperdiciados en ese orden
        """

        usados : int = 0
        for i in self.campos:
            usados += i.empaq[0]
        
        return (usados, self.campos[0].empaq[1], 0)
    

    def info_naked(self : Struct) -> tuple[int,int,int]:
        """
        Calcula los bytes usados, la alineacion y la cantidad
        de bytes despediciados si se dejan los campos como estan

        Returns:
            Tupla con los bytes usados, la alineacion y la cantidad de 
            bytes desperdiciados en ese orden
        """

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
        """
        Calcula los bytes usados, la alineacion y la cantidad
        de bytes despediciados si se optimiza la estructura.

        Para menos de 6 campos, se prueban todas las permutaciones
        (con mas campos puede llegar a ser muy lento).

        Par mas de 6 campos intenta minimizar la memoria gastada 
        colocando los campos con la alineacion mas grande primero.

        Returns:
            Tupla con los bytes usados, la alineacion y la cantidad de 
            bytes desperdiciados en ese orden
        """

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
         # normal es mejor que la "optimizada"
        if (desp > self.naked[2]):
            return self.naked

        return (used, sortCampos[0].optim[1], desp)
    


class Union(Tipo):
    """
    Representa un tipo registro variante. Guarda una lista de 
    campos con los tipos que puede contener en ese orden.
    """

    def __init__(self: Union, name: str, campos : list[Tipo]) -> None:
        """
        Constructor

        Arguments:
            name -- Nombre del tipo
            campos -- Campos del tipo declarados en orden
        """

        super().__init__(name)
        self.campos = campos[::]

        self.empaq = self.info_empaquetada()
        self.naked = self.info_naked()
        self.optim = self.info_optim()


    def info_empaquetada(self : Union) -> tuple[int,int,int]:
        """
        Calcula los bytes usados, la alineacion y la cantidad
        de bytes despediciados si se empaquetan los registros

        Returns:
            Tupla con los bytes usados, la alineacion y la cantidad de 
            bytes desperdiciados en ese orden
        """

        maxTam : int = 0
        alinea : list[int] = [i.naked[1] for i in self.campos] 
        
        for i in self.campos:
            maxTam = i.empaq[0] if i.empaq[0] > maxTam else maxTam
        
        # es uno o la alineacion del lcm?
        return (maxTam, lcm(*alinea), 0)
    

    def info_naked(self : Union) -> tuple[int,int,int]:
        """
        Calcula los bytes usados, la alineacion y la cantidad
        de bytes despediciados si se dejan los campos como estan
        a los registros

        Returns:
            Tupla con los bytes usados, la alineacion y la cantidad de 
            bytes desperdiciados en ese orden
        """

        maxTam : int = 0
        alinea : list[int] = [i.naked[1] for i in self.campos] 

        for i in self.campos:
            maxTam = i.naked[0] if i.naked[0] > maxTam else maxTam

        return (maxTam, lcm(*alinea), 0)


    def info_optim(self : Union) -> tuple[int,int,int]:
        """
        Calcula los bytes usados, la alineacion y la cantidad
        de bytes despediciados si se optimizan los registros

        Returns:
            Tupla con los bytes usados, la alineacion y la cantidad de 
            bytes desperdiciados en ese orden
        """

        maxTam : int = 0
        alinea : list[int] = [i.optim[1] for i in self.campos] 

        for i in self.campos:
            maxTam = i.optim[0] if i.optim[0] > maxTam else maxTam

        return (maxTam, lcm(*alinea), 0)


class ManejadorTipos:
    """
    Manejador de tipos. Simplemente se encarga de funcionar como interfaz
    para definir los tipos, asegurarse de que no se definan mas de una vez, 
    e imprimir la informacion de un tipo definido.
    """


    def __init__(self : ManejadorTipos) -> None:
        self.atomicos : dict[str, Atomico] = {}
        self.structs : dict[str, Struct] = {}
        self.unions : dict[str, Union] = {}
    

    def existe_tipo(self : ManejadorTipos, nombre : str) -> bool:
        """
        Chequea si ya existe un tipo que ya use un nombre.

        Arguments:
            nombre -- Nombre del tipo a buscar

        Returns:
            True si el tipo ya fue definido como atomico, struct o union
        """

        return nombre in self.atomicos or nombre in self.structs or nombre in self.unions

    
    def mostrar_info_tipo(self : ManejadorTipos, nombre : str) -> bool:
        """
        Muestra la informacion de un tipo en caso de existir

        Arguments:
            nombre -- Tipo a mostrar informacion

        Returns:
            True si el tipo existe. False en caso contrario.
        """

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
        """
        Define un tipo atomico.

        Arguments:
            nombre -- Nombre del tipo
            bytes -- Bytes que ocupa
            alin -- Alineacion del tipo

        Returns:
            True si el tipo no existia ya y se pudo crear. False en caso contrario.
        """

        if (self.existe_tipo(nombre)):
            print(f"Un tipo de nombre {nombre} ya existe.")
            return False
        
        self.atomicos[nombre] = Atomico(nombre, bytes, alin)
        return True
    

    def definir_struct(self : ManejadorTipos, nombre : str, campos : list[str]) -> bool:
        """
        Define una struct si no existe ya y si los tipos de 
        sus campos estan definidos.

        Arguments:
            nombre -- Nombre del tipo
            campos -- Campos del struct en orden de aparicion

        Returns:
            True si pudo crearse el struct. False en caso contrario
        """

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
        """
        Define una union si no existe ya y si los tipos de 
        sus campos estan definidos.

        Arguments:
            nombre -- Nombre del tipo
            campos -- Campos del union en orden de aparicion

        Returns:
            True si pudo crearse el union. False en caso contrario
        """

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