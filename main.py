#!/usr/bin/env python3
"""
Predictor de Resistencia de Hormigón - Interfaz Gráfica
=========================================================

Aplicación PyQt6 profesional para predecir la resistencia a compresión del hormigón
usando un modelo de Random Forest entrenado.

Autor: Claude Code
Versión: 1.0
Fecha: 2025-09-04
"""

import sys
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor

from predictor_gui import ConcreteStrengthPredictor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('concrete_predictor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class Application:
    """Clase principal para manejar la aplicación."""
    
    def __init__(self):
        """Inicializar la aplicación."""
        self.app = None
        self.main_window = None
        self._setup_application()
    
    def _setup_application(self):
        """Configurar la aplicación PyQt6."""
        # Configurar aplicación
        QApplication.setApplicationName("Predictor de Resistencia de Hormigón")
        QApplication.setApplicationVersion("1.0")
        QApplication.setOrganizationName("Ingeniería Civil Pro")
        QApplication.setOrganizationDomain("ingenieria.pro")
        
        # Crear aplicación
        self.app = QApplication(sys.argv)
        
        # Configurar fuente de la aplicación
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        # Aplicar tema personalizado
        self._apply_custom_theme()
        
        logger.info("Aplicación PyQt6 inicializada correctamente")
    
    def _apply_custom_theme(self):
        """Aplicar tema personalizado a la aplicación."""
        # Configurar paleta de colores profesional
        palette = QPalette()
        
        # Colores principales
        palette.setColor(QPalette.ColorRole.Window, QColor(248, 250, 252))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(30, 41, 59))
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(241, 245, 249))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(37, 99, 235))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(30, 41, 59))
        palette.setColor(QPalette.ColorRole.Button, QColor(241, 245, 249))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(30, 41, 59))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(220, 38, 38))
        palette.setColor(QPalette.ColorRole.Link, QColor(37, 99, 235))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(37, 99, 235))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.app.setPalette(palette)
    
    def run(self) -> int:
        """Ejecutar la aplicación principal."""
        try:
            # Crear ventana principal
            self.main_window = ConcreteStrengthPredictor()
            
            # Mostrar ventana
            self.main_window.show()
            
            logger.info("Ventana principal mostrada")
            
            # Ejecutar aplicación
            return self.app.exec()
            
        except Exception as e:
            logger.error(f"Error ejecutando aplicación: {e}")
            return 1


def main():
    """Función principal de entrada."""
    # Verificar archivos requeridos
    model_path = Path("modelo_hormigon_ecuador_v1.pkl")
    metadata_path = Path("modelo_metadata.json")
    
    if not model_path.exists():
        print("ERROR: No se encontro el archivo del modelo 'modelo_hormigon_ecuador_v1.pkl'")
        print("   Asegurate de estar ejecutando desde el directorio correcto.")
        return 1
    
    if not metadata_path.exists():
        print("ERROR: No se encontro el archivo de metadata 'modelo_metadata.json'")
        print("   Asegurate de estar ejecutando desde el directorio correcto.")
        return 1
    
    print("=> Archivos del modelo encontrados")
    print("=> Iniciando Predictor de Resistencia de Hormigon...")
    
    # Crear y ejecutar aplicación
    app = Application()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())