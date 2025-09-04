# Predictor de Resistencia de Hormigón - Interfaz Gráfica

## 🎯 Descripción

Aplicación profesional con interfaz gráfica PyQt6 para predecir la resistencia a compresión del hormigón utilizando un modelo de Machine Learning entrenado (Random Forest). Diseñada específicamente para ingenieros civiles y profesionales de la construcción.

## ✨ Características Principales

### 🎨 Interfaz Moderna
- **Diseño Profesional**: Interfaz moderna con tema personalizado
- **Componentes Interactivos**: Sliders sincronizados con SpinBoxes
- **Validación en Tiempo Real**: Verificación automática de rangos válidos
- **Visualizaciones Dinámicas**: Gráficos que se actualizan automáticamente

### 📊 Funcionalidades Avanzadas
- **Predicción Instantánea**: Resultados en menos de 100ms
- **Gauge Circular**: Medidor visual de resistencia predicha
- **Clasificación NEC**: Según normas ecuatorianas de construcción
- **Múltiples Visualizaciones**: Gráficos de composición, importancia y evolución

### 🔧 Herramientas Profesionales
- **Presets Inteligentes**: Mezclas predefinidas (C20, C25, C30, etc.)
- **Historial Completo**: Seguimiento de todas las predicciones
- **Exportación CSV**: Análisis de datos externos
- **Análisis del Modelo**: Métricas de performance y confiabilidad

## 🚀 Instalación y Uso

### Requisitos Previos
```bash
Python 3.11+
PyQt6 >= 6.8.0
matplotlib >= 3.8.0
pandas >= 2.1.0
numpy >= 1.26.0
scikit-learn >= 1.7.0
```

### Instalación Rápida
1. **Verificar archivos del modelo**:
   - `modelo_hormigon_ecuador_v1.pkl`
   - `modelo_metadata.json`

2. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar aplicación**:
   ```bash
   python main.py
   ```

### Uso de la Aplicación

#### Panel de Entrada (Izquierda)
1. **Materiales Cementícios**:
   - Cemento: 150-500 kg/m³
   - Escoria Alto Horno: 0-300 kg/m³
   - Ceniza Volante: 0-200 kg/m³

2. **Agua y Aditivos**:
   - Agua: 130-220 kg/m³
   - Superplastificante: 0-25 kg/m³

3. **Agregados**:
   - Agregado Grueso: 850-1100 kg/m³
   - Agregado Fino: 650-900 kg/m³

4. **Tiempo de Curado**:
   - Edad: 1-365 días

#### Panel de Resultados (Derecha)
- **Tab Resultados**: Gauge circular, métricas clave y gráficos
- **Tab Análisis**: Información del modelo e importancia de variables
- **Tab Historial**: Registro completo con exportación CSV

## 📋 Estructura del Proyecto

```
HORMIGON_ML/
├── main.py                          # Punto de entrada
├── predictor_gui.py                 # Interfaz principal
├── model_handler.py                 # Manejo del modelo ML
├── ui_components.py                 # Componentes reutilizables
├── styles.py                        # Estilos y temas
├── utils.py                         # Utilidades
├── requirements.txt                 # Dependencias
├── README.md                        # Documentación
├── modelo_hormigon_ecuador_v1.pkl   # Modelo entrenado
├── modelo_metadata.json             # Metadatos del modelo
├── ui/                              # Componentes adicionales
├── resources/                       # Recursos (iconos, estilos)
├── data/                           # Datos de trabajo
└── exports/                        # Archivos exportados
```

## 🎛️ Funcionalidades Detalladas

### Predicción de Resistencia
- **Algoritmo**: Random Forest Regressor optimizado
- **Precisión**: R² = 0.8426, MAE = 46.04 kg/cm²
- **Validación**: Cross-validation con estabilidad 0.018
- **Tiempo**: Predicción instantánea (< 100ms)

### Clasificación NEC Ecuador
- **Baja Resistencia**: < 210 kg/cm² (Rojo)
- **Resistencia Normal**: 210-280 kg/cm² (Naranja)
- **Alta Resistencia**: 280-420 kg/cm² (Verde)
- **Ultra Alta Resistencia**: > 420 kg/cm² (Azul)

