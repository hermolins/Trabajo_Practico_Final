import json
import os
import uuid
from typing import List, Optional, Dict, Any


class Mensaje:
    def __init__(self, remitente: str, destinatario: str, asunto: str, cuerpo: str, id: Optional[str] = None):
        self.id = id or uuid.uuid4().hex
        self.remitente = remitente
        self.destinatario = destinatario
        self.asunto = asunto
        self.cuerpo = cuerpo

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "remitente": self.remitente,
            "destinatario": self.destinatario,
            "asunto": self.asunto,
            "cuerpo": self.cuerpo,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Mensaje':
        return Mensaje(d.get('remitente', ''), d.get('destinatario', ''), d.get('asunto', ''), d.get('cuerpo', ''), id=d.get('id'))


class Carpeta:
    def __init__(self, nombre: str, id: Optional[str] = None):
        self.id = id or uuid.uuid4().hex
        self.nombre = nombre
        self.hijos: List[Carpeta] = []
        self.mensajes: List[str] = []  # almacena ids de mensajes

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "hijos": [h.to_dict() for h in self.hijos],
            "mensajes": list(self.mensajes),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Carpeta':
        c = Carpeta(d.get('nombre', ''), id=d.get('id'))
        c.hijos = [Carpeta.from_dict(h) for h in d.get('hijos', [])]
        c.mensajes = list(d.get('mensajes', []))
        return c

    # Recursivo: busca carpeta por id
    def buscar_por_id(self, id_buscar: str) -> Optional['Carpeta']:
        if self.id == id_buscar:
            return self
        for hijo in self.hijos:
            encontrado = hijo.buscar_por_id(id_buscar)
            if encontrado:
                return encontrado
        return None

    # Recursivo: buscar carpeta por nombre (primera coincidencia)
    def buscar_por_nombre(self, nombre_buscar: str) -> Optional['Carpeta']:
        if self.nombre == nombre_buscar:
            return self
        for hijo in self.hijos:
            encontrado = hijo.buscar_por_nombre(nombre_buscar)
            if encontrado:
                return encontrado
        return None


class Almacen:
    def __init__(self, path: str = 'data.json'):
        self.path = path
        self.mensajes: Dict[str, Mensaje] = {}
        self.raiz: Carpeta = Carpeta('Inbox')
        self._cargar()

    def _cargar(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # mensajes
                self.mensajes = {m['id']: Mensaje.from_dict(m) for m in data.get('mensajes', [])}
                # carpeta raiz
                if 'carpeta_raiz' in data:
                    self.raiz = Carpeta.from_dict(data['carpeta_raiz'])
            except Exception:
                # si falla la carga, inicializar con valores por defecto
                self.mensajes = {}
                self.raiz = Carpeta('Inbox')

    def guardar(self):
        data = {
            'mensajes': [m.to_dict() for m in self.mensajes.values()],
            'carpeta_raiz': self.raiz.to_dict()
        }
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def agregar_mensaje(self, mensaje: Mensaje, carpeta_id: Optional[str] = None):
        self.mensajes[mensaje.id] = mensaje
        carpeta = self.raiz if carpeta_id is None else self.raiz.buscar_por_id(carpeta_id)
        if carpeta is None:
            carpeta = self.raiz
        carpeta.mensajes.append(mensaje.id)
        self.guardar()

    def mover_mensaje(self, mensaje_id: str, carpeta_destino_id: str) -> bool:
        # eliminar de donde esté y añadir a destino
        encontrado = self._remover_mensaje_de_carpeta(self.raiz, mensaje_id)
        destino = self.raiz.buscar_por_id(carpeta_destino_id)
        if destino and encontrado:
            destino.mensajes.append(mensaje_id)
            self.guardar()
            return True
        return False

    def _remover_mensaje_de_carpeta(self, carpeta: Carpeta, mensaje_id: str) -> bool:
        if mensaje_id in carpeta.mensajes:
            carpeta.mensajes.remove(mensaje_id)
            return True
        for hijo in carpeta.hijos:
            if self._remover_mensaje_de_carpeta(hijo, mensaje_id):
                return True
        return False

    # Devuelve la carpeta que contiene el mensaje (o None)
    def carpeta_de_mensaje(self, mensaje_id: str) -> Optional[Carpeta]:
        def dfs(carpeta: Carpeta) -> Optional[Carpeta]:
            if mensaje_id in carpeta.mensajes:
                return carpeta
            for hijo in carpeta.hijos:
                r = dfs(hijo)
                if r:
                    return r
            return None
        return dfs(self.raiz)

    # Lista plana de carpetas con ruta legible: [{'id':..., 'ruta': 'Inbox/Proy'}]
    def listar_carpetas_con_ruta(self) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        def dfs(carpeta: Carpeta, ruta: List[str]):
            out.append({'id': carpeta.id, 'ruta': '/'.join(ruta + [carpeta.nombre])})
            for hijo in carpeta.hijos:
                dfs(hijo, ruta + [carpeta.nombre])
        dfs(self.raiz, [])
        return out

    # Búsqueda recursiva por asunto o remitente
    def buscar_mensajes(self, termino: str) -> List[Dict[str, Any]]:
        resultado: List[Dict[str, Any]] = []

        def dfs(carpeta: Carpeta, ruta: List[str]):
            for mid in carpeta.mensajes:
                m = self.mensajes.get(mid)
                if not m:
                    continue
                if termino.lower() in (m.asunto or '').lower() or termino.lower() in (m.remitente or '').lower():
                    resultado.append({
                        'mensaje': m.to_dict(),
                        'ruta': '/'.join(ruta + [carpeta.nombre])
                    })
            for hijo in carpeta.hijos:
                dfs(hijo, ruta + [carpeta.nombre])

        dfs(self.raiz, [])
        return resultado
