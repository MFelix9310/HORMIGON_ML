#!/usr/bin/env python3
"""
Componentes de Interfaz Reutilizables
====================================

Este módulo contiene componentes de UI personalizados y reutilizables
para la aplicación de predicción de hormigón.
"""

from typing import Callable, Optional, Tuple, Any
import math

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QSlider, QSpinBox, QDoubleSpinBox, QLabel, QPushButton,
                           QFrame, QProgressBar, QTextEdit, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPolygonF
from PyQt6.QtCore import QPointF, QRectF
import logging

logger = logging.getLogger(__name__)


class SliderSpinBoxWidget(QWidget):
    """Widget que combina QSlider y QSpinBox sincronizados."""
    
    valueChanged = pyqtSignal(float)
    
    def __init__(self, label: str, min_val: float, max_val: float, 
                 initial_val: float, decimals: int = 0, suffix: str = "", 
                 tooltip: str = ""):
        """
        Inicializar widget slider-spinbox.
        
        Args:
            label: Texto de la etiqueta
            min_val: Valor mínimo
            max_val: Valor máximo
            initial_val: Valor inicial
            decimals: Número de decimales (0 para entero)
            suffix: Sufijo para el valor (ej: "kg/m³")
            tooltip: Tooltip informativo
        """
        super().__init__()
        self.decimals = decimals
        self.multiplier = 10 ** decimals
        self.min_val = min_val
        self.max_val = max_val
        
        self._setup_ui(label, min_val, max_val, initial_val, suffix, tooltip)
        self._connect_signals()
        
        # Establecer valor inicial
        self.set_value(initial_val)
    
    def _setup_ui(self, label: str, min_val: float, max_val: float, 
                  initial_val: float, suffix: str, tooltip: str):
        """Configurar la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Etiqueta principal
        self.label = QLabel(label)
        self.label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.label.setStyleSheet("color: #374151; margin-bottom: 4px;")
        layout.addWidget(self.label)
        
        # Layout horizontal para slider y spinbox
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(12)
        
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(int(min_val * self.multiplier))
        self.slider.setMaximum(int(max_val * self.multiplier))
        self.slider.setValue(int(initial_val * self.multiplier))
        self.slider.setStyleSheet(self._get_slider_style())
        
        # SpinBox (doble o entero según decimales)
        if self.decimals > 0:
            self.spinbox = QDoubleSpinBox()
            self.spinbox.setDecimals(self.decimals)
        else:
            self.spinbox = QSpinBox()
        
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)
        self.spinbox.setValue(initial_val)
        self.spinbox.setSuffix(f" {suffix}" if suffix else "")
        self.spinbox.setMinimumWidth(120)
        self.spinbox.setStyleSheet(self._get_spinbox_style())
        
        controls_layout.addWidget(self.slider, 2)
        controls_layout.addWidget(self.spinbox, 1)
        
        layout.addLayout(controls_layout)
        
        # Etiqueta de rango
        range_label = QLabel(f"Rango: {min_val} - {max_val} {suffix}")
        range_label.setStyleSheet("color: #6b7280; font-size: 9pt;")
        layout.addWidget(range_label)
        
        # Tooltip
        if tooltip:
            self.setToolTip(tooltip)
    
    def _get_slider_style(self) -> str:
        """Obtener estilo personalizado para el slider."""
        return """
        QSlider::groove:horizontal {
            border: 1px solid #d1d5db;
            height: 6px;
            background: #f3f4f6;
            border-radius: 3px;
        }
        
        QSlider::handle:horizontal {
            background: #2563eb;
            border: 2px solid #1d4ed8;
            width: 20px;
            height: 20px;
            margin: -8px 0;
            border-radius: 10px;
        }
        
        QSlider::handle:horizontal:hover {
            background: #1d4ed8;
            border: 2px solid #1e40af;
        }
        
        QSlider::sub-page:horizontal {
            background: #3b82f6;
            border: 1px solid #2563eb;
            height: 6px;
            border-radius: 3px;
        }
        """
    
    def _get_spinbox_style(self) -> str:
        """Obtener estilo personalizado para el spinbox."""
        return """
        QSpinBox, QDoubleSpinBox {
            border: 2px solid #d1d5db;
            border-radius: 6px;
            padding: 6px 8px;
            font-size: 11pt;
            background: white;
        }
        
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 2px solid #2563eb;
            background: #fefefe;
        }
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            subcontrol-origin: border;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #d1d5db;
            border-bottom: 1px solid #d1d5db;
            border-top-right-radius: 4px;
            background: #f9fafb;
        }
        
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {
            background: #f3f4f6;
        }
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            subcontrol-origin: border;
            subcontrol-position: bottom right;
            width: 20px;
            border-left: 1px solid #d1d5db;
            border-top: 1px solid #d1d5db;
            border-bottom-right-radius: 4px;
            background: #f9fafb;
        }
        
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
            background: #f3f4f6;
        }
        """
    
    def _connect_signals(self):
        """Conectar señales para sincronizar slider y spinbox."""
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
    
    def _on_slider_changed(self, value: int):
        """Manejar cambio en el slider."""
        float_value = value / self.multiplier
        
        # Actualizar spinbox sin disparar su señal
        self.spinbox.blockSignals(True)
        
        # Usar tipo correcto según el tipo de spinbox
        if self.decimals > 0:
            # QDoubleSpinBox acepta float
            self.spinbox.setValue(float_value)
        else:
            # QSpinBox solo acepta int
            self.spinbox.setValue(int(float_value))
            
        self.spinbox.blockSignals(False)
        
        # Emitir señal de cambio
        self.valueChanged.emit(float_value)
    
    def _on_spinbox_changed(self, value: float):
        """Manejar cambio en el spinbox."""
        int_value = int(value * self.multiplier)
        
        # Actualizar slider sin disparar su señal
        self.slider.blockSignals(True)
        self.slider.setValue(int_value)
        self.slider.blockSignals(False)
        
        # Emitir señal de cambio
        self.valueChanged.emit(value)
    
    def set_value(self, value: float):
        """Establecer valor programáticamente."""
        value = max(self.min_val, min(self.max_val, value))
        
        self.slider.blockSignals(True)
        self.spinbox.blockSignals(True)
        
        self.slider.setValue(int(value * self.multiplier))
        
        # Usar tipo correcto según el tipo de spinbox
        if self.decimals > 0:
            # QDoubleSpinBox acepta float
            self.spinbox.setValue(value)
        else:
            # QSpinBox solo acepta int
            self.spinbox.setValue(int(value))
        
        self.slider.blockSignals(False)
        self.spinbox.blockSignals(False)
        
        self.valueChanged.emit(value)
    
    def get_value(self) -> float:
        """Obtener el valor actual."""
        return self.spinbox.value()


class CircularGauge(QWidget):
    """Widget de medidor circular para mostrar resistencia."""
    
    def __init__(self, min_value: float = 0, max_value: float = 600, 
                 value: float = 0, title: str = "Resistencia"):
        """
        Inicializar medidor circular.
        
        Args:
            min_value: Valor mínimo
            max_value: Valor máximo
            value: Valor actual
            title: Título del medidor
        """
        super().__init__()
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.title = title
        self.setMinimumSize(200, 200)
        
        # Configurar animación
        self.animation = QPropertyAnimation(self, b"value_animated")
        self.animation.setDuration(800)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._value_animated = value
    
    @property
    def value_animated(self) -> float:
        """Valor animado para interpolación."""
        return self._value_animated
    
    @value_animated.setter
    def value_animated(self, val: float):
        """Setter para valor animado."""
        self._value_animated = val
        self.update()
    
    def set_value(self, value: float, animate: bool = True):
        """
        Establecer valor del medidor.
        
        Args:
            value: Nuevo valor
            animate: Si animar la transición
        """
        value = max(self.min_value, min(self.max_value, value))
        
        if animate:
            self.animation.setStartValue(self._value_animated)
            self.animation.setEndValue(value)
            self.animation.start()
        else:
            self._value_animated = value
            self.update()
            self.repaint()  # Forzar repintado inmediato
        
        self.value = value
    
    def paintEvent(self, event):
        """Pintar el medidor circular."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Obtener dimensiones
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 20
        
        # Colores según el valor
        if self._value_animated < 210:
            color = QColor("#ef4444")  # Rojo
            text_color = QColor("#dc2626")
        elif self._value_animated < 280:
            color = QColor("#f97316")  # Naranja
            text_color = QColor("#ea580c")
        elif self._value_animated < 420:
            color = QColor("#22c55e")  # Verde
            text_color = QColor("#16a34a")
        else:
            color = QColor("#3b82f6")  # Azul
            text_color = QColor("#2563eb")
        
        # Dibujar círculo exterior
        painter.setPen(QPen(QColor("#e5e7eb"), 8))
        painter.drawEllipse(center.x() - radius, center.y() - radius, 
                          radius * 2, radius * 2)
        
        # Dibujar arco de progreso
        start_angle = 225 * 16  # Comenzar desde abajo izquierda
        span_angle = -270 * 16  # Arco de 270 grados (sentido horario)
        
        # Calcular ángulo del valor actual
        progress = (self._value_animated - self.min_value) / (self.max_value - self.min_value)
        value_span = progress * span_angle
        
        painter.setPen(QPen(color, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(center.x() - radius, center.y() - radius, 
                       radius * 2, radius * 2, start_angle, int(value_span))
        
        # Dibujar valor central
        painter.setPen(QPen(text_color, 2))
        
        # Valor principal
        font_large = QFont("Segoe UI", 18, QFont.Weight.Bold)
        painter.setFont(font_large)
        value_text = f"{self._value_animated:.1f}"
        painter.drawText(rect.adjusted(0, -20, 0, 0), Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Unidades
        font_small = QFont("Segoe UI", 10)
        painter.setFont(font_small)
        painter.setPen(QPen(QColor("#6b7280"), 1))
        painter.drawText(rect.adjusted(0, 10, 0, 0), Qt.AlignmentFlag.AlignCenter, "kg/cm²")
        
        # Título
        font_title = QFont("Segoe UI", 12, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.setPen(QPen(QColor("#374151"), 1))
        painter.drawText(rect.adjusted(0, -radius - 30, 0, 0), Qt.AlignmentFlag.AlignCenter, self.title)


class StatusCard(QFrame):
    """Tarjeta de estado con información de métricas."""
    
    def __init__(self, title: str, value: str, subtitle: str = "", 
                 color: str = "#3b82f6"):
        """
        Inicializar tarjeta de estado.
        
        Args:
            title: Título de la tarjeta
            value: Valor principal
            subtitle: Subtítulo opcional
            color: Color del tema
        """
        super().__init__()
        self.title = title
        self.value = value
        self.subtitle = subtitle
        self.color = color
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configurar la interfaz de la tarjeta."""
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.setStyleSheet(f"""
        QFrame {{
            background-color: #ffffff;
            border: none;
            border-radius: 10px;
            padding: 20px;
            margin: 6px;
            min-height: 90px;
            min-width: 180px;
            max-width: 200px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        }}
        QFrame:hover {{
            background-color: #fafbfc;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
        }}
        QLabel {{
            background-color: transparent;
            border: none;
        }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        
        # Título
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Segoe UI", 9))
        title_label.setStyleSheet("color: #6b7280; font-weight: 500;")
        layout.addWidget(title_label)
        
        # Valor principal
        value_label = QLabel(self.value)
        value_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {self.color};")
        layout.addWidget(value_label)
        
        # Subtítulo
        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setFont(QFont("Segoe UI", 8))
            subtitle_label.setStyleSheet("color: #9ca3af;")
            layout.addWidget(subtitle_label)
    
    def update_values(self, value: str, subtitle: str = None):
        """Actualizar valores - RECREAR WIDGETS COMPLETAMENTE."""
        self.value = value
        if subtitle is not None:
            self.subtitle = subtitle
        
        print(f"RECREANDO StatusCard: value='{value}', subtitle='{subtitle}'")
        
        try:
            # LIMPIAR TODO EL LAYOUT
            layout = self.layout()
            
            # Eliminar todos los widgets existentes
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            # RECREAR WIDGETS DESDE CERO
            # Título - MINIMALISTA Y ELEGANTE  
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Medium))
            title_label.setStyleSheet("color: #6b7280; font-weight: 500; background: transparent; border: none; text-decoration: none;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            layout.addWidget(title_label)
            
            # Valor principal - TAMAÑO PROPORCIONADO Y ELEGANTE
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))  # Más pequeño y proporcionado
            value_label.setStyleSheet("color: #111827; font-weight: 600; margin: 4px 0; background: transparent; border: none; text-decoration: none;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            value_label.setWordWrap(True)
            layout.addWidget(value_label)
            
            # Subtitle si existe - DISCRETO Y MINIMALISTA
            if subtitle:
                subtitle_label = QLabel(subtitle) 
                subtitle_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Normal))
                subtitle_label.setStyleSheet("color: #9ca3af; font-weight: 400; background: transparent; border: none; text-decoration: none;")
                subtitle_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
                subtitle_label.setWordWrap(True)
                layout.addWidget(subtitle_label)
            
            # FORZAR ACTUALIZACIÓN COMPLETA
            self.adjustSize()
            self.updateGeometry() 
            self.update()
            self.repaint()
            
            print(f"RECREADO StatusCard completamente")
            
        except Exception as e:
            print(f"ERROR recreando StatusCard: {e}")
            import traceback
            traceback.print_exc()


class AnimatedProgressBar(QProgressBar):
    """Barra de progreso con animación personalizada."""
    
    def __init__(self, parent=None):
        """Inicializar barra de progreso animada."""
        super().__init__(parent)
        self.setStyleSheet("""
        QProgressBar {
            border: 2px solid #e5e7eb;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            background: #f9fafb;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                       stop:0 #3b82f6, stop:1 #1d4ed8);
            border-radius: 6px;
        }
        """)
    
    def set_value_animated(self, value: int, duration: int = 1000):
        """
        Establecer valor con animación.
        
        Args:
            value: Valor objetivo
            duration: Duración de la animación en ms
        """
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(duration)
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()


class LogTextEdit(QTextEdit):
    """Widget de texto para mostrar logs con formato."""
    
    def __init__(self, parent=None):
        """Inicializar widget de logs."""
        super().__init__(parent)
        self.setReadOnly(True)
        self.setMaximumHeight(150)
        self.setStyleSheet("""
        QTextEdit {
            background: #1f2937;
            color: #f9fafb;
            border: 1px solid #374151;
            border-radius: 6px;
            font-family: 'Consolas', monospace;
            font-size: 9pt;
            padding: 8px;
        }
        """)
    
    def add_log(self, message: str, level: str = "INFO"):
        """
        Agregar mensaje de log.
        
        Args:
            message: Mensaje a agregar
            level: Nivel del log (INFO, WARNING, ERROR)
        """
        color_map = {
            "INFO": "#3b82f6",
            "WARNING": "#f59e0b",
            "ERROR": "#ef4444",
            "SUCCESS": "#10b981"
        }
        
        color = color_map.get(level, "#f9fafb")
        timestamp = QTimer().remainingTime()
        
        html_message = f"""
        <span style="color: #6b7280;">[{level}]</span>
        <span style="color: {color};">{message}</span><br>
        """
        
        self.append(html_message)
        
        # Auto-scroll al final
        cursor = self.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.setTextCursor(cursor)