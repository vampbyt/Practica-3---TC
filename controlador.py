#LIBRERIAS
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QHBoxLayout, QCheckBox, QLineEdit, QWidget
from PyQt6.QtCore import Qt

class Controlador:
    
    #CONSTRUCTOR
    def __init__(self, vista, modelo):
        #Enlace de las capas de la arquitectura
        self.vista = vista
        self.modelo = modelo
        
        #Lista para almacenar tuplas dinámicas de la forma: (QCheckBox, QLineEdit)
        #Se usa para iterar posteriormente y saber qué URLs decidió procesar el usuario.
        self.elementos_archivo = []
        
        #Inicialización de eventos
        self.conectar_botones()

    #MAPEADO DE SEÑALES (Eventos de la UI)
    def conectar_botones(self):
        self.vista.btn_inicio.clicked.connect(self.ir_a_inicio)
        self.vista.btn_ir_manual.clicked.connect(self.ir_a_manual)
        self.vista.btn_ir_archivo.clicked.connect(self.cargar_y_mostrar_archivo)
        self.vista.btn_mas_manual.clicked.connect(self.desbloquear_campo)
        
        #Uso de funciones lambda (anónimas)
        #Permite enviar un parámetro ("manual" o "archivo") a la función procesar, 
        #algo que el método .connect() normalmente no permite de forma directa.
        self.vista.btn_procesar_manual.clicked.connect(lambda: self.procesar("manual"))
        self.vista.btn_procesar_archivo.clicked.connect(lambda: self.procesar("archivo"))

    #NAVEGACION DE VISTAS (Stacked Widget)
    def ir_a_inicio(self):
        #Índice 0: Pantalla principal
        self.vista.stacked_widget.setCurrentIndex(0)
        self.vista.btn_inicio.hide()

    def ir_a_manual(self):
        #Índice 1: Pantalla de ingreso por texto
        self.vista.stacked_widget.setCurrentIndex(1)
        self.vista.btn_inicio.show()

    #INSERCION DINAMICA DE ENTRADAS (Modo Manual)
    def desbloquear_campo(self):
        #1. Eficiencia y Reutilización: 
        #Busca si hay campos previamente deshabilitados y los reactiva en lugar de crear nuevos instantes.
        for le in self.vista.entradas_manuales:
            if not le.isEnabled():
                le.setEnabled(True)
                return
        
        #2. Creación: Si todos están en uso, instancia un nuevo QLineEdit.
        nuevo_le = QLineEdit()
        #Ejemplo visual: "URL 4..."
        nuevo_le.setPlaceholderText(f"URL {len(self.vista.entradas_manuales) + 1}...")
        self.vista.entradas_manuales.append(nuevo_le)
        self.vista.layout_entradas_manuales.addWidget(nuevo_le)

    #CARGA Y RENDERIZADO DE ARCHIVOS
    def cargar_y_mostrar_archivo(self):
        #Abre un explorador de archivos nativo, filtrando estrictamente a .txt
        ruta_archivo, _ = QFileDialog.getOpenFileName(None, "Seleccionar archivo TXT", "", "Text Files (*.txt)")
        
        if ruta_archivo:
            #Proteccion de errores (Lectura)
            try:
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    #Limpia espacios en blanco y saltos de línea (\n), e ignora las líneas que estén vacías
                    urls = [linea.strip() for linea in f.readlines() if linea.strip()]
                
                #LIMPIEZA DE LAYOUT (Evita duplicados visuales)
                #Se recorre en reversa (reversed). Si borramos de 0 a N, los índices cambian en tiempo de ejecución 
                #y provocaría un desbordamiento o dejaría elementos sin borrar.
                for i in reversed(range(self.vista.layout_lista_archivo.count())): 
                    widget = self.vista.layout_lista_archivo.itemAt(i).widget()
                    if widget: widget.deleteLater() #Liberación de memoria nativa de Qt
                
                #Limpia el registro lógico
                self.elementos_archivo.clear()

                #RENDERIZADO DINAMICO DE URLs
                for url in urls:
                    #Crea un contenedor horizontal para alinear el checkbox y el texto
                    fila_widget = QWidget()
                    fila_layout = QHBoxLayout(fila_widget)
                    fila_layout.setContentsMargins(0,0,0,0) #Sin márgenes para que se vea como una lista limpia
                    
                    #Componentes de la fila
                    chk = QCheckBox()
                    chk.setChecked(True) #Se asume que por defecto sí quiere procesar la URL encontrada
                    le = QLineEdit(url)
                    
                    #Ensamblaje
                    fila_layout.addWidget(chk)
                    fila_layout.addWidget(le)
                    self.vista.layout_lista_archivo.addWidget(fila_widget)
                    
                    #Se guarda la referencia de los controles para el bucle de procesamiento posterior
                    self.elementos_archivo.append((chk, le))

                #Índice 2: Pantalla de confirmación de lista de archivo
                self.vista.stacked_widget.setCurrentIndex(2)
                self.vista.btn_inicio.show()
                
            except Exception as e:
                #Caso de que tenga un error: El archivo está bloqueado, corrupto, o codificado distinto
                QMessageBox.critical(self.vista, "Error", f"No se pudo leer el archivo: {e}")

    #LOGICA PRINCIPAL DE PROCESAMIENTO
    def procesar(self, origen):
        urls_a_procesar = []
        
        #RECOLECCION DE DATOS (DEPENDIENDO DE LA VISTA)
        if origen == "manual":
            for le in self.vista.entradas_manuales:
                #Condición: La caja debe estar habilitada Y no estar vacía
                if le.isEnabled() and le.text().strip():
                    urls_a_procesar.append(le.text().strip())
                    
        elif origen == "archivo":
            for chk, le in self.elementos_archivo:
                #Condición: El checkbox debe estar activado Y la caja no estar vacía
                if chk.isChecked() and le.text().strip():
                    urls_a_procesar.append(le.text().strip())

        #EN CASO DE QUE UN SUPER ERROR (o usuario despistado): Lista vacía
        if not urls_a_procesar:
            QMessageBox.warning(self.vista, "Atención", "No hay URLs válidas para procesar.")
            return

        #COMUNICACION CON EL MODELO
        resultados_finales = {}
        for url in urls_a_procesar:
            #Llama al motor de RegEx del archivo anterior
            resultados_finales[url] = self.modelo.analizar_url(url)
            
        #El modelo se encarga de escribir los 3 archivos físicos (.txt)
        self.modelo.guardar_resultados(resultados_finales)

        #CALCULO DE METRICAS (Σ de elementos encontrados)
        #Itera sobre los valores del diccionario resultante y suma el tamaño de las listas
        total_c = sum(len(d["correos"]) for d in resultados_finales.values())
        total_l = sum(len(d["links"]) for d in resultados_finales.values())
        total_f = sum(len(d["fechas"]) for d in resultados_finales.values())

        #ACTUALIZACION DE LA INTERFAZ DE RESULTADOS
        #1. Etiquetas de Resumen
        self.vista.lbl_resumen_correos.setText(f"Total Correos: {total_c}")
        self.vista.lbl_resumen_links.setText(f"Total Links: {total_l}")
        self.vista.lbl_resumen_fechas.setText(f"Total Fechas: {total_f}")

        #Aviso visual al usuario
        QMessageBox.information(self.vista, "Proceso Terminado", "¡Se han generado los archivos TXT exitosamente!")

        #3. Poblar la lista informativa lateral/superior con las URLs validadas
        self.vista.lista_resultados.clear()
        self.vista.lista_resultados.addItems(urls_a_procesar)

        #4. Volcado de disco a UI
        #Protección de errores: Intenta leer los archivos recién creados para mostrarlos en la UI.
        try:
            with open("correos_encontrados.txt", "r", encoding="utf-8") as f: self.vista.txt_correos.setText(f.read())
            with open("links_encontrados.txt", "r", encoding="utf-8") as f: self.vista.txt_links.setText(f.read())
            with open("fechas_encontradas.txt", "r", encoding="utf-8") as f: self.vista.txt_fechas.setText(f.read())
        except Exception:
            #Si algo falla (ej. permisos de lectura repentinos), se ignora pasivamente (pass), 
            #ya que el procesamiento fuerte ya terminó.
            pass 

        #Índice 3: Muestra la pantalla final de métricas y lectura
        self.vista.stacked_widget.setCurrentIndex(3)