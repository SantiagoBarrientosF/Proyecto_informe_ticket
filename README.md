#  Procesador de Archivos Excel con Flask
Este proyecto es una aplicación web desarrollada con Flask que permite cargar archivos Excel, procesar su contenido y descargar un archivo con los datos modificados. 

# Requisitos
- Python 3.X
- Flask
- Pandas
- openpyxl
  
##  Instalación y ejecución
1- Clona este repositorio:https://github.com/SantiagoBarrientosF/Proyecto_informe_ticket.

2- Instala las dependencias "pip install -r requirements.txt".

3- Ejecuta la aplicación "python app.py".

# Uso de la aplicación
- Sube un archivo Excel desde la página principal.  
- Se procesará y mostrará la información en pantalla.  
- Descarga el archivo modificado con los datos ajustados.
- 
# Estructura del proyecto
proyecto_informes_tiket/ 
│── static/ # Archivos estáticos.

│ ├── style.css # Archivo CSS para el diseño. 

│── templates/ # Plantillas HTML para la interfaz.
    |
    ├── index.html # Página principal de carga del archivo.
    |
    ├── resultado.html # Página de resultados después del procesamiento.
    
│── uploads/ # Carpeta donde se guardan los archivos subidos. 
    |
    ├── (Archivo Excel) # Aquí se almacenan los archivos.
    |
│── .gitignore # Lista de archivos/carpetas que Git debe ignorar.
|
│── app.py # Archivo principal con la lógica de Flask.
|
│── requirements.txt # Lista de dependencias necesarias para la aplicación.
