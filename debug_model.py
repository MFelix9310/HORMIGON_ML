#!/usr/bin/env python3
"""
Script para debuggear el contenido del modelo
"""

import pickle
import json
import numpy as np
from pathlib import Path

def debug_model():
    print("=== DEBUGGING MODELO ===")
    
    # Verificar archivos
    model_path = Path("modelo_hormigon_ecuador_v1.pkl")
    metadata_path = Path("modelo_metadata.json")
    
    print(f"Modelo existe: {model_path.exists()}")
    print(f"Metadata existe: {metadata_path.exists()}")
    
    if model_path.exists():
        print(f"Tamaño del modelo: {model_path.stat().st_size} bytes")
        
        try:
            print("\n=== CARGANDO MODELO ===")
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            print(f"Tipo del objeto cargado: {type(model_data)}")
            print(f"Tipo específico: {model_data.__class__.__name__}")
            
            if hasattr(model_data, '__dict__'):
                print(f"Atributos del objeto: {list(model_data.__dict__.keys())}")
            
            if hasattr(model_data, 'predict'):
                print("✓ Tiene método predict")
            else:
                print("✗ NO tiene método predict")
            
            if isinstance(model_data, np.ndarray):
                print(f"Es un numpy array con shape: {model_data.shape}")
                print(f"Dtype: {model_data.dtype}")
                print(f"Primeros valores: {model_data.flat[:10] if model_data.size > 0 else 'vacío'}")
            
            # Intentar con diferentes métodos de carga
            print("\n=== INTENTANDO MÉTODOS ALTERNATIVOS ===")
            
            try:
                import joblib
                print("Intentando cargar con joblib...")
                model_joblib = joblib.load(model_path)
                print(f"Tipo con joblib: {type(model_joblib)}")
                if hasattr(model_joblib, 'predict'):
                    print("✓ Joblib: Tiene método predict")
                else:
                    print("✗ Joblib: NO tiene método predict")
            except Exception as e:
                print(f"Error con joblib: {e}")
                
        except Exception as e:
            print(f"Error cargando modelo: {e}")
            import traceback
            traceback.print_exc()
    
    if metadata_path.exists():
        print("\n=== METADATA ===")
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            print(json.dumps(metadata, indent=2, ensure_ascii=False))
            
        except Exception as e:
            print(f"Error cargando metadata: {e}")

if __name__ == "__main__":
    debug_model()