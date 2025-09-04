#!/usr/bin/env python3
"""
Script para corregir el modelo - entrenar desde datos CSV
"""

import pandas as pd
import numpy as np
import pickle
import json
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def fix_model():
    print("=== CORRIGIENDO MODELO ===")
    
    # 1. Cargar y procesar datos
    print("1. Cargando datos...")
    try:
        # Cargar con formato europeo (coma decimal, punto y coma separador)
        df = pd.read_csv('Concrete_Data.csv', sep=';', decimal=',')
        print(f"Datos cargados: {df.shape}")
        print(f"Columnas: {list(df.columns)}")
        
        # Renombrar columnas para que coincidan con el metadata
        column_mapping = {
            'Cement (component 1)(kg in a m^3 mixture)': 'Cemento_kg_m3',
            'Blast Furnace Slag (component 2)(kg in a m^3 mixture)': 'Escoria_Alto_Horno_kg_m3', 
            'Fly Ash (component 3)(kg in a m^3 mixture)': 'Ceniza_Volante_kg_m3',
            'Water  (component 4)(kg in a m^3 mixture)': 'Agua_kg_m3',
            'Superplasticizer (component 5)(kg in a m^3 mixture)': 'Superplastificante_kg_m3',
            'Coarse Aggregate  (component 6)(kg in a m^3 mixture)': 'Agregado_Grueso_kg_m3',
            'Fine Aggregate (component 7)(kg in a m^3 mixture)': 'Agregado_Fino_kg_m3',
            'Age (day)': 'Edad_dias',
            'Concrete compressive strength(MPa, megapascals) ': 'Resistencia_Compresion_kg_cm2'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Verificar que no hay valores nulos
        print(f"Valores nulos: {df.isnull().sum().sum()}")
        
        # Mostrar estadísticas básicas
        print(f"Rango resistencia (MPa): {df['Resistencia_Compresion_kg_cm2'].min():.2f} - {df['Resistencia_Compresion_kg_cm2'].max():.2f}")
        
        # Convertir MPa a kg/cm² (1 MPa ≈ 10.197 kg/cm²)
        df['Resistencia_Compresion_kg_cm2'] = df['Resistencia_Compresion_kg_cm2'] * 10.197
        
        print(f"Rango resistencia (kg/cm²): {df['Resistencia_Compresion_kg_cm2'].min():.2f} - {df['Resistencia_Compresion_kg_cm2'].max():.2f}")
        print("Datos procesados correctamente")
        
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return False
    
    # 2. Preparar features y target
    feature_names = [
        'Cemento_kg_m3', 'Escoria_Alto_Horno_kg_m3', 'Ceniza_Volante_kg_m3',
        'Agua_kg_m3', 'Superplastificante_kg_m3', 'Agregado_Grueso_kg_m3',
        'Agregado_Fino_kg_m3', 'Edad_dias'
    ]
    
    X = df[feature_names].values
    y = df['Resistencia_Compresion_kg_cm2'].values
    
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    
    # 3. Entrenar modelo
    print("2. Entrenando modelo RandomForest...")
    
    # Usar los mismos hiperparámetros para mantener consistencia
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X, y)
    print("Modelo entrenado exitosamente")
    
    # 4. Evaluar modelo
    print("3. Evaluando modelo...")
    
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()
    
    print(f"R² Score: {r2:.4f}")
    print(f"MAE: {mae:.2f} kg/cm²")
    print(f"CV Score: {cv_mean:.4f} ± {cv_std:.4f}")
    
    # 5. Guardar modelo corregido
    print("4. Guardando modelo...")
    
    # Guardar modelo
    with open('modelo_hormigon_ecuador_v1.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    # Actualizar metadata
    metadata = {
        "modelo_info": {
            "tipo": "RandomForestRegressor",
            "version": "1.1",  # Incrementar versión
            "fecha_entrenamiento": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "variables_entrada": feature_names,
            "variable_salida": "Resistencia_Compresion_kg_cm2"
        },
        "metricas": {
            "r2_score": r2,
            "mae_kg_cm2": mae,
            "cv_score_mean": cv_mean,
            "estabilidad": cv_std
        },
        "datos_entrenamiento": {
            "num_muestras": len(X),
            "num_features": X.shape[1],
            "conversion_mpa_kg_cm2": 10.197
        }
    }
    
    with open('modelo_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("5. Modelo corregido guardado exitosamente!")
    
    # 6. Verificar que funciona
    print("6. Verificando modelo...")
    
    # Cargar y probar
    with open('modelo_hormigon_ecuador_v1.pkl', 'rb') as f:
        test_model = pickle.load(f)
    
    # Hacer predicción de prueba
    test_input = X[0].reshape(1, -1)
    test_pred = test_model.predict(test_input)
    
    print(f"Predicción de prueba: {test_pred[0]:.2f} kg/cm²")
    print(f"Valor real: {y[0]:.2f} kg/cm²")
    
    if hasattr(test_model, 'predict'):
        print("✓ Modelo tiene método predict")
        print("✓ MODELO CORREGIDO EXITOSAMENTE")
        return True
    else:
        print("✗ Error: Modelo no tiene predict")
        return False

if __name__ == "__main__":
    success = fix_model()
    if success:
        print("\n=== MODELO LISTO PARA USAR ===")
        print("Ejecuta 'python main.py' para usar la aplicación")
    else:
        print("\n=== ERROR CORRIGIENDO MODELO ===")