from flask import Flask, render_template, request  #Esta libreria sirve para crear un servidor que permite que nosostros podamos ver nuetra calculadora en un navegador.
import matplotlib.pyplot as plt   #Esta libreria se encarga de que podamos generar una grafica a partir de los datos calculados.
import numpy as np  #Se usa para el manejo de arreglos numericos y funciones como seno, coseno y raíz.
import pandas as pd  #Es una estructura de datos. La usamos para organizar los resultados en tablas y realizar análisis estadisticos rapidos.
import io  #Basicamente maneja la memoria, lo que nos permite guardar la gráfica temporalmente en la RAM sin tener que crear un archivo de imagen en el disco duro.
import base64  #Esta seria el tarductor de imagenes. Lo  que hace es convertir la grafica de formato binario a una cadena de texto que el navegador puede entender y mostrar como imagen.
import re  #Es un filtro inteligente. Lo que hace es buscar patrones de texto para corregir automaticamente el usuario.

app = Flask(__name__)

# Codigo para el historial
historial_consultas = []

class CalculadoraTICs:
    def __init__(self, entrada):
        self.entrada = entrada
        # Aqui generamos 500 puntos para una curva suave, pero usaremos menos puntos para la tabla
        self.x = np.linspace(-10, 10, 500)

    def limpiar_entrada(self):  #Aqui lo que hacemos es corregir lo que el usuario escribe para que la computadora no se confunda.
        txt = self.entrada.lower().replace(' ', '').replace('^', '**')
        txt = re.sub(r'(\d)(x)', r'\1*\2', txt)
        return txt

    def obtener_datos(self):  #Esta parte seria el motor de la calculadora. Aqui lo que hacemos es transformar el texto ingresado por el usuario en coordenadas numericas para la grafica y la tabla de valores.
        txt_python = self.limpiar_entrada()  #Convertimos la entrada a una sintaxixs que python pueda entender(un ejemplo es: ^ se cambia por **)
        contexto = {"x": self.x, "np": np, "sin": np.sin, "cos": np.cos, "sqrt": np.sqrt}  #Mapeamos(que esto es como crear un puente o una llave para que la computadora sepa que cuando el usuario escribe una palabra, debe ejecutar una acción específica.) palabras de txto a funciones reales de Numpy. Esto nos permite que si el usuario escribe 'sin', el programa use np.sin automáticamente.
        try:  #En esta parte se hace una evaluación dinamica: Ejecutamos el texto como una operación matemática real.
            y = eval(txt_python, {"__builtins__": None}, contexto)  #Se desactivan los 'builtins' por seguridad para evitar ejecución de codigo malicioso.
            if isinstance(y, (int, float, np.float64)):  #Se hacen correcciones de dimenciones. Si el resultado es un numero fijo(osea constante), lo expandimos a un arreglo para que Matplotlib pueda dibujarlo como una línea.
                y = np.full_like(self.x, y)
            
            # Aqui lo que hicimos es crar una tabla de tabulación (donde solo utilizamos 11 puntos para que no sea infinita), esto facilita que el usuario vea coordenadas exactas (x,y) en la interfaz.
            x_tabla = np.linspace(-5, 5, 11) 
            y_tabla = eval(txt_python, {"__builtins__": None}, {"x": x_tabla, "np": np, "sin": np.sin, "cos": np.cos, "sqrt": np.sqrt})
            if isinstance(y_tabla, (int, float, np.float64)):
                y_tabla = np.full_like(x_tabla, y_tabla)
            
            # Unimos X y Y en una lista de diccionarios para el HTML
            tabulacion = [{"x": round(xi, 1), "y": round(yi, 2)} for xi, yi in zip(x_tabla, y_tabla)]
            
            return y, txt_python, tabulacion
        except Exception as e:  #Se manejan las excepciones. Si la funcion es valida, evitamos que el servidor colapse.
            print(f"Error detectado en el motor de cálculo: {e}")
            return None, None, None

    def generar_grafica(self, y_data):  #Transformamos los arreglos numericos en una imagen digital (PNG) codificada para su visualizacion en el navegador.
        plt.figure(figsize=(8, 4))  #Lo que hacemos aqui es configurar el lienzo: Creamos una figura de 8*4 pulgadas. Y para darle un estilo más bonito y presentable usamos el estilo 'dark_background' para que tambien combine con nuestra interfaz oscura. 
        plt.style.use('dark_background') 
        plt.plot(self.x, y_data, color='#2ed573', lw=2)  #Dibujamos la línea usando los ejes x y y. El color '#2ed573' es el verde neón que elegimos para que resaltara un poco más.
        plt.axhline(0, color='white', lw=0.5); plt.axvline(0, color='white', lw=0.5)  #Aqui se hacen los ejes cartesianos: dibujamos las líneas de origen (x=0, y=0)  para que el usuario sepa donde se encuentra el centro del plano.
        plt.grid(True, alpha=0.2)  #Con esto  añadimos una cuadricula tenue para facilitar la lectura de los puntos matemáticos.
        
        buf = io.BytesIO()  #LO que se hace en esta parte es que en lugar de guardar la foto en el disco duro, lo guardamos temporalmente en un 'flujo de bytes' en la memoria.
        plt.savefig(buf, format='png', bbox_inches='tight', transparent=True)
        buf.seek(0)  #Aqui regresamos al inicio del "archivo virtual" para leerlo.
        return base64.b64encode(buf.getvalue()).decode('utf-8')  #En esta línea de codigo convertimos la imagen binaria a texto ASCII. Esto nos permite enviar la imagen directamente dentro del codigo HTML sin necesidad de una URL externa.

