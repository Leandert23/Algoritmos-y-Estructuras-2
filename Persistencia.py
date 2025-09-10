# Persistencia.py
"""
Módulo para guardar y cargar la configuración de la red en formato JSON.
Incluye serialización de las estructuras de datos AVL, B-Tree, Trie y Cola de errores.
"""
import json
from Red import Red
from Dispositivos import Interfaz
from Errores import RegistroErrores
from Arboles import AVLTree, BTree, Trie

# Codificador/decodificador personalizado para objetos complejos
class RedEncoder(json.JSONEncoder):
    """Codificador personalizado para serializar objetos de la Red en JSON."""
    def default(self, obj):
        if isinstance(obj, Red):
            return {
                "__class__": "Red",
                "dispositivos": {k: self.default(v) for k, v in obj.dispositivos.items()},
                "estadisticas": obj.estadisticas,
                "b_tree_snapshots": self.default(obj.b_tree_snapshots)
            }
        elif isinstance(obj, BTree):
            return {
                "__class__": "BTree",
                "t": obj.t,
                "altura": obj.altura,
                "nodos": obj.nodos,
                "splits": obj.splits,
                "merges": obj.merges,
                "raiz": self._serializar_btree_nodo(obj.raiz)
            }
        elif isinstance(obj, Trie):
            return {
                "__class__": "Trie",
                "raiz": self._serializar_trie_nodo(obj.raiz)
            }
        elif isinstance(obj, AVLTree):
            return {
                "__class__": "AVLTree",
                "nodos": obj.nodos,
                "altura": obj._altura(obj.raiz),
                "rotaciones": obj.obtener_stats()["rotaciones"],
                "raiz": self._serializar_avl_nodo(obj.raiz)
            }
        elif isinstance(obj, dict) or isinstance(obj, list) or isinstance(obj, str) or isinstance(obj, int) or isinstance(obj, bool):
            return obj
        return super().default(obj)
    
    def _serializar_btree_nodo(self, nodo):
        if not nodo:
            return None
        return {
            "claves": [list(k) if isinstance(k, tuple) else k for k in nodo.claves],
            "valores": nodo.valores,
            "hoja": nodo.hoja,
            "hijos": [self._serializar_btree_nodo(h) for h in nodo.hijos]
        }
    
    def _serializar_trie_nodo(self, nodo):
        if not nodo:
            return None
        return {
            "es_fin_prefijo": nodo.es_fin_prefijo,
            "politicas": nodo.politicas,
            "hijos": {bit: self._serializar_trie_nodo(hijo) for bit, hijo in nodo.hijos.items()}
        }
    
    def _serializar_avl_nodo(self, nodo):
        if not nodo:
            return None
        return {
            "prefix": nodo.prefix,
            "mask": nodo.mask,
            "next_hop": nodo.next_hop,
            "metric": nodo.metric,
            "altura": nodo.altura,
            "izquierda": self._serializar_avl_nodo(nodo.izquierda),
            "derecha": self._serializar_avl_nodo(nodo.derecha)
        }

class RedDecoder(json.JSONDecoder):
    """Decodificador personalizado para deserializar JSON a objetos de la Red."""
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)
    
    def object_hook(self, dct):
        if "__class__" in dct:
            if dct["__class__"] == "Red":
                red = Red()
                red.dispositivos = {k: self.object_hook(v) for k, v in dct["dispositivos"].items()}
                red.estadisticas = dct["estadisticas"]
                # Restaurar B-Tree (simplificado)
                red.b_tree_snapshots = BTree(dct["b_tree_snapshots"]["t"])
                self._restaurar_btree_nodo(red.b_tree_snapshots.raiz, dct["b_tree_snapshots"]["raiz"])
                return red
            elif dct["__class__"] == "BTree":
                btree = BTree(dct["t"])
                btree.altura = dct["altura"]
                btree.nodos = dct["nodos"]
                btree.splits = dct["splits"]
                btree.merges = dct["merges"]
                btree.raiz = self._restaurar_btree_nodo(None, dct["raiz"])
                return btree
            elif dct["__class__"] == "Trie":
                trie = Trie()
                trie.raiz = self._restaurar_trie_nodo(None, dct["raiz"])
                return trie
            elif dct["__class__"] == "AVLTree":
                avl = AVLTree()
                avl.nodos = dct["nodos"]
                avl.raiz = self._restaurar_avl_nodo(None, dct["raiz"])
                return avl
        return dct
    
    def _restaurar_btree_nodo(self, padre, dct):
        if not dct:
            return None
        # Restauración simplificada; no reconstruye la estructura completa de B-Tree
        from Arboles import NodoBTree
        nodo = NodoBTree(padre.t if padre else 2, dct["hoja"])
        nodo.claves = [tuple(k) if isinstance(k, list) else k for k in dct["claves"]]
        nodo.valores = dct["valores"]
        nodo.hijos = [self._restaurar_btree_nodo(nodo, h) for h in dct["hijos"]]
        return nodo
    
    def _restaurar_trie_nodo(self, padre, dct):
        if not dct:
            return None
        from Arboles import NodoTrie
        nodo = NodoTrie()
        nodo.es_fin_prefijo = dct["es_fin_prefijo"]
        nodo.politicas = dct["politicas"]
        nodo.hijos = {bit: self._restaurar_trie_nodo(nodo, hijo) for bit, hijo in dct["hijos"].items()}
        return nodo
    
    def _restaurar_avl_nodo(self, padre, dct):
        if not dct:
            return None
        from Arboles import NodoAVL
        nodo = NodoAVL(dct["prefix"], dct["mask"], dct["next_hop"], dct["metric"])
        nodo.altura = dct["altura"]
        nodo.izquierda = self._restaurar_avl_nodo(nodo, dct["izquierda"])
        nodo.derecha = self._restaurar_avl_nodo(nodo, dct["derecha"])
        return nodo

def guardar_configuracion(red, archivo="red_config.json"):
    """
    Guarda la configuración completa de la red a un archivo JSON.
    Args:
        red: Instancia de la clase Red.
        archivo: Nombre del archivo de salida.
    """
    try:
        with open(archivo, "w") as f:
            json.dump(red, f, cls=RedEncoder, indent=4)
        print(f"[OK] Configuración guardada en '{archivo}'.")
    except Exception as e:
        print(f"[ERROR] No se pudo guardar la configuración: {e}")

def cargar_configuracion(archivo="red_config.json"):
    """
    Carga la configuración completa de la red desde un archivo JSON.
    Args:
        archivo: Nombre del archivo de entrada.
    Returns:
        Instancia de la clase Red o None si falla.
    """
    try:
        with open(archivo, "r") as f:
            data = json.load(f, cls=RedDecoder)
        print(f"[OK] Configuración cargada desde '{archivo}'.")
        return data
    except FileNotFoundError:
        print(f"[ERROR] Archivo '{archivo}' no encontrado.")
        return None
    except Exception as e:
        print(f"[ERROR] No se pudo cargar la configuración: {e}")
        return None

# Funciones de ejemplo para uso en la CLI
def guardar_red_actual(red):
    """Función para guardar la red actual vía CLI."""
    guardar_configuracion(red)

def cargar_red_guardada():
    """Función para cargar una red guardada vía CLI."""
    return cargar_configuracion()