import json
import uuid
from typing import Dict, List, Set, Optional, Any
from pathlib import Path


class Servidor:
    def __init__(self, nombre: str, id: Optional[str] = None):
        self.id = id or uuid.uuid4().hex
        self.nombre = nombre

    def to_dict(self) -> Dict[str, str]:
        return {"id": self.id, "nombre": self.nombre}

    @staticmethod
    def from_dict(d: Dict[str, str]) -> 'Servidor':
        return Servidor(d.get('nombre', ''), id=d.get('id'))


class ServidorNetwork:
    """Grafo simple (lista de adyacencia) para modelar servidores de correo.

    Persistencia opcional a JSON.
    """
    def __init__(self, path: str = 'servers.json'):
        self.path = Path(path)
        self.nodes: Dict[str, Servidor] = {}
        self.adj: Dict[str, Set[str]] = {}
        self._load()

    def _load(self):
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text(encoding='utf-8'))
                for n in data.get('nodes', []):
                    s = Servidor.from_dict(n)
                    self.nodes[s.id] = s
                for a, bs in data.get('adj', {}).items():
                    self.adj[a] = set(bs)
            except Exception:
                self.nodes = {}
                self.adj = {}

    def _save(self):
        data = {
            'nodes': [n.to_dict() for n in self.nodes.values()],
            'adj': {k: list(v) for k, v in self.adj.items()}
        }
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    def add_server(self, nombre: str) -> Servidor:
        s = Servidor(nombre)
        self.nodes[s.id] = s
        self.adj.setdefault(s.id, set())
        self._save()
        return s

    def add_connection(self, id_a: str, id_b: str, directed: bool = False) -> bool:
        if id_a not in self.nodes or id_b not in self.nodes:
            return False
        self.adj.setdefault(id_a, set()).add(id_b)
        if not directed:
            self.adj.setdefault(id_b, set()).add(id_a)
        self._save()
        return True

    def list_servers(self) -> List[Dict[str, str]]:
        return [n.to_dict() for n in self.nodes.values()]

    def list_connections(self) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        for a, bs in self.adj.items():
            for b in bs:
                out.append({'from': a, 'to': b})
        return out

    def bfs_path(self, start: str, goal: str) -> List[str]:
        if start not in self.nodes or goal not in self.nodes:
            return []
        from collections import deque
        q = deque([start])
        prev: Dict[str, Optional[str]] = {start: None}
        while q:
            u = q.popleft()
            if u == goal:
                break
            for v in self.adj.get(u, []):
                if v not in prev:
                    prev[v] = u
                    q.append(v)
        if goal not in prev:
            return []
        # reconstruir camino
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = prev.get(cur)
        path.reverse()
        return path

    def dfs_path(self, start: str, goal: str) -> List[str]:
        if start not in self.nodes or goal not in self.nodes:
            return []
        visited: Set[str] = set()
        parent: Dict[str, Optional[str]] = {start: None}

        def dfs(u: str) -> bool:
            if u == goal:
                return True
            visited.add(u)
            for v in self.adj.get(u, []):
                if v in visited:
                    continue
                parent[v] = u
                if dfs(v):
                    return True
            return False

        found = dfs(start)
        if not found:
            return []
        path = []
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()
        return path

    def simulate_send(self, origen: str, destino: str, algoritmo: str = 'bfs') -> Dict[str, Any]:
        if algoritmo == 'dfs':
            path = self.dfs_path(origen, destino)
        else:
            path = self.bfs_path(origen, destino)
        named_path = [self.nodes[n].nombre for n in path] if path else []
        return {'ok': bool(path), 'path_ids': path, 'path_names': named_path, 'hops': len(path) - 1 if path else None}
