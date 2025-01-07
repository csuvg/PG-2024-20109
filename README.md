# Proyecto Final de Graduación

## Descripción
La contabilidad es una de las áreas donde menos innovación se ha visto en décadas. A pesar de avances como los sistemas ERP (Enterprise Resource Planning), muchos de los procesos fundamentales permanecen manuales y repetitivos. Este proyecto busca abordar esa falta de innovación mediante la investigación e implementación de un sistema de clasificación automática de facturas utilizando inteligencia artificial y técnicas de aprendizaje automático.

El resultado final es un sistema replicable, diseñado para trabajar con datasets demo, que permite la automatización de procesos clave en la clasificación de facturas y demuestra cómo las herramientas de IA pueden transformar la contabilidad.

---

## Instrucciones de Instalación

### Requisitos Previos
Antes de ejecutar el proyecto, asegúrate de tener instalado lo siguiente:
- Python 3.8 o superior
- Dependencias enumeradas en el archivo `requirements.txt`

### Instalación
1. Clona este repositorio:
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_REPOSITORIO>
   ```
2. Instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

### Ejecución de la Aplicación
Para poner en marcha la aplicación:
1. Ejecuta el análisis de datos en el notebook correspondiente:
   ```bash
   jupyter notebook "src/Análisis de Datos/analisis_de_datos.ipynb"
   ```
2. Para probar el Clasificador Universal:
   ```bash
   python "src/Clasificador Universal Con OpenAI/clasificador_universal.py"
   ```
3. Para iniciar las funciones de clasificación locales:
   ```bash
   python main.py
   ```

---

## Demo
Una demostración visual del proyecto en acción se encuentra en la carpeta `/demo/`. 

---

## Informe Final
El informe final de este proyecto, que incluye todos los detalles técnicos y académicos, está disponible en formato PDF en la carpeta `/docs/`. Puedes acceder a él directamente desde este repositorio:

- [Informe Final](docs/informe_final.pdf)

---

## Estructura del Proyecto
El proyecto está organizado en varias etapas que reflejan el proceso de desarrollo y análisis:

### 1. **Análisis de Datos**
Esta fase incluyó un análisis profundo y exhaustivo de los datos. Se utilizó un notebook de Python con las siguientes librerías:

```python
import pandas as pd
import json
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
```

En esta etapa se limpiaron, imputaron y transformaron los datos para preparar el dataset. Las visualizaciones y análisis estadísticos iniciales ayudaron a identificar patrones clave que guiarían la construcción del modelo.

### 2. **Modelado Predictivo**
Se desarrolló y estructuró un modelo de predicción utilizando un enfoque de aprendizaje supervisado. Finalmente, se seleccionó un Random Forest como el modelo principal por su rendimiento y capacidad de manejar datos complejos.

Adicionalmente, se implementaron técnicas de procesamiento de lenguaje natural (NLP) para extraer insights adicionales de los registros, utilizando modelos como **BERT** y **GPT-3** (OpenAI). 

#### Clasificador Universal con OpenAI
Este componente es un script ejecutable que utiliza las siguientes librerías:

```python
import pandas as pd
from openai import OpenAI
```

#### Comparación de Modelos
La comparación de modelos se realizó en un notebook que evaluó diversos enfoques y combinaciones de modelos:

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import lightgbm as lgb
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
```

### 3. **Funciones Locales**
Se implementaron funciones para acceder y utilizar los modelos generados. Estas funciones están escritas como scripts ejecutables y utilizan las siguientes librerías:

#### Clasificador Automático
```python
import numpy as np
from flask import Flask, request, jsonify
from controllers import predictValue
import joblib
import os
```

#### Entrenamiento del Modelo
```python
import os
import json
import pandas as pd
import numpy as np
import joblib
from flask import Flask, request, jsonify
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from voluptuous import MultipleInvalid
from schemas import notificationSchema
from voluptuous import Schema, Required, Any
```

---

## Limitaciones
Este proyecto se centró en demostrar cómo implementar un sistema de clasificación automática de facturas, pero se limitaron algunas funcionalidades para garantizar su replicabilidad y facilidad de uso:
- **Dataset Demo**: El sistema se probó con datasets reducidos y limpiados, lo que limita su escalabilidad inmediata a entornos de producción.
- **Eliminación de Configuraciones GCP**: Con el objetivo de hacer más fácil de replicar este proyecto y dado que su naturaleza era principalmente de investigación, se eliminaron las referencias a GCP para dado que esto se puede implementar en cualquier nube-herramienta. Esto facilita el análisis del código y sus pruebas.

---

## Conclusión
Este proyecto demuestra cómo las herramientas modernas de inteligencia artificial y aprendizaje automático pueden transformar procesos tradicionales en la contabilidad, como la clasificación de facturas. Aunque se limitó en ciertos aspectos, el código es funcional, replicable y demuestra los principios fundamentales de un sistema de automatización.

Este trabajo no solo aporta valor académico, sino que también abre puertas para futuras investigaciones y aplicaciones en automatización contable.

