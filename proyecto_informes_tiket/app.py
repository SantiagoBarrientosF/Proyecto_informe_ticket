from flask import Flask, render_template, request, redirect, url_for, send_file, session
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'clave_secreta'

UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "Downloads")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
archivo_guardado = None 

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
# Funcion encargada de procesar el archivo de SIMM- Reporte WO
def procesar_simm(df):
      # Validar que el archivo tenga al menos 5 filas
    if len(df) > 4:
        df_cleaned = df.iloc[4:].reset_index(drop=True)  
    else:
        return None, "Archivo insuficiente."
    # Numero de columnas esperadas
    expected_columns = 13
    # Ajusta el numero de columnas cuando estas son mayores a 13
    if df_cleaned.shape[1] > expected_columns:
        df_cleaned = df_cleaned.iloc[:, :expected_columns]
    # Ajusta el numero de columnas cuando son menores a 13 
    elif df_cleaned.shape[1] < expected_columns:
        missing_cols = expected_columns - df_cleaned.shape[1]
        for i in range(missing_cols):
            df_cleaned[f'Columna_extra_{i+1}'] = None
    # Columnas del archivo SIMM
    df_cleaned.columns = [
        'Correo Electronico', 'N° Orden de trabajo', 'REQ', 'Estado', 'Fecha de creación',
        'Fecha Programada Inicio', 'Fecha Ult Modificación', 'Fecha de Cierre',
        'Categorización N1', 'Categorización N2', 'Categorización N3', 'Detalle descripción', 'Resolución'
    ]
    #Eliminacion y renombre de columnas
    df_cleaned = df_cleaned.drop(['Fecha Programada Inicio', 'Fecha de Cierre'], axis=1)
    df_cleaned.rename(columns={'Resolución': 'Observación'}, inplace=True)

    # Agregar nuevas columnas
    df_cleaned['Entrega Plan de Trabajo'] = ''
    df_cleaned['Pruebas con SIMM'] = ''
    df_cleaned['Posible Salida a Producción'] = ''
    df_cleaned['Firma SIMM'] = ''
    # Reordenar columnas
    df_cleaned['Solicitante'] = ''
    cols = ['Solicitante'] + [col for col in df_cleaned.columns if col != 'Solicitante']
    df_cleaned = df_cleaned[cols]
    # Convertir formato a datetime
    df_cleaned['Fecha Ult Modificación'] = pd.to_datetime(df_cleaned['Fecha Ult Modificación'], errors='coerce')
    df_cleaned['Semaforo'] = df_cleaned['Fecha Ult Modificación'].apply(semaforo_colores)

    return df_cleaned, None
# Funcion encargada de procesar el archivo de seguimiento final
def procesar_seguimiento_final(df):
    # Columna con los datos correspondientes al archivo de seguimiento_final
    columnas = [
        'Solicitante', 'WO', 'REQ', 'Fecha Creación', 'Fecha Ultima Nota',
        'Descripción', 'Detalle Ultima Nota', 'Aplicación', 'Tipo', 'Observadores UT'
    ]

    df_cleaned = df.iloc[4:].reset_index(drop=True)
    df_cleaned.columns = columnas

    df_cleaned['Fecha Ultima Nota'] = pd.to_datetime(df_cleaned['Fecha Ultima Nota'], errors='coerce')
    df_cleaned['Semaforo'] = df_cleaned['Fecha Ultima Nota'].apply(semaforo_colores)

    return df_cleaned
# Funcion encargada procesar los colores de los semaforos en base a su fecha
def semaforo_colores(fecha):
    # Verificar que la fecha no sea nula
    try:
        hoy = datetime.now()
        if pd.isnull(fecha) or fecha is pd.NaT:
            return "sin fecha"
        if isinstance(fecha, pd.Timestamp):
            diferencia = (hoy - fecha).days
        else:
            return "sin fecha"
        # Definir colores
        if diferencia <= 30:
            return "verde"
        elif 30 < diferencia <= 60:
            return "naranja"
        else:
            return "rojo"
    except Exception:
        return "sin fecha"
# Ruta para la carga de archivos
@app.route('/', methods=['GET', 'POST'])
# Funcion encargada de la carga y manejo de los archivos subidos
def upload_file():
    global archivo_guardado
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            df = pd.read_excel(filepath)

            # Verificacion que se encarga de validar si el archivo fue subido
            if "SIMM" in file.filename:
                df_cleaned, error = procesar_simm(df)
                template = "resultado.html"
                error = None
            elif "Seguimiento_final" in file.filename:
                df_cleaned = procesar_seguimiento_final(df)
                template = "resultado_seguimiento.html"
                error = None
            else:
                return render_template('index.html', error="Archivo desconocido.")

            if error:
                return render_template('index.html', error=error)
            # Guardado de datos para mostrar en la plantilla
            data = df_cleaned.to_dict(orient='records')
            session['datos'] = data
            # Guardado de archivo para la descarga
            archivo_guardado = os.path.join(app.config['UPLOAD_FOLDER'], 'resultado_procesado.xlsx')
            df_cleaned.to_excel(archivo_guardado, index=False)

            return render_template(template, datos=data)

    return render_template('index.html')
# Ruta que premite la descarga del archivo
@app.route('/descargar', methods=['GET'])
# Funcion encargada de la descarga del archivo
def descargar():
    global archivo_guardado
    # Verifica que el archivo exista para su posterior descarga
    if archivo_guardado and os.path.exists(archivo_guardado):
        return send_file(archivo_guardado, as_attachment=True, download_name='resultado_procesado.xlsx')
    return "No hay archivo disponible para descargar."
# Ruta de ingresa al index
@app.route('/regresar', methods=['GET'])
def regresar():
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(debug=True)