### Presets Disponibles
1. **C20 - Uso General**: Hormigón estándar para aplicaciones generales
2. **C25 - Estructural**: Hormigón para estructuras comunes
3. **C30 - Alta Resistencia**: Para estructuras exigentes
4. **Hormigón Joven - 7 días**: Análisis de resistencia temprana
5. **Hormigón Maduro - 90 días**: Resistencia a largo plazo

### Gráficos y Visualizaciones
1. **Gauge Circular**: Resistencia predicha con código de colores
2. **Composición de Mezcla**: Distribución porcentual de materiales
3. **Clasificación NEC**: Comparación con rangos estándar
4. **Evolución Temporal**: Efecto de la edad en la resistencia
5. **Importancia de Variables**: Contribución de cada parámetro
6. **Historial de Predicciones**: Tendencias y comparaciones

## 🔧 Configuración Avanzada

### Personalización de Estilos
Los estilos se pueden modificar en `styles.py`:
```python
COLORS = {
    'primary': '#2563eb',        # Azul principal
    'success': '#059669',        # Verde éxito
    'warning': '#d97706',        # Naranja advertencia
    'danger': '#dc2626',         # Rojo peligro
    'background': '#f8fafc',     # Fondo principal
    'surface': '#ffffff'         # Superficie de componentes
}
```

### Logging y Debugging
Configurar nivel de log en `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # Para debug detallado
logging.basicConfig(level=logging.INFO)   # Para información normal
```

### Extensibilidad
- **Nuevos Presets**: Agregar en `model_handler.py`
- **Componentes UI**: Crear en `ui_components.py`
- **Utilidades**: Extender en `utils.py`

## 📊 Métricas del Modelo

### Performance
- **R² Score**: 0.8426 (84.26% de varianza explicada)
- **MAE**: 46.04 kg/cm² (error absoluto medio)
- **CV Score**: 0.8741 ± 0.018 (validación cruzada)
- **Estabilidad**: 0.018 (muy estable)

### Variables de Importancia
1. **Edad**: Mayor importancia en la predicción
2. **Cemento**: Material principal determinante
3. **Agua**: Afecta directamente la resistencia
4. **Agregados**: Influencia en la estructura final

## 🛠️ Troubleshooting

### Problemas Comunes

1. **Error de Archivos No Encontrados**:
   ```
   ERROR: No se encontro el archivo del modelo
   ```
   - **Solución**: Verificar que `modelo_hormigon_ecuador_v1.pkl` y `modelo_metadata.json` estén en el directorio

2. **Error de Importación PyQt6**:
   ```
   ModuleNotFoundError: No module named 'PyQt6'
   ```
   - **Solución**: `pip install PyQt6`

3. **Error de Encoding Unicode**:
   ```
   UnicodeEncodeError: 'charmap' codec can't encode
   ```
   - **Solución**: Configurar terminal con `chcp 65001` (Windows)

4. **Gráficos No Se Muestran**:
   - **Solución**: Verificar instalación de matplotlib: `pip install matplotlib`

### Logs y Diagnóstico
- **Archivo de log**: `concrete_predictor.log`
- **Nivel debug**: Cambiar en `main.py`
- **Información del sistema**: Menú Ayuda → Acerca de

## 📝 Licencia y Créditos

- **Desarrollado con**: Claude Code (Anthropic)
- **Framework GUI**: PyQt6
- **Machine Learning**: scikit-learn
- **Visualizaciones**: matplotlib + seaborn
- **Datos**: Procesamiento con pandas

## 🔄 Actualizaciones Futuras

### Características Planificadas
- [ ] Soporte para múltiples idiomas
- [ ] Exportación a PDF con gráficos
- [ ] Comparación de múltiples mezclas
- [ ] Integración con bases de datos
- [ ] API REST para uso remoto
- [ ] Modo oscuro/claro
- [ ] Predicción por lotes desde Excel

### Mejoras del Modelo
- [ ] Entrenamiento con más datos
- [ ] Validación con datos ecuatorianos
- [ ] Incorporación de nuevas variables
- [ ] Modelos especializados por región

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades:
1. Verificar troubleshooting en esta documentación
2. Revisar logs en `concrete_predictor.log`
3. Contactar al desarrollador con información del error

---

**Predictor de Resistencia de Hormigón v1.0** - Herramienta profesional para ingenieros civiles desarrollada con inteligencia artificial.