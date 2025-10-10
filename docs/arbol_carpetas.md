# Árbol de carpetas (estructura)

Este documento explica la estructura de carpetas utilizada para este proyecto(se irá completando con el paso de las entregas).

- Carpeta
  - id: identificador único (uuid)
  - nombre: nombre de la carpeta
  - hijos: lista de subcarpetas (recursiva)
  - mensajes: lista de ids de mensajes almacenados en la carpeta

Ejemplo simple:

Inbox
├─ Proyecto
│  ├─ Personal
│  └─ Trabajo
└─ Archivados

Búsquedas
- Se usa DFS recursivo a partir de la `carpeta_raiz`.
- Complejidad: O(N + M) en peor caso (N = número de carpetas, M = número de mensajes).

Mover mensaje
- Operación: remover id del array `mensajes` en la carpeta origen y agregarlo en la carpeta destino.
- Si se mantiene un índice id->carpeta, la operación puede ser O(1) para localizar carpeta destino; en la implementación actual se busca recursivamente la carpeta destino (O(depth)).

Persistencia
- La estructura se persiste en `data.json` con dos secciones: `mensajes` y `carpeta_raiz`.