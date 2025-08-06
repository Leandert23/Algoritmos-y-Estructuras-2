class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.longitud = 0
    
    def agregar(self, dato):
        nuevo = NodoLista(dato)
        if not self.cabeza:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self.longitud += 1

class Cola:
    def __init__(self):
        self.items = []
    
    def encolar(self, item):
        self.items.append(item)
    
    def desencolar(self):
        return self.items.pop(0) if self.items else None

class Pila:
    def __init__(self):
        self.items = []
    
    def apilar(self, item):
        self.items.append(item)
    
    def desapilar(self):
        return self.items.pop() if self.items else None