import pandas as pd
from openai import OpenAI

# Inicializa el cliente de OpenAI con la clave API
client = OpenAI(api_key='')

# Lee el archivo CSV
df = pd.read_csv('cleaned_descriptions.csv')

# Diccionario de caché para almacenar descripciones ya procesadas
cache = {}

# Función para procesar una descripción utilizando OpenAI
def process_description(description):
    if description in cache:
        return cache[description]
    
    new_description = f'''
    RESPONDE SOLO CON LA CLASIFICACIÓN ESPECÍFICA.
    
    Si no encuentras una clasificación apropiada, retorna "-".

    Clasifica la siguiente descripción con alguna de las siguientes clasificaciones universales:

    Electrónica
    Alimentos y Bebidas
    Ropa y Calzado
    Hogar y Jardín
    Salud y Belleza
    Juguetes y Juegos
    Automotriz
    Consultoría y Asesoría
    Servicios Médicos
    Servicios Educativos
    Servicios de Tecnología
    Servicios de Mantenimiento y Reparación
    Servicios de Transporte
    Entretenimiento y Eventos
    Deportes y Recreación
    Productos para Mascotas
    Papelería y Oficina
    Herramientas y Equipamiento
    Servicios Financieros
    Viajes y Turismo
    Muebles y Decoración
    Construcción y Remodelación
    Servicios de Limpieza
    Servicios de Seguridad
    Publicidad y Marketing
    Servicios de Belleza y Spa
    Logística y Almacenamiento
    Servicios Legales
    Agricultura y Ganadería
    Energía y Suministros
    Servicios de Alimentos y Catering
    Servicios de Bienestar y Fitness
    Servicios de Telecomunicaciones
    Arte y Artesanías

    DESCRIPCIÓN "{description}"
    '''

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": new_description,
            }
        ],
        model="gpt-3.5-turbo",
    )
    # Extraer el mensaje de respuesta del asistente
    assistant_message = chat_completion.choices[0].message.content
    print(description, '->', assistant_message)
    
    # Almacenar la respuesta en la caché
    cache[description] = assistant_message
    
    return assistant_message

# Procesa cada descripción y guarda el resultado en una nueva columna
df['cleaned_final_description'] = df['initial_description'].apply(process_description)

# Guarda el DataFrame modificado en un nuevo archivo CSV
df.to_csv('updated_csvfile.csv', index=False)

print("Procesamiento completado y archivo CSV guardado.")
