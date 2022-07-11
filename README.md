# CI-3641-Tipos
Simula un manejador de tipos de datos el cual tiene soporte a tipos atómicos, registros y registros variantes, tal que puede mostrar 
información sobre la los bytes usados por el tipo, su alineación y cuantos bytes despedicia. Hecho en Python 3.10.5.

## Modo de uso
### Ejecución
Correr el archivo **Simulador.py** con Python 3.10.5.

### Comandos del programa
```
Uso:
ATOMICO <NOMBRE> <REP> <ALI>
  Define tipo atomico de nombre <NOMBRE> que ocupa <REP> bytes y se alinea a <ALI> bytes                

STRUCT <NOMBRE> [<TIPO>]
  Crea un registro de nombre <NOMBRE> con campos con tipo y orden [<TIPO>]

UNION <NOMBRE> [<TIPO>]
  Crea un registro variante de nombre <NOMBRE> con campos con tipo y orden [<TIPO>]                
 
DESCRIBIR <NOMBRE>
  Muestra el tamano, alineacion y cantidad de bytes desperdiciados del tipo con nombre <NOMBRE> en los siguientes casos: 
  
    .Cuando el lenguaje guarda registros y registros variantes sin empaquetar.
    .Cuando el lenguaje guarda registros y registros variantes empaquetados.
    .Cuando el lenguaje guarda registros y registros variantes reordenando los
    campos de manera óptima (minimizando la memoria, sin violar reglas de alineación).
    
SALIR
  Mata\sale del programa.            
```

### Nota sobre el espacio desperdiciado e
Cuando se calcula el espacio desperdiciado por una struct, no se toma en cuenta el padding/espacio desperdiciado por campos de tipo registro o 
registro variantes del struct definido, solo se cuenta el padding entre los campos del struct.
