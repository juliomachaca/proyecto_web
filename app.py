from flask import Flask, render_template, request, jsonify
import numpy as np
import math
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)

# Función para renderizar un gráfico y devolverlo como base64
def crear_grafico(fig):
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    return plot_url

# Página principal con el menú
@app.route('/')
def index():
    return render_template('index.html')

# Clasificación de Carreteras (Demanda)
@app.route('/clasificacion_carreteras/demanda', methods=['GET', 'POST'])
def clasificacion_demanda():
    if request.method == 'POST':
        imda = int(request.form['imda'])
        clasificacion = ''
        caracteristicas = ''
        if imda > 6000:
            clasificacion = "Autopistas de Primera Clase"
            caracteristicas = ("Calzadas divididas por un separador central de mínimo 6 m, "
                               "dos o más carriles de 3.60 m de ancho, control total de accesos, "
                               "sin cruces o pasos a nivel, pavimentadas.")
        elif 4001 <= imda <= 6000:
            clasificacion = "Autopistas de Segunda Clase"
            caracteristicas = ("Calzadas divididas por un separador central de 6 m a 1 m, "
                               "dos o más carriles de 3.60 m de ancho, control parcial de accesos, "
                               "cruces o pasos a nivel, pavimentadas.")
        elif 2001 <= imda <= 4000:
            clasificacion = "Carreteras de Primera Clase"
            caracteristicas = ("Una calzada de dos carriles de 3.60 m de ancho, "
                               "cruces o pasos vehiculares a nivel, pavimentadas.")
        elif 401 <= imda <= 2000:
            clasificacion = "Carreteras de Segunda Clase"
            caracteristicas = ("Una calzada de dos carriles de 3.30 m de ancho, "
                               "cruces o pasos vehiculares a nivel, pavimentadas.")
        elif 200 <= imda <= 400:
            clasificacion = "Carreteras de Tercera Clase"
            caracteristicas = ("Una calzada de dos carriles de 3.00 m de ancho, "
                               "pueden tener carriles de 2.50 m, afirmadas o pavimentadas.")
        else:
            clasificacion = "Trochas Carrozables"
            caracteristicas = ("Ancho mínimo de 4.00 m, con ensanches cada 500 m, "
                               "superficie afirmada o sin afirmar.")

        return render_template('clasificacion_result.html', clasificacion=clasificacion, caracteristicas=caracteristicas)

    return render_template('clasificacion_demanda.html')

