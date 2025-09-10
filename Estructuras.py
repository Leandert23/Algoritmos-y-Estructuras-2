# Estructuras.py

class NodoLista:
    """Representa un nodo en una lista enlazada."""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None

class ListaEnlazada:
    """Implementación básica de una lista enlazada."""
    def __init__(self):
        self.cabeza = None
        self.longitud = 0

    def agregar(self, dato):
        """Agrega un nuevo nodo al final de la lista."""
        nuevo = NodoLista(dato)
        if not self.cabeza:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self.longitud += 1

    def __iter__(self):
        """Permite iterar sobre los elementos de la lista."""
        actual = self.cabeza
        while actual:
            yield actual.dato
            actual = actual.siguiente

    def esta_vacia(self):
        """Verifica si la lista está vacía."""
        return self.cabeza is None

    def obtener_por_indice(self, indice):
        """Obtiene el dato de un nodo por su índice."""
        if indice < 0 or indice >= self.longitud:
            return None
        actual = self.cabeza
        for _ in range(indice):
            actual = actual.siguiente
        return actual.dato

class Cola:
    """
    Implementación de una cola (FIFO).
    Para simplificar, usa una lista de Python internamente.
    Para una implementación estricta con lista enlazada, se usaría NodoLista.
    """
    def __init__(self):
        self.items = []
    
    def encolar(self, item):
        """Añade un elemento al final de la cola."""
        self.items.append(item)
    
    def desencolar(self):
        """Elimina y retorna el elemento del frente de la cola."""
        if not self.esta_vacia():
            return self.items.pop(0)
        return None
    
    def esta_vacia(self):
        """Verifica si la cola está vacía."""
        return len(self.items) == 0
    
    def tamano(self):
        """Retorna el número de elementos en la cola."""
        return len(self.items)

    def peek(self):
        """Retorna el elemento del frente sin eliminarlo."""
        return self.items[0] if not self.esta_vacia() else None

class Pila:
    """Implementación de una pila (LIFO)."""
    def __init__(self):
        self.items = []
    
    def apilar(self, item):
        """Añade un elemento a la cima de la pila."""
        self.items.append(item)
    
    def desapilar(self):
        """Elimina y retorna el elemento de la cima de la pila."""
        return self.items.pop() if self.items else None
    
    def esta_vacia(self):
        """Verifica si la pila está vacía."""
        return len(self.items) == 0