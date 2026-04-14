from PyQt6.QtWidgets import QFileDialog, QMessageBox, QHBoxLayout, QCheckBox, QLineEdit, QWidget
from PyQt6.QtCore import Qt

class Controlador:
    def __init__(self, vista, modelo):
        self.vista = vista
        self.modelo = modelo
        self.elementos_archivo = []
        self.conectar_botones()

    def conectar_botones(self):
        self.vista.btn_inicio.clicked.connect(self.ir_a_inicio)
        self.vista.btn_ir_manual.clicked.connect(self.ir_a_manual)
        self.vista.btn_ir_archivo.clicked.connect(self.cargar_y_mostrar_archivo)
        self.vista.btn_mas_manual.clicked.connect(self.desbloquear_campo)
        self.vista.btn_procesar_manual.clicked.connect(lambda: self.procesar("manual"))
        self.vista.btn_procesar_archivo.clicked.connect(lambda: self.procesar("archivo"))

    def ir_a_inicio(self):
        self.vista.stacked_widget.setCurrentIndex(0)
        self.vista.btn_inicio.hide()

    def ir_a_manual(self):
        self.vista.stacked_widget.setCurrentIndex(1)
        self.vista.btn_inicio.show()

    def desbloquear_campo(self):
        for le in self.vista.entradas_manuales:
            if not le.isEnabled():
                le.setEnabled(True)
                return
        
        nuevo_le = QLineEdit()
        nuevo_le.setPlaceholderText(f"URL {len(self.vista.entradas_manuales) + 1}...")
        self.vista.entradas_manuales.append(nuevo_le)
        self.vista.layout_entradas_manuales.addWidget(nuevo_le)

    def cargar_y_mostrar_archivo(self):
        ruta_archivo, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo TXT", "", "Text Files (*.txt)")
        
        if ruta_archivo:
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    urls = [linea.strip() for linea in f.readlines() if linea.strip()]
                
                for i in reversed(range(self.vista.layout_lista_archivo.count())): 
                    widget = self.vista.layout_lista_archivo.itemAt(i).widget()
                    if widget: widget.deleteLater()
                
                self.elementos_archivo.clear()

                for url in urls:
                    fila_widget = QWidget()
                    fila_layout = QHBoxLayout(fila_widget)
                    fila_layout.setContentsMargins(0,0,0,0)
                    
                    chk = QCheckBox()
                    chk.setChecked(True) 
                    le = QLineEdit(url)
                    
                    fila_layout.addWidget(chk)
                    fila_layout.addWidget(le)
                    self.vista.layout_lista_archivo.addWidget(fila_widget)
                    
                    self.elementos_archivo.append((chk, le))

                self.vista.stacked_widget.setCurrentIndex(2)
                self.vista.btn_inicio.show()
                
            except Exception as e:
                QMessageBox.critical(self.vista, "Error", f"No se pudo leer el archivo: {e}")

    def procesar(self, origen):
        urls_a_procesar = []
        
        if origen == "manual":
            for le in self.vista.entradas_manuales:
                if le.isEnabled() and le.text().strip():
                    urls_a_procesar.append(le.text().strip())
        elif origen == "archivo":
            for chk, le in self.elementos_archivo:
                if chk.isChecked() and le.text().strip():
                    urls_a_procesar.append(le.text().strip())

        if not urls_a_procesar:
            QMessageBox.warning(self.vista, "Atención", "No hay URLs válidas para procesar.")
            return

        resultados_finales = {}
        for url in urls_a_procesar:
            resultados_finales[url] = self.modelo.analizar_url(url)
            
        self.modelo.guardar_resultados(resultados_finales)

        total_c = sum(len(d["correos"]) for d in resultados_finales.values())
        total_l = sum(len(d["links"]) for d in resultados_finales.values())
        total_f = sum(len(d["fechas"]) for d in resultados_finales.values())

        self.vista.lbl_resumen_correos.setText(f"Total Correos: {total_c}")
        self.vista.lbl_resumen_links.setText(f"Total Links: {total_l}")
        self.vista.lbl_resumen_fechas.setText(f"Total Fechas: {total_f}")

        self.vista.tabs.setTabText(0, f"Correos ({total_c})")
        self.vista.tabs.setTabText(1, f"Links ({total_l})")
        self.vista.tabs.setTabText(2, f"Fechas ({total_f})")

        QMessageBox.information(self.vista, "Proceso Terminado", "¡Se han generado los archivos TXT exitosamente!")

        self.vista.lista_resultados.clear()
        self.vista.lista_resultados.addItems(urls_a_procesar)

        try:
            with open("correos_encontrados.txt", "r", encoding="utf-8") as f: self.vista.txt_correos.setText(f.read())
            with open("links_encontrados.txt", "r", encoding="utf-8") as f: self.vista.txt_links.setText(f.read())
            with open("fechas_encontradas.txt", "r", encoding="utf-8") as f: self.vista.txt_fechas.setText(f.read())
        except Exception:
            pass 

        self.vista.stacked_widget.setCurrentIndex(3)