#!/usr/bin/env python3
"""
Versión de debug para capturar errores específicos
"""

import sys
import traceback
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication

# Configurar logging más detallado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug_log.txt', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    """Manejar excepciones no capturadas."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Excepción no capturada:", 
                exc_info=(exc_type, exc_value, exc_traceback))
    print("EXCEPCION NO CAPTURADA:")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

# Configurar manejo de excepciones
sys.excepthook = handle_exception

try:
    print("Iniciando aplicación de debug...")
    
    # Verificar archivos
    model_path = Path("modelo_hormigon_ecuador_v1.pkl")
    metadata_path = Path("modelo_metadata.json")
    
    if not model_path.exists() or not metadata_path.exists():
        print("Error: Archivos del modelo no encontrados")
        sys.exit(1)
    
    # Importar después de configurar logging
    from predictor_gui import ConcreteStrengthPredictor
    
    print("Creando aplicación PyQt6...")
    app = QApplication(sys.argv)
    
    print("Creando ventana principal...")
    window = ConcreteStrengthPredictor()
    
    print("Mostrando ventana...")
    window.show()
    
    print("Ejecutando aplicación...")
    sys.exit(app.exec())
    
except Exception as e:
    print(f"ERROR CRÍTICO: {e}")
    traceback.print_exc()
    sys.exit(1)