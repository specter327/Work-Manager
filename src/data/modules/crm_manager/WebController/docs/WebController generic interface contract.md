# WebController interface (contract)
Functions:
- start
    Esta funcion inicia (abre/arranca) una instancia del navegador web
- stop
    Esta funcion detiene (cierra) la instancia del navegador web actual
- open_tab: url [str]
    Esta funcion abre en una nueva pestaña una pagina web especificada mediante su URL absoluta
- close_tab: handle [object | None]
    Esta funcion cierra una pestaña abierta, o la pestaña actual si no se especifica ninguna
- get_status
    Esta funcion consulta y retorna el estado actual del navegador (ABIERTO/CERRADO)
- query_tabs
    Esta funcion consulta y retorna las pestañas actualmente abiertas
- query_actual_tab
    Esta funcion consulta y retorna la pestaña actualmente enfocada
- is_opened
    Esta funciona consulta y retorna un valor booleano indicando si esta abierto, o no
- is_closed
    Esta funcion consulta y retorna un valor booleano indicando si esta cerrado, o no
- refresh: tab [handle]
    Esta funcion actualiza el contenido de una pestaña actualmente abierta