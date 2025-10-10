# Universidad Nacional
# Almirante Brown

# Trabajo Práctico Final - Estructura de Datos

Integrantes del grupo:
• Julian Fernández - julianfernandez197612@gmail.com
• Mateo Danilo Gerez - titi04gerez@gmail.com
• Adrian Eduardo Her Molins - hermolins@gmail.com

Materia: Estructura de Datos
Profesor: Bianco, Angel Leonardo
Fecha: Octubre 2025


Informe de Avance - TP Cliente de Correo
Este documento detalla el progreso del desarrollo de nuestro Cliente de Correo Electrónico para la cátedra de Estructuras de Datos. Como equipo, hemos adoptado una metodología de trabajo incremental, con reuniones semanales para discutir y evaluar las distintas alternativas de implementación, asegurando una base sólida y escalable para el proyecto.

Primera Entrega: 
Cimientos del Proyecto - Modelo de Clases
En la primera etapa, nos enfocamos en construir el núcleo del sistema. El objetivo fue definir las clases principales (Usuario, Mensaje, Carpeta) y establecer una arquitectura orientada a objetos que sirviera como pilar para las funcionalidades futuras.

Durante esta fase, se implementó un sistema funcional de registro y autenticación de usuarios y se desarrolló la capacidad básica para enviar y recibir mensajes.

Segunda entrega: 
Estructura de Carpetas: Un Árbol Recursivo
Para esta segunda fase, el desafío principal fue organizar los mensajes de manera jerárquica y eficiente. Tras evaluar diferentes enfoques, decidimos implementar el sistema de carpetas y subcarpetas utilizando una estructura de datos de Árbol General, ya que modela de forma natural la relación padre-hijo que existe en un sistema de directorios.

1. El Diseño: La Clase Carpeta como Nodo del Árbol

El nodo central de nuestro árbol es la clase Carpeta. Cada instancia de esta clase tiene la capacidad de contener tanto una colección de mensajes como una lista de otras instancias de Carpeta, definiendo así la estructura recursiva fundamental de nuestro sistema.


class Carpeta:
    def __init__(self, nombre):
        self.nombre = nombre
        self.mensajes = []       # Lista de objetos Mensaje
        self.subcarpetas = []    # Lista de objetos Carpeta (hijos)

Decisión de Diseño: Optamos por usar listas de Python para almacenar los mensajes y las subcarpetas. Esta elección se basa en la flexibilidad y eficiencia que ofrecen para las operaciones de inserción, eliminación y recorrido, que son fundamentales para la manipulación de la estructura del árbol.

2. Recursividad en Acción: Búsqueda Profunda

La principal ventaja de nuestra estructura de árbol se manifiesta en las operaciones que deben recorrer toda la jerarquía de carpetas. Hemos implementado una función de búsqueda recursiva que permite encontrar correos por remitente o asunto a través de todas las carpetas y subcarpetas de un usuario de manera intuitiva y potente.

¿Cómo funciona?

Caso Base: La función revisa la lista de mensajes de la carpeta actual. Si encuentra un mensaje que coincide con el criterio de búsqueda, lo agrega a la lista de resultados.

Paso Recursivo: La función se invoca a sí misma para cada una de las subcarpetas contenidas en la carpeta actual. De esta manera, explora sistemáticamente todas las ramas del árbol hasta encontrar todas las coincidencias posibles.

3. Funcionalidades Clave Implementadas

Creación de Carpetas y Subcarpetas: Los usuarios tienen la capacidad de crear nuevas carpetas en el nivel raíz ("Bandeja de entrada", "Enviados", etc.) o anidarlas dentro de otras existentes para una organización personalizada.

Movimiento de Mensajes: Se desarrolló la lógica necesaria para mover objetos Mensaje entre cualquier par de carpetas, actualizando de forma atómica las listas de mensajes de las carpetas de origen y destino.

Búsqueda Recursiva: Implementamos un buscador que recorre toda la estructura de directorios del usuario para encontrar correos por asunto o remitente.

Visualización Jerárquica: El sistema es capaz de mostrar la estructura completa de carpetas, reflejando visualmente las relaciones de anidamiento, tal como se detalla en nuestro diseño en docs/arbol_carpetas.md.

4. Análisis de Eficiencia (Big O)

Como parte de la entrega, hemos analizado la complejidad computacional de las operaciones clave implementadas:

Búsqueda Recursiva: La complejidad es O(C+M), donde C es el número total de carpetas y M es el número total de mensajes en la cuenta. En el peor de los casos, el algoritmo debe visitar cada carpeta y revisar cada mensaje una vez.

Mover Mensaje: Asumiendo que ya tenemos las referencias a las carpetas de origen y destino, esta operación tiene una complejidad de O(1), ya que solo implica operaciones de append y remove en listas de Python.

Próximos Pasos: Hacia la Tercera Entrega
Con la estructura de datos principal ya consolidada, nuestro siguiente objetivo es abordar las funcionalidades avanzadas del cliente de correo. El enfoque para la próxima entrega estará en:

Filtros automáticos: Desarrollar algoritmos para clasificar correos entrantes.

Cola de prioridad: Implementar un sistema para gestionar mensajes marcados como "urgentes".

Red de Servidores: Modelar la comunicación entre servidores utilizando grafos.