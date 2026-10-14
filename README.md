# Presentacion

El **Work Manager** es un proyecto de herramienta de software para la automatizacion y sistematizacion de procesos que propuse y desarrolle para mis actividades laborales, como una iniciativa extracurricular.

## Objetivos

Los objetivos de esta herramienta fueron sistematizar la atencion a clientes con la finalidad de dar un seguimiento profesional, completo y puntual, ademas de proporcionar herramientas que permitieran aumentar el rendimiento y mejorar los procesos laborales, haciendolos mas rapidos y faciles; con el proposito de que el asesor pudiera encargarse de lo importante: una atencion de calidad al cliente, con un seguimiento profundo y atento.

## Utilidades

La herramienta automatiza actividades como:

- Recuperacion, y almacenamiento de clientes
- Exportacion de clientes a formatos populares (como Excel)
- Inicio de sesion 
- Generacion de volumen de llamadas

Y agrega:

- Almacenamiento de credenciales
- Registro de historiales
- Añadido de atajos

Pudiendo agregar mas funcionalidades, como:

- Automatizacion sistematica de envio de mensajes de marketing

> Esto no fue concluido debido a falta de recursos provistos por la empresa, pero el sistema fue diseñado de forma completa.

### Personalizacion de comunicaciones - Sistema de seguimiento automatizado
El proyecto tambien definio un sistema de comunicaciones de marketing, definiendo:

- Plantillas de mensajes (personalizadas con **Sparky**: https://github.com/specter327/proyects/tree/main/Sparky)

- Horarios de comunicacion
- Flujos de estado de cliente-producto y seguimiento evolutivo
. Atencion automatizada con chat-bot

### Medios de comunicacion
Soportando comunicaciones por medio de:

- Correo electronico
- Mensajeria SMS (con **SMSGateAPI**: https://github.com/specter327/proyects/tree/main/SMSGateAPI, o con dispositivos GSM/GPRS)

- Estadisticas, y notificaciones

Sobre eventos como:

- Venta de producto
- Cambio de estado de cliente
- Cambios en el producto de cliente

## Recursos

Este proyecto fue programado enteramente con Python, integrando JavaScript para control de navegador web. Se utilizaron librerias multiplataforma como:

- **PyQT5** para la creacion de la interfaz grafica (GUI)
- **Selenium** como interfaz hacia el controlador del navegador web (en este caso, adoptamos Google Chrome)
- **Pandas** para formateo de datos
- **SQLite** y **JSON** para el almacenamiento de bases de datos
- **Logging** para registros
- **SMTP** para envio de correos electronicos
- **SMSGateAPI** y **PySerial** (con comandos AT) para envio de mensajes SMS

Tambien, se diseño un controlador para navegador web: *WebController*, el cual potencialmente es adaptable a la gestion de cualquier sitio web, junto con sus paginas web.

## Arquitectura

El software fue diseñado con una arquitectura modular: la aplicacion principal unicamente exponia un marco estructural que permitia cargar "modulos", cada cual con funciones que pudieran ser cargadas graficamente en la interfaz de la aplicacion. Cada funcion residia dentro de su propio modulo, pero tambien se diseño un mecanismo de comunicacion entre modulos, con la finalidad de crear una comparticion de datos.

## Seguridad
### Validacion de licencia
Tambien se diseño un mecanismo de validacion de licencia. Este mecanismo se basaba en el uso de un servidor de validacion; siempre que este servidor estuviera activo, la aplicacion se determinaria como "valida". Pero, cuando no lo estuviera, se bloquearia por seguridad la aplicacion completa.

Esto fue implementado en la practica con un tunel de NGROK, y un servidor HTTP simple que pudiera ser desplegado en cualquier dispositivo: en una computadora personal, un celular, un servidor, etcetera

### Validacion de usuario
Ademas, se implemento una validacion de usuario, con la finalidad de identificar a cada usuario de la aplicacion mediante una identificacion unica generada a partir de datos base de su dispositivo (como numero serial del BIOS, y otros componentes del sistema)
