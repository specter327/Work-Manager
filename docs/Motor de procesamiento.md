=====
Proceso de linea

Se podria ver al proceso de elaboracion de un mensaje como un proceso de linea de ensamblaje. Donde el producto
inicial se transporta sobre una cinta recta, donde multiples elementos intervienen manipulandolo y cambiando
su forma a su propia manera. Hasta que, al final de la cinta se obtiene un producto procesado y compuesto de
multiples elementos

Datos de ingreso:
- Perfil de contacto
- Perfil de agente
- Producto actual (mensaje, horario de envio)

Datos de egreso:
- Producto resultado

==========
Funciones interventoras

=====
Intervencion de funciones:
Cada funcion interventora, tendra acceso durante su ejecucion a datos de ingreso:
Perfil de contacto
Plantillas de mensaje
Resultados previos (entregados por la funcion interventora que se ejecuto anteriormente. Incluye el mensaje actual)
Otra informacion (perfil de agente, entre otros)

=====
Estructura de funciones. Orden de ejecucion:
Se utilizara una estructura de funciones ordenada por valor de prioridad (valor decimal del: 0 (minimo), al 100 (maximo)), en un par: valor-funcion

Ejemplo:
{
    100:funcionInterventora2,
    90:funcionInterventora1,
    40:funcionInterventora3
}

Donde se dara ejecucion en el orden siguiente (de mayor a menor):
1. Funcion interventora 2
2. Funcion interventora 1
3. Funcion interventora 3


==========
Importado

El motor de gestion es un elemento el cual recibe como datos de ingreso (entrada) la informacion de un cliente.
Esta informacion cumple con un perfil como:
7199339	SAMANIEGO AMEZCUA ERNESTO	8110811866	crazysloth222@gmail.com	Hombre	1130老客还款未用信Renovación_2025-12-02 08:20:32	还款未用信-T1	RNL-T1	无产品	FacilDinero	TSO2512021650090038666442		20/11/2025	6 Plazo			https://admin.oa.wowcredito.com/tele-sale/userInfo?uid=7199339	5000	2200	1/12/2025	FALSO	0	FALSO	2/12/2025	vincen1@mxg		FALSO		1

Con esta informacion, se comienza a procesar en una cadena de intervenciones para finalmente entregar una instruccion final.
Entre este proceso de procesamiento de datos, existen varios elementos que influyen en la elaboracion de mensajes para el cliente:

1. Tipo de cartera de cliente

Dependiendo del tipo de cartera de cliente:
- Cliente nuevo
- Cliente nuevo vencido
- Renovacion
- Renovacion vencida
- Renovacion con limite de credito
- Etcetera

Es el tipo de plantilla de mensaje a utilizar

2. Dia de asignación

Dependiendo del dia de atención al cliente:
- Dia 1. Primer dia asignado (atencion activa)
- Dia 2. Segundo dia asignado (atencion pasiva)

Sera el tipo de mensaje a enviar (ademas, se podria considerar un flujo de mensajes secuencial. Tambien habria que considerar en que parte de dicho flujo estariamos)

3. Estado del credito

Dependiendo del estado actual del credito:
- Crédito aprobado
- Registro sin crédito
- En proceso de revisión
- Etcetera

4. Tiempo de registro

Dependiendo de la fecha en que se registro el cliente.
- Menor a 1 semana
- Mayor a 1 semana
- Mayor a 1 mes
- Mayor a 6 meses
- Mayor a 1 año

5. Monto del crédito

Dependiendo del monto del crédito: (depende de la cartera)
- Alto: 
    - Cliente nuevo: Mayor a $4,000
- Medio: 
    - Cliente nuevo: Mayor a $2,000
- Bajo: 
    - Cliente nuevo: Menor a $2,000

6. Limite de credito:

Dependiendo de:
- Hubo aumento de limite: Se personaliza el mensaje
- No hubo aumento de limite: No se personaliza el mensaje

7. Credito disponible:

Dependiendo del porcentaje de credito disponible:
- 100%: Totalidad del credito disponible
- 60&: Mas de la mitad del credito disponible
- <60%: Menos de la mitad del credito disponible

8. Ofertas disponiubleS:

Dependiendo de si existen ofertas disponibles:
- Hay cupon(es) de descuento(s)
- No hay cupon de descuento

9. Genero:

Dependiendo del genero del cliente:
- Hombre
- Mujer

Se personalizara diferente el mensaje

10. Estado del credito

Dependiendo de:
- Si el credito ha sido cobrado (en su totalidad, o parcial)
- Si el credito no ha sido cobrado

Dependiendo de estos factores interventores, se elaborara y modificara el mensaje a enviar a dicho cliente, con la finalidad de elaborar un texto adecuado a la situacion del mismo. Esta descripcion no considera:

- Horarios: Distintos horarios al dia son mas adecuados para enviar mensajes
- Secuencialidad: Distintos mensajes al dia son diferentes variando el dia de gestion y orden