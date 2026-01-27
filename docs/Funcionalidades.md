====================
Modulos requeridos

- Control de CRM
Este modulo debe implementar funciones para:
 1. Generar volumen de llamadas
 2. Extraer contactos del dia de hoy
 3. Exportar contactos
 4. Activar/Desactivar modo predictivo
 5. Consultar informacion de estado
 6. Iniciar sesion
 7. Cerrar sesion

Con datos como:
 1. Nombre de usuario
 2. Contraseña

- Control de autenticacion
Este modulo debe implementar funciones para:
 1. Iniciar sesion
 2. Cerrar sesion
 3. Consultar estado actual

Con datos como:
 1. Nombre de usuario
 2. Contraseña

- Control de comunicaciones
Este modulo debe implementar funciones para:
 1. Enviar mensaje (por medio de comunicacion: Correo electronico, WhatsApp, SMS, etcetera)

====================
Arquitectura

La aplicacion debe tener una interfaz grafica simple. Idealmente debe contener un
apartado principal donde se incluye el contenido, y en un apartado lateral, una botonera
para acceder a modulos, los cuales cargaran su contenido dinamicamente

Cada modulo es totalmente independiente y tendran acceso a la interfaz grafica, permitiendo
asi la interaccion con el usuario

De esta forma, logramos un desarrollo modular, pues la modificacion de la aplicacion general
afecta unicamente a la misma, y la modificacion de cada modulo afecta unicamente al modulo
en cuestion. Por otra parte, la implementacion de nuevas funiones es tan simple como integrar
nuevos modulos


====================
Arquitectura principal - Modular

La arquitectura principal proporcionara una base para la aplicacion, y permitira la integracion
de modulos que extenderan las capacidades de la misma

Cada modulo es independiente y diferente, pero deben cumplir con una interfaz uniforme (contrato) 
para permitir la modularidad

====================
Interfaz (contrato) de modulo

Cada modulo debe cumplir con tener:
- Datos:
 1. Nombre del modulo

- Funciones:
 1.

====================
Modulos

Cada modulo estara compuesto por dos partes:

Interfaz grafica
       |
 Nucleo funcional

La interfaz grafica implementara solamente los elementos necesarios para interactuar con el
modulo tanto para la entrada de datos por parte del usuario (escritura, seleccion de botones, etcetera),
como tambien para la salida de datos por parte del modulo (campos de texto, colores, etcetera)

Este elemento de interfaz debe cumplir con las convenciones (contrato) especificadas por la arquitectura
principal para permitir la integracion

Por otra parte, el nucleo funcional sera el encargado de implementar todo el funcionamiento del modulo,
abstrayendo de esto a la interfaz grafica