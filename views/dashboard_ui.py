from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header
        header = QLabel("Dashboard Principal")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(header)

        # KPI Cards Row
        kpi_layout = QHBoxLayout()
        kpi_layout.setSpacing(20)
        
        self.card_sales = self.create_kpi_card("Ventas del Día", "RD$ 45,230.00", "▲ 12%")
        self.card_orders = self.create_kpi_card("Total Facturas", "124", "▼ 3%")
        self.card_products = self.create_kpi_card("Productos Críticos", "8", "⚠ Stock Bajo")
        
        kpi_layout.addWidget(self.card_sales)
        kpi_layout.addWidget(self.card_orders)
        kpi_layout.addWidget(self.card_products)
        
        layout.addLayout(kpi_layout)

        # Charts Section
        chart_frame = QFrame()
        chart_frame.setStyleSheet("background-color: white; border-radius: 10px; border: 1px solid #ddd;")
        chart_layout = QVBoxLayout(chart_frame)
        
        chart_title = QLabel("Ventas por Hora (Tiempo Real)")
        chart_title.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        chart_layout.addWidget(chart_title)
        
        # Matplotlib Chart
        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.plot_chart()
        
        chart_layout.addWidget(self.canvas)
        layout.addWidget(chart_frame, 1) # Expand chart

        self.setLayout(layout)

    def create_kpi_card(self, title, value, footer):
        card = QFrame()
        card.setProperty("class", "Card") # For QSS
        
        layout = QVBoxLayout(card)
        
        lbl_title = QLabel(title)
        lbl_title.setProperty("class", "CardTitle")
        
        lbl_value = QLabel(value)
        lbl_value.setProperty("class", "CardValue")
        
        lbl_footer = QLabel(footer)
        lbl_footer.setStyleSheet("color: #27ae60; font-weight: bold;" if "▲" in footer else "color: #e74c3c; font-weight: bold;")
        
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        layout.addWidget(lbl_footer)
        
        return card

    def plot_chart(self):
        ax = self.figure.add_subplot(111)
        hours = ['8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM']
        sales = [random.randint(5000, 20000) for _ in range(len(hours))]
        
        bars = ax.bar(hours, sales, color='#3498db')
        ax.set_title('Ventas Diarias')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        self.canvas.draw()
