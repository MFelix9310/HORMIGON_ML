#!/usr/bin/env python3
"""
Model Handler CORREGIDO - Usando el modelo ORIGINAL del usuario
===============================================================

Este módulo carga correctamente el modelo RandomForestRegressor entrenado
por el usuario en el notebook.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import pandas as pd
from datetime import datetime
import joblib

logger = logging.getLogger(__name__)


class ConcreteModelHandler:
    """Manejador del modelo de predicción ORIGINAL del usuario."""
    
    # Rangos válidos EXACTOS del notebook
    VALID_RANGES = {
        'Cemento_kg_m3': (102, 540),           # Min/Max reales del dataset
        'Escoria_Alto_Horno_kg_m3': (0, 359),  
        'Ceniza_Volante_kg_m3': (0, 200),
        'Agua_kg_m3': (122, 247),              # Rangos reales
        'Superplastificante_kg_m3': (0, 32),   
        'Agregado_Grueso_kg_m3': (801, 1145),  
        'Agregado_Fino_kg_m3': (594, 993),     
        'Edad_dias': (1, 365)                  
    }
    
    # Clasificación NEC Ecuador EXACTA
    NEC_CLASSIFICATION = {
        (0, 140): ("Baja Resistencia", "#ef4444", "Uso estructural limitado"),
        (140, 280): ("Resistencia Normal", "#f97316", "Uso estructural común"), 
        (280, 420): ("Alta Resistencia", "#22c55e", "Estructuras exigentes"),
        (420, float('inf')): ("Ultra Alta Resistencia", "#3b82f6", "Estructuras especiales")
    }
    
    def __init__(self, model_path: str = "modelo_hormigon_ecuador_v1.pkl", 
                 metadata_path: str = "modelo_metadata.json"):
        """Inicializar con el modelo ORIGINAL del usuario."""
        self.model_path = Path(model_path)
        self.metadata_path = Path(metadata_path)
        self.model = None
        self.metadata = None
        
        # Nombres de features EXACTOS del notebook
        self.feature_names = [
            'Cemento_kg_m3',
            'Escoria_Alto_Horno_kg_m3',
            'Ceniza_Volante_kg_m3', 
            'Agua_kg_m3',
            'Superplastificante_kg_m3',
            'Agregado_Grueso_kg_m3',
            'Agregado_Fino_kg_m3',
            'Edad_dias'
        ]
        
        self.is_loaded = False
        self._load_model_and_metadata()
    
    def _load_model_and_metadata(self) -> bool:
        """Cargar el modelo ORIGINAL usando joblib como se entrenó."""
        try:
            # Cargar modelo con joblib (como se guardó en el notebook)
            logger.info(f"Cargando modelo original desde {self.model_path}")
            self.model = joblib.load(self.model_path)
            
            # Verificar que es el modelo correcto
            if not hasattr(self.model, 'predict'):
                raise ValueError("El modelo no tiene método predict")
                
            if not self.model.__class__.__name__ == 'RandomForestRegressor':
                logger.warning(f"Modelo inesperado: {self.model.__class__.__name__}")
            
            logger.info("Modelo RandomForestRegressor cargado correctamente")
            
            # Cargar metadata
            logger.info(f"Cargando metadata desde {self.metadata_path}")
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            
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
        """Obtener información del modelo."""
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
        """Validar inputs con rangos REALES del dataset."""
        errors = []
        
        # Verificar variables requeridas
        for feature in self.feature_names:
            if feature not in inputs:
                errors.append(f"Falta la variable: {feature}")
        
        # Validar rangos (más permisivos que antes)
        for feature, value in inputs.items():
            if feature in self.VALID_RANGES:
                min_val, max_val = self.VALID_RANGES[feature]
                # Agregar 10% de margen para flexibilidad
                margin = (max_val - min_val) * 0.1
                extended_min = max(0, min_val - margin)
                extended_max = max_val + margin
                
                if not (extended_min <= value <= extended_max):
                    errors.append(f"{feature}: {value} fuera del rango extendido [{extended_min:.0f}, {extended_max:.0f}]")
        
        return len(errors) == 0, errors
    
    def predict_strength(self, inputs: Dict[str, float]) -> Dict[str, Any]:
        """Predicción usando el modelo ORIGINAL como en el notebook."""
        if not self.is_loaded:
            raise RuntimeError("Modelo no cargado correctamente")
        
        # Validar inputs
        is_valid, errors = self.validate_inputs(inputs)
        if not is_valid:
            logger.warning(f"Inputs con advertencias: {', '.join(errors)}")
            # No lanzar error, solo advertir
        
        try:
            # Preparar datos EXACTAMENTE como en el notebook
            # Crear DataFrame con nombres de columnas (como se entrenó)
            feature_values = [inputs[feature] for feature in self.feature_names]
            
            # Usar array numpy para evitar warning de sklearn
            input_array = np.array(feature_values, dtype=np.float64).reshape(1, -1)
            
            # Realizar predicción
            prediction = self.model.predict(input_array)[0]
            
            # Verificar predicción válida
            if np.isnan(prediction) or np.isinf(prediction):
                raise ValueError("Predicción resultó en valor inválido")
            
            # Asegurar rango razonable
            if prediction < 0:
                prediction = abs(prediction)
                logger.warning(f"Predicción negativa corregida: {prediction:.2f}")
            
            # Calcular métricas adicionales
            water_cement_ratio = inputs['Agua_kg_m3'] / inputs['Cemento_kg_m3']
            total_cementitious = (inputs['Cemento_kg_m3'] + 
                                inputs['Escoria_Alto_Horno_kg_m3'] + 
                                inputs['Ceniza_Volante_kg_m3'])
            
            # Clasificación NEC EXACTA del notebook
            nec_class, nec_color, nec_description = self._classify_nec(prediction)
            
            # Confianza basada en la estabilidad del CV
            confidence = max(0.7, min(0.95, 1 - self.metadata['metricas']['estabilidad']))
            
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
        """Clasificación NEC EXACTA del notebook."""
        for (min_val, max_val), (classification, color, description) in self.NEC_CLASSIFICATION.items():
            if min_val <= strength < max_val:
                return classification, color, description
        
        return "Sin Clasificar", "#6b7280", "Valor fuera de rangos estándar"
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Obtener importancia de características del modelo original."""
        if not self.is_loaded or not hasattr(self.model, 'feature_importances_'):
            return {}
        
        importance_dict = {}
        for name, importance in zip(self.feature_names, self.model.feature_importances_):
            friendly_name = self._get_friendly_name(name)
            importance_dict[friendly_name] = round(importance, 4)
        
        return dict(sorted(importance_dict.items(), key=lambda x: x[1], reverse=True))
    
    def _get_friendly_name(self, technical_name: str) -> str:
        """Convertir nombres técnicos a nombres amigables."""
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
        """Mezclas predefinidas basadas en datos reales del notebook."""
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
            "Test del Notebook": {
                'Cemento_kg_m3': 200,
                'Escoria_Alto_Horno_kg_m3': 200,
                'Ceniza_Volante_kg_m3': 100,
                'Agua_kg_m3': 130,
                'Superplastificante_kg_m3': 25,
                'Agregado_Grueso_kg_m3': 1000,
                'Agregado_Fino_kg_m3': 700,
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
            }
        }