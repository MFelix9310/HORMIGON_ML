#!/usr/bin/env python3
"""
Manejador del Modelo de Machine Learning
=======================================

Este módulo maneja la carga y uso del modelo de predicción de resistencia
de hormigón entrenado.
"""

import json
import pickle
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime

logger = logging.getLogger(__name__)


class ConcreteModelHandler:
    """Manejador del modelo de predicción de hormigón."""
    
    # Rangos válidos para cada variable (kg/m³ excepto edad en días)
    VALID_RANGES = {
        'Cemento_kg_m3': (150, 500),
        'Escoria_Alto_Horno_kg_m3': (0, 300),
        'Ceniza_Volante_kg_m3': (0, 200),
        'Agua_kg_m3': (130, 220),
        'Superplastificante_kg_m3': (0, 25),
        'Agregado_Grueso_kg_m3': (850, 1100),
        'Agregado_Fino_kg_m3': (650, 900),
        'Edad_dias': (1, 365)
    }
    
    # Clasificación NEC Ecuador
    NEC_CLASSIFICATION = {
        (0, 210): ("Baja Resistencia", "#ef4444", "Uso estructural limitado"),
        (210, 280): ("Resistencia Normal", "#f97316", "Uso estructural común"),
        (280, 420): ("Alta Resistencia", "#22c55e", "Estructuras exigentes"),
        (420, float('inf')): ("Ultra Alta Resistencia", "#3b82f6", "Estructuras especiales")
    }
    
    def __init__(self, model_path: str = "modelo_hormigon_ecuador_v1.pkl", 
                 metadata_path: str = "modelo_metadata.json"):
        """
        Inicializar el manejador del modelo.
        
        Args:
            model_path: Ruta al archivo del modelo .pkl
            metadata_path: Ruta al archivo de metadata .json
        """
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.model = None
        self.metadata = None
        self.feature_names = None
        self.is_loaded = False
        
        # Cargar modelo y metadata
        self._load_model_and_metadata()
    
    def _load_model_and_metadata(self) -> bool:
        """
        Cargar el modelo y sus metadatos.
        
        Returns:
            bool: True si la carga fue exitosa
        """
        try:
            # Cargar modelo
            logger.info(f"Cargando modelo desde {self.model_path}")
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Cargar metadata
            logger.info(f"Cargando metadata desde {self.metadata_path}")
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
            # Extraer nombres de características
            self.feature_names = self.metadata['modelo_info']['variables_entrada']
            
            self.is_loaded = True
            logger.info("Modelo y metadata cargados exitosamente")
            return True
            
        except FileNotFoundError as e:
            logger.error(f"Archivo no encontrado: {e}")
            return False
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtener información del modelo.
        
        Returns:
            Dict con información del modelo
        """
        if not self.is_loaded:
            return {}
        
        return {
            'tipo_modelo': self.metadata['modelo_info']['tipo'],
            'version': self.metadata['modelo_info']['version'],
            'fecha_entrenamiento': self.metadata['modelo_info']['fecha_entrenamiento'],
            'r2_score': round(self.metadata['metricas']['r2_score'], 4),
            'mae_kg_cm2': round(self.metadata['metricas']['mae_kg_cm2'], 2),
            'cv_score_mean': round(self.metadata['metricas']['cv_score_mean'], 4),
            'estabilidad': round(self.metadata['metricas']['estabilidad'], 6),
            'variables_entrada': self.feature_names,
            'variable_salida': self.metadata['modelo_info']['variable_salida']
        }
    
    def validate_inputs(self, inputs: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validar que los inputs estén en rangos válidos.
        
        Args:
            inputs: Diccionario con los valores de entrada
            
        Returns:
            Tuple[bool, List[str]]: (es_válido, lista_errores)
        """
        errors = []
        
        # Verificar que todas las variables requeridas estén presentes
        for feature in self.feature_names:
            if feature not in inputs:
                errors.append(f"Falta la variable: {feature}")
        
        # Verificar rangos válidos
        for feature, value in inputs.items():
            if feature in self.VALID_RANGES:
                min_val, max_val = self.VALID_RANGES[feature]
                if not (min_val <= value <= max_val):
                    errors.append(f"{feature}: {value} fuera del rango válido [{min_val}, {max_val}]")
        
        return len(errors) == 0, errors
    
    def predict_strength(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """
        Predecir la resistencia a compresión del hormigón.
        
        Args:
            inputs: Diccionario con los valores de entrada
            
        Returns:
            Dict con la predicción y análisis adicional
        """
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado correctamente")
        
        # Validar inputs
        is_valid, errors = self.validate_inputs(inputs)
        if not is_valid:
            raise ValueError(f"Inputs inválidos: {', '.join(errors)}")
        
        try:
            # Preparar datos para predicción
            feature_values = [inputs[feature] for feature in self.feature_names]
            X = np.array(feature_values, dtype=np.float64).reshape(1, -1)
            
            # Verificar que no hay valores NaN o infinitos
            if np.any(np.isnan(X)) or np.any(np.isinf(X)):
                raise ValueError("Los datos contienen valores inválidos (NaN o infinito)")
            
            # Verificar que los valores están en rangos razonables
            if np.any(X < 0):
                raise ValueError("Los datos no pueden ser negativos")
            
            # Realizar predicción
            prediction = self.model.predict(X)[0]
            
            # Verificar que la predicción es válida
            if np.isnan(prediction) or np.isinf(prediction):
                raise ValueError("La predicción resultó en un valor inválido")
            
            # Verificar que la predicción está en un rango razonable (5-1000 kg/cm²)
            if not (5 <= prediction <= 1000):
                logger.warning(f"Predicción fuera de rango normal: {prediction:.2f} kg/cm²")
            
            # Calcular métricas adicionales
            water_cement_ratio = inputs['Agua_kg_m3'] / inputs['Cemento_kg_m3']
            total_cementitious = (inputs['Cemento_kg_m3'] + 
                                inputs['Escoria_Alto_Horno_kg_m3'] + 
                                inputs['Ceniza_Volante_kg_m3'])
            
            # Clasificación NEC
            nec_class, nec_color, nec_description = self._classify_nec(prediction)
            
            # Confianza de la predicción (basada en la estabilidad del CV)
            confidence = max(0.6, min(0.95, 1 - self.metadata['metricas']['estabilidad'] * 10))
            
            result = {
                'resistencia_predicha_kg_cm2': round(prediction, 2),
                'relacion_agua_cemento': round(water_cement_ratio, 3),
                'total_cementicios_kg_m3': round(total_cementitious, 1),
                'clasificacion_nec': nec_class,
                'color_clasificacion': nec_color,
                'descripcion_nec': nec_description,
                'confianza_prediccion': round(confidence, 3),
                'edad_ensayo_dias': inputs['Edad_dias'],
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Prediccion exitosa: {prediction:.2f} kg/cm²")
            return result
            
        except Exception as e:
            logger.error(f"Error en prediccion: {e}")
            raise
    
    def _classify_nec(self, strength: float) -> Tuple[str, str, str]:
        """
        Clasificar la resistencia según normas NEC Ecuador.
        
        Args:
            strength: Resistencia en kg/cm²
            
        Returns:
            Tuple[str, str, str]: (clasificación, color, descripción)
        """
        for (min_val, max_val), (classification, color, description) in self.NEC_CLASSIFICATION.items():
            if min_val <= strength < max_val:
                return classification, color, description
        
        # Fallback para valores extremos
        return "Sin Clasificar", "#6b7280", "Valor fuera de rangos estándar"
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Obtener la importancia de las características del modelo.
        
        Returns:
            Dict con importancia de cada característica
        """
        if not self.is_loaded or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = {}
        for name, importance in zip(self.feature_names, self.model.feature_importances_):
            # Convertir nombres técnicos a nombres amigables
            friendly_name = self._get_friendly_name(name)
            importance_dict[friendly_name] = round(importance, 4)
        
        # Ordenar por importancia descendente
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def _get_friendly_name(self, technical_name: str) -> str:
        """
        Convertir nombre técnico a nombre amigable.
        
        Args:
            technical_name: Nombre técnico de la variable
            
        Returns:
            str: Nombre amigable
        """
        name_mapping = {
            'Cemento_kg_m3': 'Cemento',
            'Escoria_Alto_Horno_kg_m3': 'Escoria de Alto Horno',
            'Ceniza_Volante_kg_m3': 'Ceniza Volante',
            'Agua_kg_m3': 'Agua',
            'Superplastificante_kg_m3': 'Superplastificante',
            'Agregado_Grueso_kg_m3': 'Agregado Grueso',
            'Agregado_Fino_kg_m3': 'Agregado Fino',
            'Edad_dias': 'Edad de Curado'
        }
        
        return name_mapping.get(technical_name, technical_name)
    
    def get_preset_mixes(self) -> Dict[str, Dict[str, float]]:
        """
        Obtener mezclas predefinidas comunes.
        
        Returns:
            Dict con mezclas predefinidas
        """
        return {
            "C20 - Uso General": {
                'Cemento_kg_m3': 280,
                'Escoria_Alto_Horno_kg_m3': 70,
                'Ceniza_Volante_kg_m3': 0,
                'Agua_kg_m3': 175,
                'Superplastificante_kg_m3': 2.5,
                'Agregado_Grueso_kg_m3': 950,
                'Agregado_Fino_kg_m3': 750,
                'Edad_dias': 28
            },
            "C25 - Estructural": {
                'Cemento_kg_m3': 320,
                'Escoria_Alto_Horno_kg_m3': 80,
                'Ceniza_Volante_kg_m3': 20,
                'Agua_kg_m3': 165,
                'Superplastificante_kg_m3': 4.0,
                'Agregado_Grueso_kg_m3': 975,
                'Agregado_Fino_kg_m3': 775,
                'Edad_dias': 28
            },
            "C30 - Alta Resistencia": {
                'Cemento_kg_m3': 380,
                'Escoria_Alto_Horno_kg_m3': 95,
                'Ceniza_Volante_kg_m3': 45,
                'Agua_kg_m3': 155,
                'Superplastificante_kg_m3': 6.5,
                'Agregado_Grueso_kg_m3': 1000,
                'Agregado_Fino_kg_m3': 800,
                'Edad_dias': 28
            },
            "Hormigón Joven - 7 días": {
                'Cemento_kg_m3': 350,
                'Escoria_Alto_Horno_kg_m3': 0,
                'Ceniza_Volante_kg_m3': 0,
                'Agua_kg_m3': 170,
                'Superplastificante_kg_m3': 3.5,
                'Agregado_Grueso_kg_m3': 980,
                'Agregado_Fino_kg_m3': 780,
                'Edad_dias': 7
            },
            "Hormigón Maduro - 90 días": {
                'Cemento_kg_m3': 300,
                'Escoria_Alto_Horno_kg_m3': 150,
                'Ceniza_Volante_kg_m3': 75,
                'Agua_kg_m3': 160,
                'Superplastificante_kg_m3': 5.0,
                'Agregado_Grueso_kg_m3': 950,
                'Agregado_Fino_kg_m3': 750,
                'Edad_dias': 90
            }
        }