AUTOR = {"materia": "Cálculo y Programación", "nombres": "Ana Martínez & Rubi Aguilar"}  #Configuramos los metadatos(que son datos sobre los datos, dicho de una manera mas sencilla). Se utiliza un diccionario para centralizar la información de proyecto. Esto facilita el mantenimiento si es que llegamos a cambiar algun dato, basicamente solo lo editariamos en esta misma línea y se actualizaria en toda la pagina automaticamente.

@app.route('/', methods=['GET', 'POST'])  #Aquie se hizo el puente entre el usuario y la logica matematica.
def index():
    resultado = None  #Definimos el resultado como None para que la interfaz no intente mostrar graficas vacias al cargar la pagina.
    if request.method == 'POST':  #Si el usuario envio el formulario...
        func_input = request.form.get('funcion', '')  #Capturamos la entrada del formulario usnado el atributo 'name' del HTML.
        calc = CalculadoraTICs(func_input)  #Creamos un objeto de nuestra clase logica.
        y, py, tabulacion = calc.obtener_datos()  #Solicitamos los datos calculados (y, sintaxis Python y Tabulacion)
        
        if y is not None:  #Solo si el cálculo fue correcto, generamos una respuesta.
            img = calc.generar_grafica(y)  #Generamos el renderizado visual, ose la grafica.
            resultado = {  #Creamos un objeto con toda la información pra que el frontend (HTML) la despliegue de forma adecuada.
                "img": img, 
                "original": func_input, 
                "py": py,
                "max": round(np.max(y), 2),  #Aqui se hace el calculo estadistico del punto más alto.
                "min": round(np.min(y), 2),  #Y aqui se hace el calculo del punto más bajo.
                "tabla": tabulacion
            }
            # Se guarda el historial (Al principio de la lista)
            historial_consultas.insert(0, {"fecha": "Reciente", "func": func_input})

    return render_template('index.html', autor=AUTOR, r=resultado, historial=historial_consultas[:5])  #Enviamos todos los datos al archivo index.html. Usamos Jinja2 (el motor de flask) para inyectar las variables en el HTML.

if __name__ == '__main__':  #Iniciamos el servidor en modo depuración, lo que permite ver errores detallados en consola y recargar cambios al instante.
    app.run(debug=True)