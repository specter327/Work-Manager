# Estructura de elementos
        User
         |
      WebSite
         |
 WebFolder/WebPage
         |
     WebBrowser
         |
    WebController
         |
 Physical web browser

# WebBrowser
Esta clase proporciona una representacion de alto nivel sobre un navegador web, y proporciona un conjunto de metodos y propiedades generales. Internamente, utiliza un controlador de navegador web enfocado a cubrir las necesidades del navegador subyacente que se este utilizando para trabajar. Pero, abstrae y encapsula la variabilidad, permitiendo asi disponer de una plataforma uniforme, flexible, escalable, y robusta

Hay que recordar que, entre el WebBrowser y el WebController, hay una interfaz (o contrato) bien definido sobre las propiedades y metodos publicos que debe tener para formar parte de la plataforma uniforme

# WebController
Esta clase provee dos areas:

- Publica (externa): Proporciona una capa de metodos y propiedades generales, que cumplen con una interfaz estandarizada. Permite una plataforma igualitaria sin importar el navegador utilizado
- Privada (interna): Proporciona el conjunto de metodos y propiedades internas que requiere la clase de controlador de navegador web en particular. Abstrae y encapsula las diferencias

Cualquier navegador web, sera manejado utilizando una clase de WebController especifica a el, donde para proveer las funcionalidades publicas y generales, hara uso de sus propios medios (o bien, indicara que no dispone de algun dato o funcion), de forma que se encapsulara la variabilidad

Estructura interna:
        Funciones/datos publicos genericos
                       |
      Funciones/datos privados personalizados
      
# WebSite
Esta clase proporciona una representacion abstracta de un sitio web, proporcionando organizacion logica sobre el dominio principal, y todas las paginas web que pertenecen a el

# WebFolder
Esta clase proporciona una representacion sobre una carpeta (folder) en un sitio web, el cual es un recurso destinado meramente para proporcionar estructura y organizacion a sus paginas web

# WebPage
Esta clase proporciona una representacion sobre una pagina web, perteneciente a un sitio web, incluyendo todos los metodos y propiedades generales, pero tambien permitiendo la extension de la clase para cubrir las funciones y datos particulares de cada pagina web