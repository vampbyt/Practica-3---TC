import urllib.request
import re #Bblioteca para expresiones regulares.

def descargar_html(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        respuesta = urllib.request.urlopen(req)
        html = respuesta.read().decode('utf-8')
        return html
    except Exception as e:
        print(f"Error al descargar el HTML: {e}")
        return None
    

urls = []
print("--- Extractor de datos ---")
for i in range(3):
    url = input(f"Ingrese la URL {i+1}: ")
    urls.append(url)


todos_correos = []
todos_links = []
todas_fechas = []

for url in urls:
    print(f"\nProcesando URL: {url}"    )
    html = descargar_html(url)
    if html:
        patron_correo = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        correos_encontrados = re.findall(patron_correo, html)
        
        patron_link = r'href=["\'](http[s]?://[^"\']+)["\']'
        links_encontrados = re.findall(patron_link, html)

        patron_fechas = patron_fecha = r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b'
        fechas_encontradas = re.findall(patron_fechas, html)

        # Mostramos los resultados por página como pide la práctica
        print(f"  -> Correos encontrados: {len(correos_encontrados)}")
        print(f"  -> Links encontrados: {len(links_encontrados)}")
        print(f"  -> Fechas encontradas: {len(fechas_encontradas)}")

        
        # Guardamos en la lista global
        todos_correos.extend(correos_encontrados)
        todos_links.extend(links_encontrados)
        todas_fechas.extend(fechas_encontradas)

# 4. Generar archivos de salida (Ejemplo con el archivo de correos)
# Usamos set() para eliminar correos duplicados si aparecieron varias veces
with open("correos_encontrados.txt", "w", encoding="utf-8") as archivo_correos:
    for correo in set(todos_correos):
        archivo_correos.write(correo + "\n")

with open("links_encontrados.txt", "w", encoding="utf-8") as archivo_links:
    for link in set(todos_links):
        archivo_links.write(link + "\n")

with open("fechas_encontradas.txt", "w", encoding="utf-8") as archivo_fechas:
    for fecha in set(todas_fechas):
        archivo_fechas.write(fecha + "\n")


print("\n¡Análisis terminado! Archivos generados correctamente.")
