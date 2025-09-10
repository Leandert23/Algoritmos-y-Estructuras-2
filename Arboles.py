# --- Módulo 1: AVL Tree para Tabla de Rutas ---
class NodoAVL:
    """Representa un nodo en el árbol AVL para la tabla de rutas."""
    def __init__(self, prefix, mask, next_hop, metric):
        self.prefix = prefix
        self.mask = mask
        self.next_hop = next_hop
        self.metric = metric
        self.izquierda = None
        self.derecha = None
        self.altura = 1 # Altura del nodo en el subárbol
        self.balance = 0 # Factor de balance (altura_izquierda - altura_derecha)

    def __repr__(self):
        """Representación en cadena del nodo AVL."""
        return f"[{self.prefix}/{self.mask} via {self.next_hop} metric {self.metric}]"

class AVLTree:
    """Implementación de un árbol AVL para la tabla de enrutamiento."""
    def __init__(self):
        self.raiz = None
        self.nodos = 0
        # Contadores para fines didácticos
        self.rotaciones_ll = 0
        self.rotaciones_lr = 0
        self.rotaciones_rl = 0
        self.rotaciones_rr = 0

    def _altura(self, nodo):
        """Retorna la altura de un nodo."""
        return nodo.altura if nodo else 0

    def _actualizar_altura_balance(self, nodo):
        """Actualiza la altura y el factor de balance de un nodo."""
        if nodo:
            nodo.altura = 1 + max(self._altura(nodo.izquierda), self._altura(nodo.derecha))
            nodo.balance = self._altura(nodo.izquierda) - self._altura(nodo.derecha)

    # Métodos de rotación
    def _rotacion_derecha(self, z):
        """Realiza una rotación simple a la derecha."""
        y = z.izquierda
        T3 = y.derecha
        y.derecha = z
        z.izquierda = T3
        self._actualizar_altura_balance(z)
        self._actualizar_altura_balance(y)
        return y

    def _rotacion_izquierda(self, z):
        """Realiza una rotación simple a la izquierda."""
        y = z.derecha
        T2 = y.izquierda
        y.izquierda = z
        z.derecha = T2
        self._actualizar_altura_balance(z)
        self._actualizar_altura_balance(y)
        return y

    def _balancear(self, nodo):
        """Balancea el nodo si es necesario aplicando rotaciones."""
        self._actualizar_altura_balance(nodo)
        balance = nodo.balance

        # Caso LL (Left-Left)
        if balance > 1 and nodo.izquierda and nodo.izquierda.balance >= 0:
            self.rotaciones_ll += 1
            return self._rotacion_derecha(nodo)
        # Caso LR (Left-Right)
        if balance > 1 and nodo.izquierda and nodo.izquierda.balance < 0:
            self.rotaciones_lr += 1
            nodo.izquierda = self._rotacion_izquierda(nodo.izquierda)
            return self._rotacion_derecha(nodo)
        # Caso RR (Right-Right)
        if balance < -1 and nodo.derecha and nodo.derecha.balance <= 0:
            self.rotaciones_rr += 1
            return self._rotacion_izquierda(nodo)
        # Caso RL (Right-Left)
        if balance < -1 and nodo.derecha and nodo.derecha.balance > 0:
            self.rotaciones_rl += 1
            nodo.derecha = self._rotacion_derecha(nodo.derecha)
            return self._rotacion_izquierda(nodo)
        return nodo

    def insertar(self, prefix, mask, next_hop, metric):
        """Inserta una nueva ruta en el AVL."""
        def _insertar(nodo, prefix, mask, next_hop, metric):
            if not nodo:
                self.nodos += 1
                return NodoAVL(prefix, mask, next_hop, metric)
            
            # Comparación principal por prefijo, secundaria por métrica
            # NOTA: La comparación de prefijos IP es más compleja que una simple < o >.
            # Para una implementación real, se necesitaría una función de comparación de IP/máscara.
            # Aquí se usa una comparación lexicográfica simple para el esqueleto.
            if prefix < nodo.prefix:
                nodo.izquierda = _insertar(nodo.izquierda, prefix, mask, next_hop, metric)
            elif prefix > nodo.prefix:
                nodo.derecha = _insertar(nodo.derecha, prefix, mask, next_hop, metric)
            else: # Prefijos iguales, comparar por métrica
                if metric < nodo.metric:
                    nodo.izquierda = _insertar(nodo.izquierda, prefix, mask, next_hop, metric)
                elif metric > nodo.metric:
                    nodo.derecha = _insertar(nodo.derecha, prefix, mask, next_hop, metric)
                else:
                    # Si prefijo y métrica son iguales, se considera un duplicado o actualización.
                    # Para este simulador, asumimos que no se insertan duplicados exactos.
                    return nodo 

            return self._balancear(nodo)

        self.raiz = _insertar(self.raiz, prefix, mask, next_hop, metric)

    def eliminar(self, prefix, mask):
        """Elimina una ruta del AVL."""
        def _eliminar(nodo, prefix, mask):
            if not nodo:
                return nodo

            # Buscar el nodo a eliminar
            if prefix < nodo.prefix:
                nodo.izquierda = _eliminar(nodo.izquierda, prefix, mask)
            elif prefix > nodo.prefix:
                nodo.derecha = _eliminar(nodo.derecha, prefix, mask)
            else: # Prefijo encontrado
                if mask != nodo.mask:
                    # Si el prefijo coincide pero la máscara no, no es el nodo exacto.
                    # En un sistema real, podría haber múltiples entradas para el mismo prefijo con diferentes máscaras.
                    return nodo 

                # Nodo con un solo hijo o sin hijos
                if not nodo.izquierda:
                    temp = nodo.derecha
                    self.nodos -= 1
                    return temp
                elif not nodo.derecha:
                    temp = nodo.izquierda
                    self.nodos -= 1
                    return temp

                # Nodo con dos hijos: obtener el sucesor inorden (el más pequeño en el subárbol derecho)
                temp = self._get_min_value_node(nodo.derecha)
                nodo.prefix = temp.prefix
                nodo.mask = temp.mask
                nodo.next_hop = temp.next_hop
                nodo.metric = temp.metric
                nodo.derecha = _eliminar(nodo.derecha, temp.prefix, temp.mask) # Eliminar el sucesor inorden
            
            if not nodo: # Si el árbol se vació después de la eliminación
                return nodo

            return self._balancear(nodo)

        self.raiz = _eliminar(self.raiz, prefix, mask)

    def _get_min_value_node(self, nodo):
        """Encuentra el nodo con el valor mínimo en un subárbol."""
        if nodo is None or nodo.izquierda is None:
            return nodo
        return self._get_min_value_node(nodo.izquierda)

    def buscar(self, dest_ip):
        """
        Busca la mejor ruta (longest-prefix match simplificado) para una IP de destino.
        NOTA: Un AVL no es la estructura más eficiente para Longest-Prefix Match (LPM) real.
        Un Trie (Módulo 3) es mucho más adecuado para LPM.
        Aquí, la búsqueda es una búsqueda binaria estándar por la clave del nodo.
        Para simular LPM con AVL, se necesitaría iterar sobre todas las rutas que coinciden
        y seleccionar la más específica (mayor longitud de máscara) o con mejor métrica.
        Esta implementación es una búsqueda binaria simple por prefijo.
        """
        # Implementación simplificada: busca una ruta que contenga la IP de destino.
        # Esto no es un LPM real, sino una búsqueda de coincidencia.
        # Para LPM, se debería recorrer el árbol y encontrar la coincidencia más larga.
        # Se devuelve el primer nodo que "coincida" (simplificado).
        
        # Placeholder para la lógica de búsqueda de ruta.
        # En un escenario real, se necesitaría una función para comparar si una IP
        # cae dentro de un prefijo/máscara.
        
        # Ejemplo muy simplificado:
        def _buscar(nodo, ip):
            if not nodo:
                return None
            
            # Lógica de comparación de IP con prefijo del nodo
            # Esto es una simplificación. Debería ser una función de utilidad de red.
            # Por ejemplo, si ip_en_rango(ip, nodo.prefix, nodo.mask):
            # return nodo
            
            # Si no hay coincidencia directa, se podría buscar en subárboles
            # basándose en la estructura del AVL (prefijo < o >).
            # Para LPM, se buscaría en ambos lados y se elegiría la mejor coincidencia.
            
            # Para este esqueleto, solo se devuelve la raíz si existe.
            # La implementación real de LPM es compleja.
            return nodo # Retorna la raíz como un placeholder de "ruta encontrada"

        return _buscar(self.raiz, dest_ip)


    def obtener_stats(self):
        """Retorna estadísticas del árbol AVL."""
        return {
            "nodos": self.nodos,
            "altura": self._altura(self.raiz),
            "rotaciones": {
                "LL": self.rotaciones_ll,
                "LR": self.rotaciones_lr,
                "RL": self.rotaciones_rl,
                "RR": self.rotaciones_rr
            }
        }

    def imprimir_arbol_ascii(self):
        """Imprime el árbol AVL en formato ASCII (simplificado)."""
        def _print_tree(node, indent="", last='updown'):
            if node:
                print(indent, end="")
                if last == 'updown':
                    print("---", end="")
                    indent += "   "
                elif last == 'right':
                    print(" /--", end="")
                    indent += "|  "
                elif last == 'left':
                    print(" \\--", end="")
                    indent += "   "
                print(f"[{node.prefix}/{node.mask}]")
                _print_tree(node.izquierda, indent, 'right')
                _print_tree(node.derecha, indent, 'left')

        _print_tree(self.raiz)


