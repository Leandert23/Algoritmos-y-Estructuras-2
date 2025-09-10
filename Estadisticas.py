"""
Módulo para generar estadísticas y reportes detallados de la red,
dispositivos y estructuras de datos.
"""
from datetime import datetime

class Estadisticas:
    """Clase para recopilar y mostrar estadísticas del simulador."""
    
    def __init__(self, red):
        self.red = red
        self.historial_reportes = []  # Lista de reportes generados
    
    def generar_reporte_completo(self):
        """
        Genera un reporte completo de estadísticas de la red.
        Returns:
            str: El reporte formateado.
        """
        reporte = []
        reporte.append("REPORTE DE ESTADÍSTICAS DEL SIMULADOR DE RED LAN")
        reporte.append("=" * 60)
        reporte.append(f"Fecha y Hora: {datetime.now().isoformat()}")
        reporte.append("")
        
        # Estadísticas generales de la red
        reporte.append("1. ESTADÍSTICAS GENERALES DE LA RED:")
        reporte.append(f"   - Número de dispositivos: {len(self.red.dispositivos)}")
        reporte.append(f"   - Número de conexiones: {self._contar_conexiones()}")
        reporte.append(f"   - Paquetes enviados: {self.red.estadisticas['paquetes_enviados']}")
        reporte.append(f"   - Paquetes entregados: {self.red.estadisticas['paquetes_entregados']}")
        reporte.append("")
        
        # Detalles por dispositivo
        reporte.append("2. DETALLES POR DISPOSITIVO:")
        for nombre, dispositivo in self.red.dispositivos.items():
            reporte.append(f"   - Dispositivo: {nombre} (Tipo: {dispositivo.tipo})")
            reporte.append(f"     Interfaces: {len(dispositivo.interfaces)}")
            for intf_nombre, interfaz in dispositivo.interfaces.items():
                estado = "ACTIVA" if interfaz.estado else "INACTIVA"
                reporte.append(f"       {intf_nombre}: {estado}, IP: {interfaz.ip or 'Sin dirección'}, Conexiones: {len(interfaz.conexiones)}")
            
            if dispositivo.tipo == "router":
                # Estadísticas específicas para routers
                stats = dispositivo.tabla_rutas_avl.obtener_avl_stats()
                reporte.append(f"       Tabla de Rutas (AVL): Nodos: {stats['nodos']}, Altura: {stats['altura']}, Rotaciones: LL={stats['rotaciones']['LL']}, LR={stats['rotaciones']['LR']}, RL={stats['rotaciones']['RL']}, RR={stats['rotaciones']['RR']}")
            reporte.append("")
        
        # Estadísticas del B-Tree de snapshots
        bstats = self.red.b_tree_snapshots.obtener_bstats()
        reporte.append("3. ÍNDICE DE CONFIGURACIONES PERSISTENTES (B-TREE):")
        reporte.append(f"   - Orden (t): {bstats['orden']}")
        reporte.append(f"   - Altura: {bstats['altura']}")
        reporte.append(f"   - Número de nodos: {bstats['nodos']}")
        reporte.append(f"   - Número de splits: {bstats['splits']}")
        reporte.append(f"   - Número de merges: {bstats['merges']}")
        reporte.append("")
        
        # Estadísticas del registro de errores
        from Errores import error_logger
        errores = error_logger.obtener_errores()
        reporte.append("4. REGISTRO DE ERRORES:")
        reporte.append(f"   - Número total de errores registrados: {len(errores)}")
        if errores:
            reporte.append("   - Últimos 5 errores:")
            for error in errores[-5:]:
                reporte.append(f"     [{error['timestamp']}] {error['tipo']}: {error['mensaje']}")
        reporte.append("")
        
        # Mostrar reporte y guardarlo en historial
        reporte_completo = "\n".join(reporte)
        self.historial_reportes.append({
            "fecha": datetime.now().isoformat(),
            "reporte": reporte_completo
        })
        return reporte_completo
    
    def _contar_conexiones(self):
        """Cuenta el número total de conexiones en la red."""
        total_conexiones = 0
        for dispositivo in self.red.dispositivos.values():
            for interfaz in dispositivo.interfaces.values():
                total_conexiones += len(interfaz.conexiones)
        return total_conexiones // 2  # Cada conexión se cuenta dos veces (bidireccional)

    def mostrar_historial_reportes(self):
        """
        Muestra el historial de reportes generados.
        Returns:
            str: Lista de reportes en el historial.
        """
        if not self.historial_reportes:
            return "No hay reportes generados aún."
        
        output = []
        output.append("HISTORIAL DE REPORTES:")
        output.append("=" * 40)
        for i, reporte in enumerate(self.historial_reportes, 1):
            output.append(f"{i}. Fecha: {reporte['fecha']}")
            output.append("   Resumen: (Ver reporte completo para detalles)")
        return "\n".join(output)
    
    def exportar_reporte_a_archivo(self, reporte, archivo="reporte_estadisticas.txt"):
        """
        Exporta un reporte a un archivo de texto.
        Args:
            reporte (str): El contenido del reporte.
            archivo (str): Nombre del archivo de salida.
        """
        try:
            with open(archivo, "w") as f:
                f.write(reporte)
            print(f"[OK] Reporte exportado a '{archivo}'.")
        except Exception as e:
            print(f"[ERROR] No se pudo exportar el reporte: {e}")