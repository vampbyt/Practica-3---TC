import urllib.request
import re
from datetime import datetime

class ExtractorModelo:
    def __init__(self):
        self.patron_correo = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.patron_link = r'href=["\'](http[s]?://[^"\']+)["\']'
        self.patron_fechas = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b'

    def descargar_html(self, url):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            respuesta = urllib.request.urlopen(req, timeout=10)
            return respuesta.read().decode('utf-8', errors='ignore')
        except Exception as e:
            return None

    def estandarizar_fecha(self, fecha_str):
        formatos = ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d", "%Y/%m/%d"]
        fecha_limpia = fecha_str.strip()
        for fmt in formatos:
            try:
                return datetime.strptime(fecha_limpia, fmt).strftime("%d-%m-%Y")
            except ValueError:
                continue
        return fecha_limpia

    def analizar_url(self, url):
        html = self.descargar_html(url)
        if not html:
            return {"correos": [], "links": [], "fechas": []}

        correos = list(set(re.findall(self.patron_correo, html)))
        links = list(set(re.findall(self.patron_link, html)))
        fechas = list(set([self.estandarizar_fecha(f) for f in re.findall(self.patron_fechas, html)]))

        return {"correos": correos, "links": links, "fechas": fechas}

    def guardar_resultados(self, resultados):
        archivos = {
            "correos_encontrados.txt": ("correos", "Numero de correos"),
            "links_encontrados.txt": ("links", "Numero de links"),
            "fechas_encontradas.txt": ("fechas", "Numero de fechas")
        }

        for nombre_archivo, (clave, texto_cabecera) in archivos.items():
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                total_elementos = sum(len(datos[clave]) for datos in resultados.values())
                
                f.write(f"{texto_cabecera} = {total_elementos}\n")
                f.write("-" * 40 + "\n\n")

                for url, datos in resultados.items():
                    elementos = datos[clave]
                    if elementos:
                        f.write(f"{url}:\n")
                        f.write(f"{clave.capitalize()} encontrados:\n")
                        for elemento in elementos:
                            f.write(f"{elemento}\n")
                        f.write("---\n\n")