# --- Módulo 2: B-Tree para Índice de Configuraciones ---
class NodoBTree:
    """Representa un nodo en un B-Tree."""
    def __init__(self, t, hoja=True):
        self.t = t  # Grado mínimo (define el número máximo de claves y hijos)
        self.claves = [] # Lista de claves (ej. timestamps o nombres)
        self.valores = [] # Lista de valores asociados a las claves (ej. punteros a archivos)
        self.hijos = []  # Lista de nodos hijos
        self.hoja = hoja # True si es un nodo hoja, False si es interno

class BTree:
    """Implementación de un B-Tree para indexar snapshots de configuración."""
    def __init__(self, t):
        self.raiz = NodoBTree(t, True)
        self.t = t # Grado mínimo
        self.altura = 1
        self.nodos = 1 # Contar la raíz
        self.splits = 0
        self.merges = 0

    def insertar(self, key, value):
        """Inserta una clave-valor en el B-Tree."""
        # Lógica de inserción en B-Tree, incluyendo splits.
        # Esta es una implementación compleja y se deja como un placeholder.
        # Si la raíz se divide, la altura del árbol aumenta.
        r = self.raiz
        if len(r.claves) == (2 * self.t) - 1: # La raíz está llena, necesita split
            s = NodoBTree(self.t, hoja=False)
            s.hijos.insert(0, r)
            self.raiz = s
            self.nodos += 1
            self.altura += 1
            self._split_hijo(s, 0, r)
            self._insertar_no_lleno(s, key, value)
        else:
            self._insertar_no_lleno(r, key, value)

    def _insertar_no_lleno(self, nodo, key, value):
        """Inserta en un nodo que no está lleno."""
        i = len(nodo.claves) - 1
        if nodo.hoja:
            nodo.claves.append(None) # Espacio para la nueva clave
            nodo.valores.append(None) # Espacio para el nuevo valor
            while i >= 0 and key < nodo.claves[i]:
                nodo.claves[i + 1] = nodo.claves[i]
                nodo.valores[i + 1] = nodo.valores[i]
                i -= 1
            nodo.claves[i + 1] = key
            nodo.valores[i + 1] = value
        else:
            while i >= 0 and key < nodo.claves[i]:
                i -= 1
            i += 1
            if len(nodo.hijos[i].claves) == (2 * self.t) - 1: # Hijo está lleno, necesita split
                self._split_hijo(nodo, i, nodo.hijos[i])
                if key > nodo.claves[i]:
                    i += 1
            self._insertar_no_lleno(nodo.hijos[i], key, value)

    def _split_hijo(self, padre, i, hijo):
        """Divide un hijo lleno del nodo padre."""
        self.splits += 1
        z = NodoBTree(self.t, hoja=hijo.hoja)
        self.nodos += 1
        padre.hijos.insert(i + 1, z)
        padre.claves.insert(i, hijo.claves[self.t - 1])
        padre.valores.insert(i, hijo.valores[self.t - 1])

        z.claves = hijo.claves[self.t:]
        z.valores = hijo.valores[self.t:]
        hijo.claves = hijo.claves[:self.t - 1]
        hijo.valores = hijo.valores[:self.t - 1]

        if not hijo.hoja:
            z.hijos = hijo.hijos[self.t:]
            hijo.hijos = hijo.hijos[:self.t]

    def buscar(self, key):
        """Busca una clave en el B-Tree."""
        def _buscar(nodo, key):
            i = 0
            while i < len(nodo.claves) and key > nodo.claves[i]:
                i += 1
            if i < len(nodo.claves) and key == nodo.claves[i]:
                return nodo.valores[i] # Clave encontrada
            if nodo.hoja:
                return None # No encontrado en nodo hoja
            return _buscar(nodo.hijos[i], key)
        
        return _buscar(self.raiz, key)

    def eliminar(self, key):
        """Elimina una clave del B-Tree."""
        # Lógica de eliminación en B-Tree, incluyendo merges.
        # Esta es una implementación compleja y se deja como un placeholder.
        pass

    def recorrer_en_orden(self):
        """Generador para recorrer el B-Tree en orden (claves y valores)."""
        def _recorrer(nodo):
            for i, clave in enumerate(nodo.claves):
                if not nodo.hoja:
                    yield from _recorrer(nodo.hijos[i])
                yield (clave, nodo.valores[i])
            if not nodo.hoja:
                yield from _recorrer(nodo.hijos[len(nodo.claves)])
        
        return list(_recorrer(self.raiz))

    def obtener_stats(self):
        """Retorna estadísticas del B-Tree."""
        return {
            "orden": self.t,
            "altura": self.altura,
            "nodos": self.nodos,
            "splits": self.splits,
            "merges": self.merges
        }


