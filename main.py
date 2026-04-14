import sys
from PyQt6.QtWidgets import QApplication
from modelo import ExtractorModelo
from vista import VentanaPrincipal
from controlador import Controlador

def main():
    app = QApplication(sys.argv)
    modelo = ExtractorModelo()
    vista = VentanaPrincipal()
    controlador = Controlador(vista, modelo)
    
    vista.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()