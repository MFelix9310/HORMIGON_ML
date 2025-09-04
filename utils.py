#!/usr/bin/env python3
"""
Utilidades y Funciones de Apoyo
===============================

Módulo con funciones utilitarias para la aplicación de predicción
de resistencia de hormigón.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO", log_file: str = "concrete_predictor.log") -> None:
    """
    Configurar sistema de logging.
    
    Args:
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)
        log_file: Archivo donde guardar logs
    """
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Nivel de log inválido: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def validate_model_files(model_path: str = "modelo_hormigon_ecuador_v1.pkl", 
                        metadata_path: str = "modelo_metadata.json") -> Tuple[bool, List[str]]:
    """
    Validar que los archivos del modelo existan y sean válidos.
    
    Args:
        model_path: Ruta al archivo del modelo
        metadata_path: Ruta al archivo de metadata
        
    Returns:
        Tuple[bool, List[str]]: (es_válido, lista_errores)
    """
    errors = []
    
    # Verificar existencia de archivos
    if not Path(model_path).exists():
        errors.append(f"Archivo del modelo no encontrado: {model_path}")
    
    if not Path(metadata_path).exists():
        errors.append(f"Archivo de metadata no encontrado: {metadata_path}")
    
    # Verificar formato de metadata si existe
    if Path(metadata_path).exists():
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Verificar campos requeridos
            required_fields = ['modelo_info', 'metricas']
            for field in required_fields:
                if field not in metadata:
                    errors.append(f"Campo faltante en metadata: {field}")
        
        except json.JSONDecodeError as e:
            errors.append(f"Error leyendo metadata JSON: {e}")
        except Exception as e:
            errors.append(f"Error validando metadata: {e}")
    
    return len(errors) == 0, errors


def format_resistance_value(value: float, precision: int = 2) -> str:
    """
    Formatear valor de resistencia para mostrar.
    
    Args:
        value: Valor de resistencia
        precision: Número de decimales
        
    Returns:
        str: Valor formateado con unidades
    """
    return f"{value:.{precision}f} kg/cm²"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Formatear valor como porcentaje.
    
    Args:
        value: Valor entre 0 y 1
        precision: Número de decimales
        
    Returns:
        str: Valor formateado como porcentaje
    """
    return f"{value * 100:.{precision}f}%"


def get_nec_color(resistance: float) -> str:
    """
    Obtener color según clasificación NEC Ecuador.
    
    Args:
        resistance: Valor de resistencia en kg/cm²
        
    Returns:
        str: Código de color hexadecimal
    """
    if resistance < 210:
        return "#ef4444"  # Rojo - Baja resistencia
    elif resistance < 280:
        return "#f97316"  # Naranja - Normal
    elif resistance < 420:
        return "#22c55e"  # Verde - Alta
    else:
        return "#3b82f6"  # Azul - Ultra alta


def create_backup_filename(base_name: str, extension: str = ".csv") -> str:
    """
    Crear nombre de archivo con timestamp para backups.
    
    Args:
        base_name: Nombre base del archivo
        extension: Extensión del archivo
        
    Returns:
        str: Nombre de archivo con timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{base_name}_{timestamp}{extension}"


def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Convertir valor a float de manera segura.
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si falla la conversión
        
    Returns:
        float: Valor convertido o valor por defecto
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"No se pudo convertir {value} a float, usando {default}")
        return default


def calculate_water_cement_ratio(water: float, cement: float) -> float:
    """
    Calcular relación agua/cemento.
    
    Args:
        water: Cantidad de agua en kg/m³
        cement: Cantidad de cemento en kg/m³
        
    Returns:
        float: Relación A/C
    """
    if cement == 0:
        logger.warning("División por cero en cálculo A/C, cemento = 0")
        return 0.0
    
    return water / cement


def calculate_total_cementitious(cement: float, slag: float = 0.0, 
                                fly_ash: float = 0.0) -> float:
    """
    Calcular total de materiales cementícios.
    
    Args:
        cement: Cemento en kg/m³
        slag: Escoria de alto horno en kg/m³
        fly_ash: Ceniza volante en kg/m³
        
    Returns:
        float: Total de materiales cementícios
    """
    return cement + slag + fly_ash


def export_data_to_csv(data: List[Dict[str, Any]], filename: str) -> bool:
    """
    Exportar datos a archivo CSV.
    
    Args:
        data: Lista de diccionarios con datos
        filename: Nombre del archivo a crear
        
    Returns:
        bool: True si la exportación fue exitosa
    """
    try:
        import pandas as pd
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Datos exportados exitosamente a {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exportando datos a CSV: {e}")
        return False


def load_data_from_csv(filename: str) -> Optional[List[Dict[str, Any]]]:
    """
    Cargar datos desde archivo CSV.
    
    Args:
        filename: Nombre del archivo a leer
        
    Returns:
        Optional[List[Dict[str, Any]]]: Datos cargados o None si error
    """
    try:
        import pandas as pd
        df = pd.read_csv(filename, encoding='utf-8')
        data = df.to_dict('records')
        logger.info(f"Datos cargados exitosamente desde {filename}")
        return data
    except Exception as e:
        logger.error(f"Error cargando datos desde CSV: {e}")
        return None


def get_app_version() -> str:
    """
    Obtener versión de la aplicación.
    
    Returns:
        str: Versión de la aplicación
    """
    return "1.0.0"


def get_system_info() -> Dict[str, str]:
    """
    Obtener información del sistema.
    
    Returns:
        Dict[str, str]: Información del sistema
    """
    import platform
    import sys
    
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'python_version': sys.version,
        'platform': platform.platform(),
        'architecture': platform.architecture()[0]
    }


def create_directories_if_needed() -> None:
    """Crear directorios necesarios si no existen."""
    directories = ['exports', 'logs', 'data', 'resources']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        logger.debug(f"Directorio verificado/creado: {directory}")


# Constantes útiles
DEFAULT_CONCRETE_PARAMS = {
    'Cemento_kg_m3': 280,
    'Escoria_Alto_Horno_kg_m3': 0,
    'Ceniza_Volante_kg_m3': 0,
    'Agua_kg_m3': 175,
    'Superplastificante_kg_m3': 2.5,
    'Agregado_Grueso_kg_m3': 975,
    'Agregado_Fino_kg_m3': 775,
    'Edad_dias': 28
}

NEC_CLASSIFICATIONS = {
    'baja': (0, 210, "#ef4444", "Uso estructural limitado"),
    'normal': (210, 280, "#f97316", "Uso estructural común"),
    'alta': (280, 420, "#22c55e", "Estructuras exigentes"),
    'ultra_alta': (420, float('inf'), "#3b82f6", "Estructuras especiales")
}