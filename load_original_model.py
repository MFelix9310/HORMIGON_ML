#!/usr/bin/env python3
"""
Script para cargar y verificar el modelo ORIGINAL entrenado por el usuario
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path

def load_and_verify_original_model():
    print("=== CARGANDO MODELO ORIGINAL DEL USUARIO ===")
    
    model_path = Path("modelo_hormigon_ecuador_v1.pkl")
    
    if not model_path.exists():
        print("ERROR: modelo_hormigon_ecuador_v1.pkl no encontrado")
        return False
    
    try:
        # Cargar con joblib (como se entrenó originalmente)
        model = joblib.load(model_path)
        print(f"Modelo cargado: {type(model)}")
        print(f"Tipo específico: {model.__class__.__name__}")
        
        if hasattr(model, 'predict'):
            print("✓ Tiene método predict")
        else:
            print("✗ NO tiene método predict")
            return False
        
        # Verificar parámetros del modelo
        if hasattr(model, 'get_params'):
            params = model.get_params()
            print(f"Parámetros del modelo:")
            for key, value in params.items():
                print(f"  {key}: {value}")
        
        # Test de predicción
        print("\n=== TEST DE PREDICCIÓN ===")
        
        # Usar los mismos nombres de features que en el notebook
        feature_names = [
            'Cemento_kg_m3',
            'Escoria_Alto_Horno_kg_m3', 
            'Ceniza_Volante_kg_m3',
            'Agua_kg_m3',
            'Superplastificante_kg_m3',
            'Agregado_Grueso_kg_m3',
            'Agregado_Fino_kg_m3',
            'Edad_dias'
        ]
        
        # Valores de test (del notebook: cemento=200, escoria=200, etc.)
        test_values = [200, 200, 100, 130, 25, 1000, 700, 28]
        
        # Crear DataFrame con nombres de columnas (como se entrenó)
        test_df = pd.DataFrame([test_values], columns=feature_names)
        
        # Predicción
        prediction = model.predict(test_df)
        print(f"Predicción de test: {prediction[0]:.2f} kg/cm²")
        print("(Debería ser ~412.6 kg/cm² como en el notebook)")
        
        # Verificar que funciona con array numpy también
        test_array = np.array(test_values).reshape(1, -1)
        prediction_array = model.predict(test_array)
        print(f"Predicción con numpy array: {prediction_array[0]:.2f} kg/cm²")
        
        return True
        
    except Exception as e:
        print(f"Error cargando modelo: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = load_and_verify_original_model()
    if success:
        print("\n✅ MODELO ORIGINAL FUNCIONA CORRECTAMENTE")
    else:
        print("\n❌ ERROR CON EL MODELO ORIGINAL")