# Diseño Geométrico de Carreteras
@app.route('/diseno_geometrico', methods=['GET', 'POST'])
def diseno_geometrico():
    if request.method == 'POST':
        try:
            velocidad_diseño = float(request.form['velocidad_diseño'])
            radio_curva = float(request.form['radio_curva'])
            coef_friccion = float(request.form['coef_friccion'])
            pendiente_longitudinal = float(request.form['pendiente_longitudinal'])
            peralte_max = 8
            tiempo_percepcion = 2.5

            # Cálculo del peralte y otras variables
            peralte = (velocidad_diseño / 3.6)**2 / (9.81 * radio_curva) - coef_friccion
            peralte = max(0, peralte * 100)
            radio_minimo = (velocidad_diseño / 3.6)**2 / (9.81 * (peralte_max / 100 + coef_friccion))
            distancia_frenado = (velocidad_diseño / 3.6)**2 / (254 * (coef_friccion + pendiente_longitudinal / 100))
            longitud_transicion = (velocidad_diseño / 3.6)**3 / (radio_curva * peralte_max / 100)
            visibilidad = 0.278 * velocidad_diseño * tiempo_percepcion + (velocidad_diseño**2) / (254 * coef_friccion)

            # Generar gráfico
            radios = np.linspace(50, 500, 100)
            peraltes = [(velocidad_diseño / 3.6)**2 / (9.81 * r) - coef_friccion for r in radios]
            peraltes = [max(0, p * 100) for p in peraltes]

            fig, ax = plt.subplots()
            ax.plot(radios, peraltes, label='Peralte vs Radio de Curva')
            ax.axvline(radio_minimo, color='r', linestyle='--', label=f'Radio mínimo: {radio_minimo:.2f} m')
            ax.set_xlabel('Radio de Curva (m)')
            ax.set_ylabel('Peralte (%)')
            ax.set_title('Relación entre el peralte y el radio de la curva')
            ax.legend()
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('diseno_result.html', peralte=peralte, radio_minimo=radio_minimo,
                                   distancia_frenado=distancia_frenado, longitud_transicion=longitud_transicion,
                                   visibilidad=visibilidad, plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('diseno_geometrico.html')

# Capacidad y Nivel de Servicio
@app.route('/capacidad_nivel_servicio', methods=['GET', 'POST'])
def capacidad_nivel_servicio():
    if request.method == 'POST':
        try:
            volumen_trafico = float(request.form['volumen_trafico'])
            ancho_carril = float(request.form['ancho_carril'])
            tipo_vehiculo = request.form['tipo_vehiculo'].lower()

            capacidad = 2400 if tipo_vehiculo == "liviano" else 1920
            capacidad += 100 if ancho_carril > 3.7 else -200 if ancho_carril < 3.5 else 0

            flujo = volumen_trafico / capacidad
            nivel_servicio = "A" if flujo <= 0.6 else "B" if flujo <= 0.7 else "C" if flujo <= 0.8 else \
                             "D" if flujo <= 0.9 else "E" if flujo <= 1.0 else "F"

            # Generar gráfico
            fig, ax = plt.subplots()
            ax.bar(["A", "B", "C", "D", "E", "F"], [0.6, 0.7, 0.8, 0.9, 1.0, 1.2], color=['green', 'lightgreen', 'yellow', 'orange', 'red', 'darkred'])
            ax.set_xlabel('Nivel de Servicio')
            ax.set_ylabel('Flujo (vehículos/hora)')
            ax.set_title('Capacidad y Nivel de Servicio')
            ax.axhline(flujo, color='blue', linestyle='--', label=f'Flujo actual: {flujo:.2f}')
            ax.legend()
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('capacidad_result.html', nivel_servicio=nivel_servicio, capacidad=capacidad, plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('capacidad_nivel_servicio.html')

# Pavimentos y Diseño de Estructuras de Pavimento
@app.route('/pavimentos_diseno_estructuras', methods=['GET', 'POST'])
def pavimentos_diseno_estructuras():
    if request.method == 'POST':
        try:
            trafico_medio_diario = float(request.form['trafico_medio_diario'])
            CBR_suelo = float(request.form['CBR_suelo'])
            cargas_eje = float(request.form['cargas_eje'])
            vida_util = float(request.form['vida_util'])

            espesor_subbase = max(15, 0.25 * trafico_medio_diario / CBR_suelo + 0.1 * cargas_eje)
            espesor_base = max(20, 0.2 * trafico_medio_diario / CBR_suelo + 0.15 * cargas_eje)
            espesor_rodadura = max(5, 0.05 * trafico_medio_diario / vida_util)
            espesor_total = espesor_subbase + espesor_base + espesor_rodadura

            # Generar gráfico
            fig, ax = plt.subplots()
            capas = ['Subbase', 'Base', 'Capa Rodadura']
            espesores = [espesor_subbase, espesor_base, espesor_rodadura]
            ax.bar(capas, espesores, color=['#ffcc80', '#90a4ae', '#37474f'])
            ax.set_xlabel('Capas del Pavimento')
            ax.set_ylabel('Espesor (cm)')
            ax.set_title('Diseño de Espesor de Capas de Pavimento')
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('pavimentos_result.html', espesor_subbase=espesor_subbase,
                                   espesor_base=espesor_base, espesor_rodadura=espesor_rodadura,
                                   espesor_total=espesor_total, plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('pavimentos_diseno_estructuras.html')

# Diseño de Drenaje
@app.route('/diseno_drenaje', methods=['GET', 'POST'])
def diseno_drenaje():
    if request.method == 'POST':
        try:
            intensidad_lluvia = float(request.form['intensidad_lluvia'])
            pendiente_transversal = float(request.form['pendiente_transversal'])
            longitud_via = float(request.form['longitud_via'])
            ancho_via = float(request.form['ancho_via'])
            coef_escorrentia = float(request.form['coef_escorrentia'])
            capacidad_almacenamiento = float(request.form['capacidad_almacenamiento'])

            area = longitud_via * ancho_via
            caudal_diseño = (intensidad_lluvia / 3600) * area * coef_escorrentia
            diametro_necesario = ((caudal_diseño / (0.013 * math.sqrt(pendiente_transversal / 100))) ** (3/8)) / 1000
            capacidad_sistema = (math.pi * (diametro_necesario/2)**2) * math.sqrt(pendiente_transversal / 100) * 1000
            riesgo_inundacion = "Posible inundación" if caudal_diseño > capacidad_sistema else "Sistema adecuado"

            # Generar gráfico
            fig, ax = plt.subplots()
            ax.bar(["Tubería necesaria"], [diametro_necesario], color='#42a5f5')
            ax.set_xlabel('Componentes de Drenaje')
            ax.set_ylabel('Diámetro (m)')
            ax.set_title('Diámetro de Tubería Necesario')
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('drenaje_result.html', caudal_diseño=caudal_diseño, 
                                   diametro_necesario=diametro_necesario,
                                   capacidad_sistema=capacidad_sistema, riesgo_inundacion=riesgo_inundacion,
                                   plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('diseno_drenaje.html')

# Análisis de Estabilidad de Taludes en Carreteras
@app.route('/analisis_estabilidad_taludes', methods=['GET', 'POST'])
def analisis_estabilidad_taludes():
    if request.method == 'POST':
        try:
            angulo_talud = float(request.form['angulo_talud'])
            tipo_suelo = request.form['tipo_suelo'].lower()
            cohesion = float(request.form['cohesion'])
            angulo_friccion = float(request.form['angulo_friccion'])
            carga_externa = float(request.form['carga_externa'])
            condiciones_extremas = request.form['condiciones_extremas'].lower() == 'si'

            peso_suelo = {'arcilla': 18, 'arena': 20, 'roca': 25}.get(tipo_suelo, 20)
            angulo_rad = math.radians(angulo_talud)
            num = cohesion + (peso_suelo * math.tan(math.radians(angulo_friccion)))
            den = peso_suelo * math.sin(angulo_rad) + carga_externa
            factor_seguridad = num / den

            prediccion = "Posible deslizamiento en condiciones críticas" if condiciones_extremas and factor_seguridad < 1.2 else "Estabilidad suficiente"

            # Generar gráfico
            fig, ax = plt.subplots()
            ax.bar(["Talud"], [factor_seguridad], color='green' if factor_seguridad >= 1.5 else 'red')
            ax.set_xlabel('Ángulo del talud')
            ax.set_ylabel('Factor de seguridad')
            ax.set_title('Estabilidad del Talud')
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('taludes_result.html', factor_seguridad=factor_seguridad,
                                   prediccion=prediccion, plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('analisis_estabilidad_taludes.html')

# Cálculo de Volúmenes de Movimiento de Tierra
@app.route('/calculo_volumen_tierra', methods=['GET', 'POST'])
def calculo_volumen_tierra():
    if request.method == 'POST':
        try:
            area_corte = float(request.form['area_corte'])
            area_relleno = float(request.form['area_relleno'])
            longitud_tramo = float(request.form['longitud_tramo'])
            altura_corte = float(request.form['altura_corte'])
            altura_rellenar = float(request.form['altura_rellenar'])
            costo_por_m3 = float(request.form['costo_por_m3'])

            volumen_corte = altura_corte * area_corte * longitud_tramo
            volumen_relleno = altura_rellenar * area_relleno * longitud_tramo
            costo_total = (volumen_corte + volumen_relleno) * costo_por_m3

            # Generar gráfico
            fig, ax = plt.subplots()
            categorias = ['Corte', 'Relleno']
            volúmenes = [volumen_corte, volumen_relleno]
            ax.bar(categorias, volúmenes, color=['#e53935', '#43a047'])
            ax.set_ylabel('Volumen (m³)')
            ax.set_title('Volúmenes de Movimiento de Tierra')
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('volumen_tierra_result.html', volumen_corte=volumen_corte,
                                   volumen_relleno=volumen_relleno, costo_total=costo_total,
                                   plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('calculo_volumen_tierra.html')

# Cálculo de Distancias de Frenado y Visibilidad
@app.route('/calculo_distancias', methods=['GET', 'POST'])
def calculo_distancias():
    if request.method == 'POST':
        try:
            velocidad = float(request.form['velocidad']) * (1000 / 3600)  # Convertir km/h a m/s
            coef_friccion = float(request.form['coef_friccion'])
            pendiente = float(request.form['pendiente'])
            tiempo_reaccion = 2.0  # Tiempo de reacción promedio en segundos

            # Cálculo de la distancia de frenado
            distancia_frenado = (velocidad ** 2) / (2 * (9.81 * (coef_friccion + math.tan(math.radians(pendiente)))))
            # Cálculo de la distancia de visibilidad
            distancia_visibilidad = velocidad * tiempo_reaccion

            # Generar gráfico
            fig, ax = plt.subplots()
            categorias = ['Distancia de Frenado', 'Distancia de Visibilidad']
            distancias = [distancia_frenado, distancia_visibilidad]
            ax.bar(categorias, distancias, color=['#ff8a65', '#42a5f5'])
            ax.set_ylabel('Distancia (m)')
            ax.set_title('Distancias de Frenado y Visibilidad')
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('distancias_result.html', distancia_frenado=distancia_frenado,
                                   distancia_visibilidad=distancia_visibilidad, plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('calculo_distancias.html')

# Señalización y Seguridad Vial
@app.route('/calculo_senalizacion', methods=['GET', 'POST'])
def calculo_senalizacion():
    if request.method == 'POST':
        try:
            velocidad = float(request.form['velocidad'])
            tramos_criticos = request.form['tramos_criticos'].lower() == "si"
            volumen_trafico = float(request.form['volumen_trafico'])

            recomendaciones = []
            if velocidad > 80:
                recomendaciones.append("Colocar límites de velocidad a 80 km/h en tramos críticos.")
            else:
                recomendaciones.append("Mantener el límite de velocidad actual.")

            if tramos_criticos:
                recomendaciones.append("Instalar señalización de advertencia en curvas cerradas y cruces.")

            if volumen_trafico > 2000:
                recomendaciones.append("Colocar reductores de velocidad en zonas de alta congestión.")
            else:
                recomendaciones.append("No se requiere instalación de reductores de velocidad.")

            # Generar gráfico
            fig, ax = plt.subplots()
            categorias = ['Velocidad', 'Tramos Críticos', 'Volumen de Tráfico']
            valores = [velocidad, 1 if tramos_criticos else 0, volumen_trafico]
            ax.bar(categorias, valores, color=['#1e88e5', '#fb8c00', '#43a047'])
            ax.set_ylabel('Valores')
            ax.set_title('Datos de Señalización y Seguridad Vial')
            ax.grid(True)

            plot_url = crear_grafico(fig)

            return render_template('senalizacion_result.html', recomendaciones=recomendaciones, plot_url=plot_url)
        except ValueError:
            return "Por favor, ingresa valores numéricos válidos."

    return render_template('calculo_senalizacion.html')

if __name__ == '__main__':
    app.run(debug=True)
