#Librerias:
import urllib.request           #Para realizar peticiones HTTP y descargar el código fuente
import re                       #Motor de Expresiones Regulares (Regex) para la búsqueda de patrones
from datetime import datetime   #Para la conversión y estandarización de objetos de tiempo


#CLASE PRINCIPAL
class ExtractorModelo:
    def __init__(self):
        #DEFINICION DE PATRONES (EXPRESIONES REGULARES)
        #Esta es la teoría lógica que usará el motor para encontrar coincidencias.
        
        # 1. Correos: P(usuario) + @ + P(dominio) + . + P(extension)
        # Busca caracteres permitidos, seguidos de arroba, un dominio, un punto y una extensión de mínimo 2 letras.
        self.patron_correo = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # 2. Enlaces: href="URL" o href='URL'
        # Busca el atributo href, capta la comilla (simple o doble), busca http o https y captura todo hasta la comilla de cierre.
        self.patron_link = r'href=["\'](http[s]?://[^"\']+)["\']'
        
        # 3. Fechas: DD/MM/AAAA, DD-MM-AA, AAAA-MM-DD, etc.
        # \b define los límites de la palabra para no cortar números largos. 
        # \d cuantifica los dígitos separados por / o -.
        self.patron_fechas = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b'

    #DESCARGA DE HTML
    def descargar_html(self, url):
        #Proteccion de errores en la conexion
        #Si la página no existe, bloquea el acceso o tarda mucho, el programa no se detendrá bruscamente.
        try:
            #Fingimos ser un navegador (User-Agent) para evitar bloqueos de seguridad básicos (Error 403)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            #Lanzamos la petición con un límite de tiempo
            respuesta = urllib.request.urlopen(req, timeout=10)
            #Decodificamos el binario a texto (UTF-8), ignorando caracteres corruptos para no crashear
            return respuesta.read().decode('utf-8', errors='ignore')
        except Exception as e:
            #Caso de que tenga un error en la red o página no encontrada
            return None

    #ESTANDARIZACION DE FORMATOS
    def estandarizar_fecha(self, fecha_str):
        #Diccionario de formatos posibles que la regex pudo haber capturado
        formatos = ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%Y-%m-%d", "%Y/%m/%d"]
        
        #Limpieza básica de espacios fantasma al inicio o final
        fecha_limpia = fecha_str.strip()
        
        #BUCLE DE CONVERSION
        #Prueba cada formato hasta encontrar el que coincida con la cadena extraída
        for fmt in formatos:
            try:
                #Ejemplo: "2026/04/14" choca con "%d/%m/%Y" -> Falla y sigue intentando
                #Cuando coincide con "%Y/%m/%d", la convierte y la formatea unificadamente a "DD-MM-YYYY"
                return datetime.strptime(fecha_limpia, fmt).strftime("%d-%m-%Y")
            except ValueError:
                #Si el formato no coincide, simplemente pasa al siguiente intento
                continue
        
        #EN CASO DE QUE UN SUPER ERROR de formato no contemplado ocurra, devuelve la fecha original sin modificar
        return fecha_limpia

    #ANALISIS Y EXTRACCION DE DATOS
    def analizar_url(self, url):
        #Obtenemos el código fuente de la página
        html = self.descargar_html(url)
        
        #Si la descarga falló (retornó None), devolvemos listas vacías para no romper el programa
        if not html:
            return {"correos": [], "links": [], "fechas": []}

        #EXTRACCION POR EXPRESIONES REGULARES
        #re.findall() busca TODAS las coincidencias en el HTML.
        #Usamos set() para eliminar duplicados de forma ultra eficiente (O(1) en inserciones),
        #y luego list() para volver a tener un formato manejable y ordenable.
        correos = list(set(re.findall(self.patron_correo, html)))
        links = list(set(re.findall(self.patron_link, html)))
        
        #Para las fechas, aplicamos comprensión de listas llamando a nuestra función de estandarización
        fechas = list(set([self.estandarizar_fecha(f) for f in re.findall(self.patron_fechas, html)]))

        #Retornamos un diccionario empaquetado con los resultados
        return {"correos": correos, "links": links, "fechas": fechas}

    #GUARDADO DE RESULTADOS
    def guardar_resultados(self, resultados):
        #Matriz/Diccionario de configuración para los archivos de salida
        #Estructura: "nombre_archivo": ("clave_del_diccionario", "Texto de la cabecera")
        archivos = {
            "correos_encontrados.txt": ("correos", "Numero de correos"),
            "links_encontrados.txt": ("links", "Numero de links"),
            "fechas_encontradas.txt": ("fechas", "Numero de fechas")
        }

        #BUCLE PRINCIPAL DE ESCRITURA
        for nombre_archivo, (clave, texto_cabecera) in archivos.items():
            #Abrimos/creamos el archivo en modo escritura ("w") con soporte para caracteres especiales ("utf-8")
            with open(nombre_archivo, "w", encoding="utf-8") as f:
                
                #Cálculo del total: suma la cantidad de elementos de todas las URLs analizadas para esta categoría específica
                total_elementos = sum(len(datos[clave]) for datos in resultados.values())
                
                #Encabezado del archivo
                f.write(f"{texto_cabecera} = {total_elementos}\n")
                f.write("-" * 40 + "\n\n")

                #Despliegue de datos agrupados por URL origen
                for url, datos in resultados.items():
                    elementos = datos[clave] #Extrae solo la lista correspondiente (ej. solo correos)
                    
                    #Validación: Solo escribe en el archivo si realmente se encontró algo en esa URL
                    if elementos:
                        f.write(f"{url}:\n")
                        f.write(f"{clave.capitalize()} encontrados:\n")
                        
                        #Vaciado de elementos
                        for elemento in elementos:
                            f.write(f"{elemento}\n")
                        #Separador visual entre distintas URLs dentro del mismo archivo
                        f.write("---\n\n")