# --- Módulo 3: Trie para Prefijos IP y Políticas ---
class NodoTrie:
    """Representa un nodo en el Trie para prefijos IP."""
    def __init__(self):
        self.hijos = {} # Clave: '0' o '1' para trie binario, o octeto para base-256
        self.es_fin_prefijo = False # True si este nodo marca el final de un prefijo IP
        self.politicas = {} # Diccionario de políticas asociadas a este prefijo (ej. {'ttl-min': N, 'block': True})

class Trie:
    """Implementación de un Trie (árbol n-ario) para prefijos IP y políticas jerárquicas."""
    def __init__(self):
        self.raiz = NodoTrie()

    def _ip_to_binary(self, ip_address, mask_length=32):
        """Convierte una dirección IP a su representación binaria."""
        try:
            octets = list(map(int, ip_address.split('.')))
            if not all(0 <= o <= 255 for o in octets) or len(octets) != 4:
                raise ValueError("Formato de IP inválido.")
            
            binary_ip = ''.join(f'{octet:08b}' for octet in octets)
            return binary_ip[:mask_length]
        except ValueError as e:
            # Manejo de error para IP inválida
            print(f"Error al convertir IP a binario: {e}")
            return None

    def insertar_prefijo(self, prefix_ip, mask_length, politicas=None):
        """Inserta un prefijo IP en el Trie y asocia políticas."""
        bin_prefix = self._ip_to_binary(prefix_ip, mask_length)
        if bin_prefix is None:
            return False # IP o máscara inválida

        actual = self.raiz
        for bit in bin_prefix:
            if bit not in actual.hijos:
                actual.hijos[bit] = NodoTrie()
            actual = actual.hijos[bit]
        actual.es_fin_prefijo = True
        if politicas:
            actual.politicas.update(politicas)
        return True

    def obtener_politica(self, dest_ip):
        """
        Realiza un longest-prefix match para obtener la política más específica
        para una IP de destino, aplicando herencia.
        """
        bin_ip = self._ip_to_binary(dest_ip, 32) # IP completa para búsqueda
        if bin_ip is None:
            return {} # IP inválida

        actual = self.raiz
        longest_match_politicas = {}
        
        for bit in bin_ip:
            if bit in actual.hijos:
                actual = actual.hijos[bit]
                if actual.es_fin_prefijo:
                    # Heredar políticas: las políticas del prefijo más largo sobrescriben las anteriores
                    longest_match_politicas.update(actual.politicas)
            else:
                break # No hay más coincidencia de prefijo
        return longest_match_politicas

    def eliminar_prefijo(self, prefix_ip, mask_length):
        """Elimina un prefijo del Trie."""
        # Esta es una implementación compleja ya que puede requerir la eliminación
        # de nodos intermedios si no son parte de otros prefijos.
        # Se deja como un placeholder.
        bin_prefix = self._ip_to_binary(prefix_ip, mask_length)
        if bin_prefix is None:
            return False

        # Lógica para encontrar el nodo final del prefijo y marcarlo como no-fin.
        # Luego, si el nodo no tiene hijos y no es fin de otro prefijo, eliminarlo y sus ancestros.
        print(f"Eliminación de prefijo {prefix_ip}/{mask_length} en Trie no implementada completamente.")
        return False # Placeholder

    def imprimir_arbol_ascii(self):
        """Imprime el Trie en formato ASCII (simplificado)."""
        def _print_trie(node, current_prefix_bits="", indent=""):
            # Convertir bits a formato IP para visualización
            ip_part = ""
            if current_prefix_bits:
                try:
                    # Intentar convertir los bits a octetos y luego a IP
                    octets = [int(current_prefix_bits[i:i+8], 2) for i in range(0, len(current_prefix_bits), 8)]
                    ip_part = ".".join(map(str, octets))
                    if len(current_prefix_bits) % 8 != 0: # Si no es un octeto completo
                        ip_part += f" ({current_prefix_bits[-len(current_prefix_bits)%8:]}...) "
                    ip_part = f"[{ip_part}/{len(current_prefix_bits)}]"
                except ValueError:
                    ip_part = f"[{current_prefix_bits}]" # Si no es una IP válida, mostrar bits
            
            if node.es_fin_prefijo:
                print(f"{indent}{ip_part} {{politicas: {node.politicas}}}")
            elif current_prefix_bits: # Solo imprimir nodos intermedios si representan algo
                print(f"{indent}{ip_part}")

            # Ordenar hijos para una impresión consistente
            sorted_children_keys = sorted(node.hijos.keys())
            for i, bit in enumerate(sorted_children_keys):
                # Determinar el prefijo para el hijo
                child_prefix_bits = current_prefix_bits + bit
                
                # Determinar el prefijo de indentación para el árbol
                if i == len(sorted_children_keys) - 1: # Último hijo
                    new_indent = indent + "└── "
                    next_indent = indent + "    "
                else:
                    new_indent = indent + "├── "
                    next_indent = indent + "|   "
                
                print(new_indent, end="")
                _print_trie(node.hijos[bit], child_prefix_bits, next_indent)
        
        _print_trie(self.raiz)