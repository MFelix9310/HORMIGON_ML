#!/usr/bin/env python3
"""
Interfaz Gráfica Principal del Predictor de Hormigón
===================================================

Ventana principal de la aplicación que integra todos los componentes
para la predicción de resistencia del hormigón.
"""

import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                           QSplitter, QGroupBox, QLabel, QPushButton, QComboBox,
                           QFrame, QScrollArea, QTabWidget, QTableWidget, 
                           QTableWidgetItem, QFileDialog, QMessageBox, QStatusBar,
                           QMenuBar, QMenu, QApplication)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QAction

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import seaborn as sns

from model_handler_fixed import ConcreteModelHandler
from ui_components import SliderSpinBoxWidget, CircularGauge, StatusCard, LogTextEdit
from styles import get_complete_stylesheet, COLORS

logger = logging.getLogger(__name__)

class ConcreteStrengthPredictor(QMainWindow):
    """Ventana principal del predictor de resistencia de hormigón."""
    
    def __init__(self):
        """Inicializar la ventana principal."""
        super().__init__()
        
        # Inicializar modelo
        self.model_handler = ConcreteModelHandler()
        
        # Variables de estado
        self.current_prediction = None
        self.prediction_history = []
        
        # Configurar ventana
        self._setup_window()
        self._setup_ui()
        self._setup_connections()
        self._apply_styles()
        
        # Inicializar con valores por defecto
        self._load_default_values()
        
        logger.info("Ventana principal inicializada")
    
    def _setup_window(self):
        """Configurar propiedades de la ventana principal."""
        self.setWindowTitle("Predictor de Resistencia de Hormigón - v1.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Centrar ventana en pantalla
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def _setup_ui(self):
        """Configurar la interfaz de usuario."""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Splitter principal
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Panel izquierdo (controles)
        left_panel = self._create_left_panel()
        main_splitter.addWidget(left_panel)
        
        # Panel derecho (resultados y gráficos)
        right_panel = self._create_right_panel()
        main_splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        main_splitter.setSizes([400, 800])
        
        # Configurar menú y barra de estado
        self._setup_menu_bar()
        self._setup_status_bar()
    
    def _create_left_panel(self) -> QWidget:
        """Crear panel izquierdo con controles de entrada."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        
        # Título
        title_label = QLabel("Parámetros de la Mezcla")
        title_label.setProperty("labelType", "title")
        layout.addWidget(title_label)
        
        # Scroll area para los controles
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(12)
        
        # Grupo: Materiales Cementícios
        cement_group = QGroupBox("Materiales Cementícios")
        cement_layout = QVBoxLayout(cement_group)
        
        # Crear sliders para materiales cementícios
        self.cemento_slider = SliderSpinBoxWidget(
            "Cemento", 150, 500, 280, suffix="kg/m³",
            tooltip="Cantidad de cemento Portland en la mezcla"
        )
        
        self.escoria_slider = SliderSpinBoxWidget(
            "Escoria de Alto Horno", 0, 300, 0, suffix="kg/m³",
            tooltip="Material puzolánicos que mejora la durabilidad"
        )
        
        self.ceniza_slider = SliderSpinBoxWidget(
            "Ceniza Volante", 0, 200, 0, suffix="kg/m³",
            tooltip="Subproducto que mejora la trabajabilidad"
        )
        
        cement_layout.addWidget(self.cemento_slider)
        cement_layout.addWidget(self.escoria_slider)
        cement_layout.addWidget(self.ceniza_slider)
        controls_layout.addWidget(cement_group)
        
        # Grupo: Agua y Aditivos
        water_group = QGroupBox("Agua y Aditivos")
        water_layout = QVBoxLayout(water_group)
        
        self.agua_slider = SliderSpinBoxWidget(
            "Agua", 130, 220, 175, suffix="kg/m³",
            tooltip="Agua de mezclado, afecta la relación A/C"
        )
        
        self.superplast_slider = SliderSpinBoxWidget(
            "Superplastificante", 0, 25, 2.5, decimals=1, suffix="kg/m³",
            tooltip="Aditivo que mejora la trabajabilidad"
        )
        
        water_layout.addWidget(self.agua_slider)
        water_layout.addWidget(self.superplast_slider)
        controls_layout.addWidget(water_group)
        
        # Grupo: Agregados
        aggregates_group = QGroupBox("Agregados")
        aggregates_layout = QVBoxLayout(aggregates_group)
        
        self.agregado_grueso_slider = SliderSpinBoxWidget(
            "Agregado Grueso", 850, 1100, 975, suffix="kg/m³",
            tooltip="Grava o piedra triturada"
        )
        
        self.agregado_fino_slider = SliderSpinBoxWidget(
            "Agregado Fino", 650, 900, 775, suffix="kg/m³",
            tooltip="Arena natural o manufacturada"
        )
        
        aggregates_layout.addWidget(self.agregado_grueso_slider)
        aggregates_layout.addWidget(self.agregado_fino_slider)
        controls_layout.addWidget(aggregates_group)
        
        # Grupo: Tiempo de Curado
        time_group = QGroupBox("Tiempo de Curado")
        time_layout = QVBoxLayout(time_group)
        
        self.edad_slider = SliderSpinBoxWidget(
            "Edad del Ensayo", 1, 365, 28, suffix="días",
            tooltip="Días transcurridos desde el vaciado"
        )
        
        time_layout.addWidget(self.edad_slider)
        controls_layout.addWidget(time_group)
        
        # Presets y controles
        presets_group = QGroupBox("Mezclas Predefinidas")
        presets_layout = QVBoxLayout(presets_group)
        
        self.presets_combo = QComboBox()
        self.presets_combo.addItems(["Seleccionar mezcla..."] + 
                                  list(self.model_handler.get_preset_mixes().keys()))
        presets_layout.addWidget(self.presets_combo)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.predict_button = QPushButton("🔍 Predecir Resistencia")
        self.predict_button.setProperty("buttonType", "success")
        
        self.reset_button = QPushButton("🔄 Restablecer")
        self.reset_button.setProperty("buttonType", "secondary")
        
        buttons_layout.addWidget(self.predict_button)
        buttons_layout.addWidget(self.reset_button)
        presets_layout.addLayout(buttons_layout)
        
        controls_layout.addWidget(presets_group)
        controls_layout.addStretch()
        
        scroll.setWidget(controls_widget)
        layout.addWidget(scroll)
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """Crear panel derecho con resultados y gráficos."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(16)
        
        # Tabs para diferentes vistas
        self.tabs = QTabWidget()
        
        # Tab 1: Resultados principales
        results_tab = self._create_results_tab()
        self.tabs.addTab(results_tab, "📊 Resultados")
        
        # Tab 2: Análisis avanzado
        analysis_tab = self._create_analysis_tab()
        self.tabs.addTab(analysis_tab, "🔬 Análisis")
        
        # Tab 3: Historial
        history_tab = self._create_history_tab()
        self.tabs.addTab(history_tab, "📋 Historial")
        
        layout.addWidget(self.tabs)
        
        return panel
    
    def _create_results_tab(self) -> QWidget:
        """Crear tab de resultados principales."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Sección superior: Resultado principal
        result_section = QFrame()
        result_section.setProperty("frameType", "card")
        result_layout = QHBoxLayout(result_section)
        
        # Gauge circular
        self.gauge = CircularGauge(0, 600, 0, "Resistencia Predicha")
        result_layout.addWidget(self.gauge)
        
        # Información adicional
        info_layout = QVBoxLayout()
        
        # Cards de información en cuadrícula 2x2 ESTÉTICA
        cards_layout = QGridLayout()
        cards_layout.setSpacing(12)  # Más espacio entre cards
        
        self.resistance_card = StatusCard(
            "Resistencia Predicha", "-- kg/cm²", "Esperando predicción..."
        )
        
        self.nec_card = StatusCard(
            "Clasificación NEC", "-- ", "Según normas ecuatorianas"
        )
        
        self.wc_ratio_card = StatusCard(
            "Relación A/C", "--", "Agua/Cemento"
        )
        
        self.confidence_card = StatusCard(
            "Confianza", "--%", "Fiabilidad del modelo"
        )
        
        # Organizar en cuadrícula 2x2 estética:
        # Fila 1: Resistencia | Clasificación NEC  
        # Fila 2: Relación A/C | Confianza
        cards_layout.addWidget(self.resistance_card, 0, 0)    # Fila 0, Columna 0
        cards_layout.addWidget(self.nec_card, 0, 1)           # Fila 0, Columna 1
        cards_layout.addWidget(self.wc_ratio_card, 1, 0)      # Fila 1, Columna 0
        cards_layout.addWidget(self.confidence_card, 1, 1)    # Fila 1, Columna 1
        
        # Crear widget contenedor para el grid
        cards_widget = QWidget()
        cards_widget.setLayout(cards_layout)
        info_layout.addWidget(cards_widget)
        info_layout.addStretch()
        
        result_layout.addLayout(info_layout)
        
        layout.addWidget(result_section)
        
        # Sección inferior: Gráficos
        charts_section = QFrame()
        charts_section.setProperty("frameType", "card")
        charts_layout = QVBoxLayout(charts_section)
        
        # Crear figura de matplotlib
        self.results_figure = Figure(figsize=(10, 6), facecolor='white')
        self.results_canvas = FigureCanvas(self.results_figure)
        charts_layout.addWidget(self.results_canvas)
        
        layout.addWidget(charts_section)
        
        return tab
    
    def _create_analysis_tab(self) -> QWidget:
        """Crear tab de análisis avanzado."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Información del modelo
        model_info_frame = QFrame()
        model_info_frame.setProperty("frameType", "card")
        model_layout = QVBoxLayout(model_info_frame)
        
        info_label = QLabel("Información del Modelo")
        info_label.setProperty("labelType", "subtitle")
        model_layout.addWidget(info_label)
        
        # Crear cards de información del modelo
        model_info = self.model_handler.get_model_info()
        model_cards_layout = QHBoxLayout()
        
        self.r2_card = StatusCard(
            "R² Score", f"{model_info.get('r2_score', 0):.4f}",
            "Coeficiente de determinación"
        )
        
        self.mae_card = StatusCard(
            "MAE", f"{model_info.get('mae_kg_cm2', 0):.2f} kg/cm²",
            "Error absoluto medio"
        )
        
        self.cv_card = StatusCard(
            "CV Score", f"{model_info.get('cv_score_mean', 0):.4f}",
            "Validación cruzada"
        )
        
        model_cards_layout.addWidget(self.r2_card)
        model_cards_layout.addWidget(self.mae_card)
        model_cards_layout.addWidget(self.cv_card)
        
        model_layout.addLayout(model_cards_layout)
        layout.addWidget(model_info_frame)
        
        # Gráfico de feature importance
        importance_frame = QFrame()
        importance_frame.setProperty("frameType", "card")
        importance_layout = QVBoxLayout(importance_frame)
        
        importance_label = QLabel("Importancia de Variables")
        importance_label.setProperty("labelType", "subtitle")
        importance_layout.addWidget(importance_label)
        
        self.importance_figure = Figure(figsize=(10, 6), facecolor='white')
        self.importance_canvas = FigureCanvas(self.importance_figure)
        importance_layout.addWidget(self.importance_canvas)
        
        layout.addWidget(importance_frame)
        
        # Crear gráfico de importancia inicial
        self._plot_feature_importance()
        
        return tab
    
    def _create_history_tab(self) -> QWidget:
        """Crear tab de historial de predicciones."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)
        
        # Controles superiores
        controls_layout = QHBoxLayout()
        
        history_label = QLabel("Historial de Predicciones")
        history_label.setProperty("labelType", "subtitle")
        controls_layout.addWidget(history_label)
        
        controls_layout.addStretch()
        
        # Botones de exportación
        self.export_csv_button = QPushButton("📁 Exportar CSV")
        self.export_csv_button.setProperty("buttonType", "secondary")
        
        self.clear_history_button = QPushButton("🗑️ Limpiar Historial")
        self.clear_history_button.setProperty("buttonType", "warning")
        
        controls_layout.addWidget(self.export_csv_button)
        controls_layout.addWidget(self.clear_history_button)
        
        layout.addLayout(controls_layout)
        
        # Tabla de historial
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(10)
        
        headers = [
            "Fecha/Hora", "Resistencia (kg/cm²)", "Cemento", "Agua", 
            "Escoria", "Ceniza V.", "Superplast.", "A. Grueso", 
            "A. Fino", "Edad (días)"
        ]
        self.history_table.setHorizontalHeaderLabels(headers)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSortingEnabled(True)
        
        layout.addWidget(self.history_table)
        
        return tab
    
    def _setup_menu_bar(self):
        """Configurar barra de menú."""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Nuevo análisis
        new_action = QAction("&Nueva Predicción", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._reset_inputs)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # Exportar
        export_action = QAction("&Exportar Historial", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_history)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Salir
        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        # Actualizar gráficos
        refresh_action = QAction("&Actualizar Gráficos", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_charts)
        view_menu.addAction(refresh_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        
        # Acerca de
        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_status_bar(self):
        """Configurar barra de estado."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Información del modelo
        model_info = self.model_handler.get_model_info()
        model_status = f"Modelo: {model_info.get('tipo_modelo', 'N/A')} v{model_info.get('version', 'N/A')}"
        accuracy_status = f"Precisión: R²={model_info.get('r2_score', 0):.3f}"
        
        self.status_bar.addWidget(QLabel(model_status))
        self.status_bar.addPermanentWidget(QLabel(accuracy_status))
        self.status_bar.showMessage("Listo para predicción")
    
    def _setup_connections(self):
        """Configurar conexiones de señales."""
        # Conectar sliders a función de actualización
        self.cemento_slider.valueChanged.connect(self._on_input_changed)
        self.escoria_slider.valueChanged.connect(self._on_input_changed)
        self.ceniza_slider.valueChanged.connect(self._on_input_changed)
        self.agua_slider.valueChanged.connect(self._on_input_changed)
        self.superplast_slider.valueChanged.connect(self._on_input_changed)
        self.agregado_grueso_slider.valueChanged.connect(self._on_input_changed)
        self.agregado_fino_slider.valueChanged.connect(self._on_input_changed)
        self.edad_slider.valueChanged.connect(self._on_input_changed)
        
        # Conectar botones
        self.predict_button.clicked.connect(self._predict_strength)
        self.reset_button.clicked.connect(self._reset_inputs)
        
        # Conectar presets
        self.presets_combo.currentTextChanged.connect(self._load_preset)
        
        # Conectar botones de historial
        self.export_csv_button.clicked.connect(self._export_history)
        self.clear_history_button.clicked.connect(self._clear_history)
    
    def _apply_styles(self):
        """Aplicar estilos personalizados."""
        self.setStyleSheet(get_complete_stylesheet())
    
    def _load_default_values(self):
        """Cargar valores por defecto."""
        # Cargar preset C25 como valor inicial
        presets = self.model_handler.get_preset_mixes()
        if "C25 - Estructural" in presets:
            self._apply_preset_values(presets["C25 - Estructural"])
            self.presets_combo.setCurrentText("C25 - Estructural")
    
    def _on_input_changed(self):
        """Manejar cambios en los inputs.""" 
        # SOLO cambiar preset, NO actualizar cards automáticamente
        # (para evitar que sobrescriba las predicciones)
        
        # Cambiar estado del preset a personalizado si se modifica
        if self.presets_combo.currentText() != "Seleccionar mezcla...":
            self.presets_combo.blockSignals(True)
            self.presets_combo.setCurrentIndex(0)
            self.presets_combo.blockSignals(False)
        
        # Actualizar solo el status bar con info básica
        agua = self.agua_slider.get_value()
        cemento = self.cemento_slider.get_value()
        if cemento > 0:
            wc_ratio = agua / cemento
            self.status_bar.showMessage(f"Relación A/C: {wc_ratio:.3f} - Hacer clic en 'Predecir' para ver resultados")
    
    def _load_preset(self, preset_name: str):
        """Cargar valores de preset seleccionado."""
        if preset_name == "Seleccionar mezcla...":
            return
        
        presets = self.model_handler.get_preset_mixes()
        if preset_name in presets:
            values = presets[preset_name]
            self._apply_preset_values(values)
    
    def _apply_preset_values(self, values: Dict[str, float]):
        """Aplicar valores de preset a los sliders."""
        self.cemento_slider.set_value(values.get('Cemento_kg_m3', 280))
        self.escoria_slider.set_value(values.get('Escoria_Alto_Horno_kg_m3', 0))
        self.ceniza_slider.set_value(values.get('Ceniza_Volante_kg_m3', 0))
        self.agua_slider.set_value(values.get('Agua_kg_m3', 175))
        self.superplast_slider.set_value(values.get('Superplastificante_kg_m3', 2.5))
        self.agregado_grueso_slider.set_value(values.get('Agregado_Grueso_kg_m3', 975))
        self.agregado_fino_slider.set_value(values.get('Agregado_Fino_kg_m3', 775))
        self.edad_slider.set_value(values.get('Edad_dias', 28))
    
    def _get_current_inputs(self) -> Dict[str, float]:
        """Obtener valores actuales de entrada."""
        return {
            'Cemento_kg_m3': self.cemento_slider.get_value(),
            'Escoria_Alto_Horno_kg_m3': self.escoria_slider.get_value(),
            'Ceniza_Volante_kg_m3': self.ceniza_slider.get_value(),
            'Agua_kg_m3': self.agua_slider.get_value(),
            'Superplastificante_kg_m3': self.superplast_slider.get_value(),
            'Agregado_Grueso_kg_m3': self.agregado_grueso_slider.get_value(),
            'Agregado_Fino_kg_m3': self.agregado_fino_slider.get_value(),
            'Edad_dias': self.edad_slider.get_value()
        }
    
    def _predict_strength(self):
        """Realizar predicción de resistencia."""
        print("DEBUG: BUTTON CLICKED - Iniciando prediccion...")
        
        try:
            # Forzar actualización de status
            self.status_bar.showMessage("Realizando predicción...")
            self.status_bar.repaint()  # Forzar actualización visual
            
            # Obtener inputs actuales
            inputs = self._get_current_inputs()
            print(f"DEBUG: Inputs obtenidos: {inputs}")
            
            # Realizar predicción
            result = self.model_handler.predict_strength(inputs)
            self.current_prediction = result
            print(f"DEBUG: Resultado prediccion: {result['resistencia_predicha_kg_cm2']:.2f}")
            
            # FORZAR actualización de UI inmediatamente
            resistance = result['resistencia_predicha_kg_cm2']
            
            # Actualizar gauge directamente SIN ANIMACION
            print("DEBUG: Actualizando gauge directamente...")
            self.gauge.set_value(resistance, animate=False)
            self.gauge.repaint()
            
            # Actualizar cards directamente
            print("DEBUG: Actualizando resistance card...")
            self.resistance_card.update_values(
                f"{resistance:.2f} kg/cm²",
                f"Edad: {result['edad_ensayo_dias']} días"
            )
            self.resistance_card.repaint()
            
            print("DEBUG: Actualizando NEC card...")
            self.nec_card.update_values(
                result['clasificacion_nec'],
                result['descripcion_nec']
            )
            self.nec_card.repaint()
            
            print("DEBUG: Actualizando W/C ratio card...")
            self.wc_ratio_card.update_values(
                f"{result['relacion_agua_cemento']:.3f}",
                "Agua/Cemento"
            )
            self.wc_ratio_card.repaint()
            
            print("DEBUG: Actualizando confidence card...")
            confidence_pct = result['confianza_prediccion'] * 100
            self.confidence_card.update_values(
                f"{confidence_pct:.1f}%",
                "Fiabilidad del modelo"
            )
            self.confidence_card.repaint()
            
            # Actualizar historial
            print("DEBUG: Agregando al historial...")
            self._add_to_history(inputs, result)
            
            # Actualizar gráficos
            print("DEBUG: Actualizando graficos...")
            self._plot_results_charts()
            
            # Forzar actualización completa de la ventana
            self.update()
            self.repaint()
            
            print("DEBUG: Prediccion completada exitosamente")
            self.status_bar.showMessage(f"Prediccion completada: {resistance:.2f} kg/cm²")
            
        except Exception as e:
            print(f"DEBUG: ERROR en prediccion: {e}")
            import traceback
            traceback.print_exc()
            
            error_msg = str(e)
            logger.error(f"Error en predicción: {e}")
            
            # Mensajes de error más específicos
            if "Singular matrix" in error_msg:
                error_msg = "Error matemático: Verifique que los valores estén en rangos válidos"
            elif "numpy" in error_msg.lower():
                error_msg = "Error de cálculo: Algunos valores pueden estar fuera de rango"
            
            QMessageBox.critical(self, "Error", f"Error realizando predicción:\n{error_msg}")
            self.status_bar.showMessage("Error en predicción")
    
    def _update_results_ui(self, result: Dict[str, Any]):
        """Actualizar interfaz con resultados."""
        print(f"DEBUG: Actualizando UI con resistencia: {result['resistencia_predicha_kg_cm2']}")
        resistance = result['resistencia_predicha_kg_cm2']
        
        # Actualizar gauge
        print("DEBUG: Actualizando gauge...")
        self.gauge.set_value(resistance)
        
        # Actualizar cards
        print("DEBUG: Actualizando cards...")
        self.resistance_card.update_values(
            f"{resistance:.2f} kg/cm²",
            f"Edad: {result['edad_ensayo_dias']} días"
        )
        
        self.nec_card.update_values(
            result['clasificacion_nec'],
            result['descripcion_nec']
        )
        
        self.wc_ratio_card.update_values(
            f"{result['relacion_agua_cemento']:.3f}",
            "Agua/Cemento"
        )
        
        confidence_pct = result['confianza_prediccion'] * 100
        self.confidence_card.update_values(
            f"{confidence_pct:.1f}%",
            "Fiabilidad del modelo"
        )
        print("DEBUG: UI actualizada completamente")
    
    def _add_to_history(self, inputs: Dict[str, float], result: Dict[str, Any]):
        """Agregar predicción al historial."""
        history_item = {
            'timestamp': result['timestamp'],
            'resistance': result['resistencia_predicha_kg_cm2'],
            **inputs
        }
        
        self.prediction_history.append(history_item)
        self._update_history_table()
    
    def _update_history_table(self):
        """Actualizar tabla de historial."""
        self.history_table.setRowCount(len(self.prediction_history))
        
        for row, item in enumerate(self.prediction_history):
            # Timestamp
            self.history_table.setItem(row, 0, 
                QTableWidgetItem(item['timestamp'][:19]))  # Sin microsegundos
            
            # Resistencia
            self.history_table.setItem(row, 1, 
                QTableWidgetItem(f"{item['resistance']:.2f}"))
            
            # Parámetros
            params = [
                item['Cemento_kg_m3'],
                item['Agua_kg_m3'],
                item['Escoria_Alto_Horno_kg_m3'],
                item['Ceniza_Volante_kg_m3'],
                item['Superplastificante_kg_m3'],
                item['Agregado_Grueso_kg_m3'],
                item['Agregado_Fino_kg_m3'],
                item['Edad_dias']
            ]
            
            for col, param in enumerate(params, start=2):
                self.history_table.setItem(row, col, 
                    QTableWidgetItem(str(param)))
        
        # Ajustar columnas
        self.history_table.resizeColumnsToContents()
    
    def _plot_results_charts(self):
        """Crear gráficos de resultados - ULTRA SIMPLIFICADO SIN ERRORES."""
        if not self.current_prediction:
            return
            
        try:
            # Limpiar figura completamente
            self.results_figure.clear()
            
            # Crear UN SOLO gráfico simple
            ax = self.results_figure.add_subplot(111)
            
            # Datos simples de clasificación NEC
            current_resistance = self.current_prediction['resistencia_predicha_kg_cm2']
            
            # Rangos NEC básicos
            ranges = [140, 280, 420, 600]
            labels = ['Baja\n<140', 'Normal\n140-280', 'Alta\n280-420', 'Ultra\n>420']
            colors = ['#ef4444', '#f97316', '#22c55e', '#3b82f6']
            
            # Gráfico de barras simple
            bars = ax.bar(labels, ranges, color=colors, alpha=0.7, width=0.6)
            
            # Línea de resistencia actual
            ax.axhline(y=current_resistance, color='black', linestyle='--', linewidth=3, 
                      label=f'Predicción: {current_resistance:.1f} kg/cm²')
            
            # Configuración básica
            ax.set_ylabel('Resistencia (kg/cm²)', fontsize=12)
            ax.set_title('Clasificación NEC Ecuador', fontsize=14, pad=20)
            ax.set_ylim(0, 700)
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Layout simple sin tight_layout que puede causar errores
            self.results_figure.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.15)
            
            # Redibujar
            self.results_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error en graficos - se omite visualizacion: {e}")
            # Crear texto simple si fallan los gráficos
            try:
                self.results_figure.clear()
                ax = self.results_figure.add_subplot(111)
                ax.text(0.5, 0.5, f'Resistencia: {current_resistance:.2f} kg/cm²', 
                       ha='center', va='center', fontsize=16, 
                       transform=ax.transAxes)
                ax.set_title('Resultado de Predicción')
                ax.axis('off')
                self.results_canvas.draw()
            except:
                pass  # Si todo falla, simplemente omitir gráficos
    
    def _plot_feature_importance(self):
        """Crear gráfico de importancia de variables - SIMPLIFICADO."""
        try:
            importance = self.model_handler.get_feature_importance()
            
            if not importance:
                return
            
            self.importance_figure.clear()
            ax = self.importance_figure.add_subplot(111)
            
            # Solo tomar las 6 más importantes para evitar aglomeración
            items = list(importance.items())[:6]
            features = [item[0] for item in items]
            values = [item[1] for item in items]
            
            # Gráfico horizontal simple
            bars = ax.barh(features, values, color='#2563eb', alpha=0.7)
            ax.set_xlabel('Importancia', fontsize=12)
            ax.set_title('Variables Más Importantes', fontsize=14)
            ax.grid(True, axis='x', alpha=0.3)
            
            # Layout simple
            self.importance_figure.subplots_adjust(left=0.25, right=0.95, top=0.9, bottom=0.1)
            
            # Redibujar
            self.importance_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error en grafico importancia - se omite: {e}")
            # Si falla, crear texto simple
            try:
                self.importance_figure.clear()
                ax = self.importance_figure.add_subplot(111)
                ax.text(0.5, 0.5, 'Gráfico de importancia\nno disponible', 
                       ha='center', va='center', fontsize=14, 
                       transform=ax.transAxes)
                ax.axis('off')
                self.importance_canvas.draw()
            except:
                pass
    
    def _reset_inputs(self):
        """Restablecer inputs a valores por defecto."""
        self._load_default_values()
        self.status_bar.showMessage("Valores restablecidos")
    
    def _refresh_charts(self):
        """Actualizar todos los gráficos."""
        if self.current_prediction:
            self._plot_results_charts()
        self._plot_feature_importance()
        self.status_bar.showMessage("Gráficos actualizados")
    
    def _export_history(self):
        """Exportar historial a CSV."""
        if not self.prediction_history:
            QMessageBox.information(self, "Información", 
                                  "No hay datos en el historial para exportar.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Guardar Historial", "historial_predicciones.csv",
            "CSV files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                df = pd.DataFrame(self.prediction_history)
                df.to_csv(filename, index=False)
                QMessageBox.information(self, "Éxito", 
                                      f"Historial exportado exitosamente a:\n{filename}")
                self.status_bar.showMessage(f"✅ Historial exportado: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando historial:\n{str(e)}")
    
    def _clear_history(self):
        """Limpiar historial de predicciones."""
        reply = QMessageBox.question(self, "Confirmar", 
                                   "¿Está seguro de que desea limpiar todo el historial?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.prediction_history.clear()
            self._update_history_table()
            self.status_bar.showMessage("Historial limpiado")
    
    def _show_about(self):
        """Mostrar diálogo Acerca de."""
        model_info = self.model_handler.get_model_info()
        about_text = f"""
        <h3>Predictor de Resistencia de Hormigón v1.0</h3>
        <p>Aplicación profesional para predecir la resistencia a compresión del hormigón 
        basada en modelos de Machine Learning.</p>
        
        <h4>Información del Modelo:</h4>
        <ul>
        <li><b>Tipo:</b> {model_info.get('tipo_modelo', 'N/A')}</li>
        <li><b>Versión:</b> {model_info.get('version', 'N/A')}</li>
        <li><b>Fecha de entrenamiento:</b> {model_info.get('fecha_entrenamiento', 'N/A')}</li>
        <li><b>Precisión (R²):</b> {model_info.get('r2_score', 0):.4f}</li>
        <li><b>Error promedio:</b> {model_info.get('mae_kg_cm2', 0):.2f} kg/cm²</li>
        </ul>
        
        <h4>Tecnologías:</h4>
        <ul>
        <li>PyQt6 - Interfaz gráfica</li>
        <li>Scikit-learn - Machine Learning</li>
        <li>Matplotlib - Visualizaciones</li>
        <li>Pandas - Manejo de datos</li>
        </ul>
        
        <p><i>Desarrollado con Claude Code</i></p>
        """
        
        QMessageBox.about(self, "Acerca de", about_text)