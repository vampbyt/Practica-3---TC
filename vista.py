from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QListWidget, 
                             QStackedWidget, QFrame, QLineEdit,
                             QScrollArea, QCheckBox, QTabWidget)
from PyQt6.QtCore import Qt

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Extractor de Datos - Regex")
        self.resize(850, 650)
        
        self.setStyleSheet("""
            QMainWindow { background-color: #F3E5F5; }
            #ContenedorPrincipal { border: 4px solid #7B1FA2; border-radius: 10px; background-color: #FAFAFA; margin: 5px; }
            QWidget { font-family: Arial; font-size: 11pt; color: #333333; } 
            QPushButton { background-color: #7B1FA2; color: white; font-weight: bold; border-radius: 5px; padding: 8px; }
            QPushButton:hover { background-color: #9C27B0; }
            QPushButton:disabled { background-color: #CE93D8; color: #757575; }
            QLineEdit, QTextEdit, QListWidget, QScrollArea { background-color: white; border: 2px solid #BA68C8; border-radius: 4px; padding: 4px; color: #000000; }
            QLabel { color: #4A148C; font-weight: bold; }
            QCheckBox { color: #333333; font-weight: bold; }
            QCheckBox::indicator { width: 18px; height: 18px; }
            QTabWidget::pane { border: 2px solid #7B1FA2; border-radius: 4px; background-color: white; }
            QTabBar::tab { background: #E1BEE7; border: 1px solid #7B1FA2; padding: 8px; border-top-left-radius: 4px; border-top-right-radius: 4px; color: #4A148C; font-weight: bold; }
            QTabBar::tab:selected { background: #7B1FA2; color: white; }
            QScrollBar:vertical { border: none; background: #F3E5F5; width: 14px; margin: 0px; border-radius: 7px; }
            QScrollBar::handle:vertical { background: #BA68C8; min-height: 30px; border-radius: 7px; }
            QScrollBar::handle:vertical:hover { background: #7B1FA2; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
            QScrollBar:horizontal { border: none; background: #F3E5F5; height: 14px; margin: 0px; border-radius: 7px; }
            QScrollBar::handle:horizontal { background: #BA68C8; min-width: 30px; border-radius: 7px; }
            QScrollBar::handle:horizontal:hover { background: #7B1FA2; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        """)
        self._iniciar_ui()

    def _iniciar_ui(self):
        contenedor_principal = QFrame()
        contenedor_principal.setObjectName("ContenedorPrincipal")
        layout_global = QVBoxLayout(contenedor_principal)

        layout_header = QHBoxLayout()
        self.titulo_practica = QLabel("Práctica 3: Expresiones Regulares en Python")
        self.titulo_practica.setStyleSheet("font-size: 16pt; color: #4A148C;")
        self.btn_inicio = QPushButton("Inicio")
        self.btn_inicio.setFixedWidth(100)
        self.btn_inicio.hide()
        
        layout_header.addWidget(self.titulo_practica)
        layout_header.addStretch()
        layout_header.addWidget(self.btn_inicio)
        layout_global.addLayout(layout_header)

        linea = QFrame()
        linea.setFrameShape(QFrame.Shape.HLine)
        linea.setStyleSheet("border: 1px solid #BA68C8;")
        layout_global.addWidget(linea)

        self.stacked_widget = QStackedWidget()
        layout_global.addWidget(self.stacked_widget)

        self.crear_pantalla_inicio()
        self.crear_pantalla_manual()
        self.crear_pantalla_archivo()
        self.crear_pantalla_resultados()

        self.setCentralWidget(contenedor_principal)

    def crear_pantalla_inicio(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitulo = QLabel("Desarrollado por: Angel Abraham Higuera Pineda")
        subtitulo.setStyleSheet("font-size: 12pt; margin-bottom: 30px;")
        subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout_botones = QHBoxLayout()
        self.btn_ir_manual = QPushButton("Agregar links a mano")
        self.btn_ir_manual.setMinimumHeight(60)
        self.btn_ir_archivo = QPushButton("Subir archivo TXT")
        self.btn_ir_archivo.setMinimumHeight(60)
        
        layout_botones.addWidget(self.btn_ir_manual)
        layout_botones.addWidget(self.btn_ir_archivo)

        layout.addWidget(subtitulo)
        layout.addLayout(layout_botones)
        self.stacked_widget.addWidget(pagina)

    def crear_pantalla_manual(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.addWidget(QLabel("Agrega los links que quieras procesar:"))

        self.layout_entradas_manuales = QVBoxLayout()
        self.entradas_manuales = []
        
        for i in range(4):
            le = QLineEdit()
            le.setPlaceholderText(f"URL {i+1}...")
            if i > 0:
                le.setEnabled(False)
            self.entradas_manuales.append(le)
            self.layout_entradas_manuales.addWidget(le)

        layout.addLayout(self.layout_entradas_manuales)

        self.btn_mas_manual = QPushButton("+ Desbloquear / Añadir más")
        self.btn_mas_manual.setStyleSheet("background-color: #BA68C8;")
        layout.addWidget(self.btn_mas_manual, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addStretch()
        self.btn_procesar_manual = QPushButton("Procesar Enlaces")
        layout.addWidget(self.btn_procesar_manual)
        self.stacked_widget.addWidget(pagina)

    def crear_pantalla_archivo(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.addWidget(QLabel("Enlaces cargados del archivo (Desactiva los que no quieras usar):"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        contenedor_scroll = QWidget()
        contenedor_scroll.setStyleSheet("background-color: white;") 
        
        self.layout_lista_archivo = QVBoxLayout(contenedor_scroll)
        scroll.setWidget(contenedor_scroll)
        layout.addWidget(scroll)

        self.btn_procesar_archivo = QPushButton("Procesar Enlaces Seleccionados")
        layout.addWidget(self.btn_procesar_archivo)
        self.stacked_widget.addWidget(pagina)

    def crear_pantalla_resultados(self):
        pagina = QWidget()
        layout = QHBoxLayout(pagina)

        panel_izq = QVBoxLayout()
        panel_izq.addWidget(QLabel("Links Procesados:"))
        self.lista_resultados = QListWidget()
        self.lista_resultados.setFixedWidth(250)
        panel_izq.addWidget(self.lista_resultados)
        
        panel_der = QVBoxLayout()
        panel_der.addWidget(QLabel("Contenido de Archivos Generados:"))

        # --- NUEVO: Etiquetas de Resumen de Totales ---
        self.layout_resumen = QHBoxLayout()
        self.lbl_resumen_correos = QLabel("Total Correos: 0")
        self.lbl_resumen_links = QLabel("Total Links: 0")
        self.lbl_resumen_fechas = QLabel("Total Fechas: 0")
        
        estilo_resumen = "color: #9C27B0; font-weight: bold; background: #F3E5F5; padding: 5px; border-radius: 4px;"
        self.lbl_resumen_correos.setStyleSheet(estilo_resumen)
        self.lbl_resumen_links.setStyleSheet(estilo_resumen)
        self.lbl_resumen_fechas.setStyleSheet(estilo_resumen)
        
        self.layout_resumen.addWidget(self.lbl_resumen_correos)
        self.layout_resumen.addWidget(self.lbl_resumen_links)
        self.layout_resumen.addWidget(self.lbl_resumen_fechas)
        panel_der.addLayout(self.layout_resumen)
        # ----------------------------------------------

        self.tabs = QTabWidget()
        self.txt_correos = QTextEdit()
        self.txt_correos.setReadOnly(True)
        self.txt_correos.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) 
        
        self.txt_links = QTextEdit()
        self.txt_links.setReadOnly(True)
        self.txt_links.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        self.txt_fechas = QTextEdit()
        self.txt_fechas.setReadOnly(True)
        self.txt_fechas.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

        self.tabs.addTab(self.txt_correos, "Correos")
        self.tabs.addTab(self.txt_links, "Links")
        self.tabs.addTab(self.txt_fechas, "Fechas")
        
        panel_der.addWidget(self.tabs)

        layout.addLayout(panel_izq)
        layout.addLayout(panel_der)
        self.stacked_widget.addWidget(pagina)