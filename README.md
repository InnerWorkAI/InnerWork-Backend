# InnerWork AI - Backend

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python 3.11](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=for-the-badge&logo=TensorFlow&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

Este repositorio contiene el código fuente del backend para la plataforma **InnerWork AI**, una API RESTful desarrollada en **FastAPI**. Su propósito principal es gestionar entidades empresariales (usuarios, empresas, empleados) y proveer servicios avanzados de **Machine Learning** enfocados en la evaluación predictiva de estrés y riesgo de burnout (desgaste laboral).

## Modelos de Machine Learning Implementados

El sistema integra predicciones provenientes de modelos de inteligencia artificial pre-entrenados del componente `app/ml_models`, los cuales son consumidos a través de endpoints específicos:

1. **Modelo Convolucional (Imágenes Faciales):** 
   - Archivo: `stress_image_predictor.h5`
   - Framework: **TensorFlow/Keras**
   - Propósito: Extrae y clasifica características de retratos visuales de empleados para determinar indicadores de estrés.
   - Endpoint Clave: Operado principalmente a través de `image_predictor_controller`.

2. **Modelo SVM de Procesamiento de Lenguaje (Audio/Texto):**
   - Archivos: `svm_calibrated_model.joblib` y `tfidf_vectorizer.joblib`
   - Framework: **Scikit-Learn**
   - Propósito: Analiza transcripciones (Speech-to-Text de audios) para interpretar el estrés basado en la estructura emocional del lenguaje.
   - Endpoint Clave: Operado principalmente a través de `audio_predictor_controller`.

3. **Modelo Predictor de Atrición Laboral y Burnout:**
   - Archivo: `employee_attrition.joblib`
   - Framework: **Scikit-Learn / XGBoost**
   - Propósito: Anticipa la probabilidad de deserción (turnover) y picos críticos de burnout procesando datos estructurados provenientes de reportes semanales.
   - Endpoint Clave: Se alimenta de métricas capturadas y analizadas en `weekly_burnout_form_controller`.

## Tecnologías y Arquitectura

- **Framework Web Core:** FastAPI (Python 3.11)
- **Motor de Base de Datos Relacional:** PostgreSQL
- **Mapeo Objeto-Relacional (ORM):** SQLAlchemy
- **Criptografía y Autenticación:** Tokens JWT y funciones hash unidireccionales (Bcrypt)
- **Data Science:** OpenCV, Pillow, numpy, joblib (para inferencia y manipulación de medios)
- **Automatización y Tareas:** APScheduler
- **Integraciones Externas (Emails y LLMs):** Resend, OpenAI HTTP Clients
- **Infraestructura Ágil:** Docker y Docker Compose

## Organización del Arquetipo (app/)

El ecosistema dentro del directorio principal respeta una arquitectura de componentes modulares y bajo acoplamiento, separando claramente la capa de transporte (controladores) de la capa de datos (modelos/repositorios):

```text
app/
├── agents/           [Integración] Interactuadores de API con LLMs de terceros (ej. OpenAI)
├── controllers/      [Red] Definición de enrutadores y endpoints públicos/privados
├── core/             [Configuración] Gestión centralizada del entorno (settings.py y seguridad vital)
├── db/               [Persistencia] Conexión asíncrona a base de datos y fábrica de sesiones SQLAlchemy
├── enums/            [Tipos] Enumeradores globales y convenciones estáticas (Gender, Roles)
├── ml_models/        [Machine Learning] Almacenamiento binario local para modelos pre-entrenados
├── models/           [Datos] Clases SQLAlchemy correspondientes al esquema analítico RDBMS
├── repositories/     [Persistencia] Interactuación con colecciones abstractas de DB
├── schemas/          [Validación] Objetos de Transferencia de Datos (DTO) usando Pydantic V2
├── seeders/          [Testing] Programas de inyección e hidratación para escenarios de pruebas
├── services/         [Dominio] Módulo con la lógica de negocio imperativa
├── tasks/            [Background] Manejo de triggers en segundo plano (Recordatorios semanales)
└── main.py           [Entrypoint] App delegada de FastAPI e inicializador de ciclo de vida (lifespan)
```

## Especificaciones e Inicialización

**Dependencias Críticas:**
- Python 3.11 o posterior.
- Base de datos PostgreSQL local o remota.
- Herramienta de contenedores como Docker Compose (Opcional, pero recomendado).

### Variables de Entorno Obligatorias
Antes de arrancar la aplicación, ya sea local o mediante Docker, se debe crear un archivo `.env` o `.env.development` en el directorio raíz. Controles vitales mínimos que este archivo debe definir:
- `DATABASE_URL`: Cadena de conexión a PostgreSQL (Ej: `postgresql://user:pass@host:5432/dbname`)
- `SECRET_KEY`: Semilla criptográfica para la firma de tokens JWT.
- `RESEND_API_KEY`: API Key para la pasarela de envíos de email de recordatorio en segundo plano.
- `OPENAI_API_KEY`: Claves de facturación del servicio cognitivo en la nube.

### Despliegue Mediante Contenedores

Es la vía más recomendada porque levanta y vincula contenedores inmersos, resolviendo dependencias por sí mismo.

1. Construir e iniciar componentes en segundo plano:
   ```bash
   docker-compose up --build
   ```
2. Una vez que las capas están consolidadas, el puerto vinculante será `http://localhost:8000`.

### Construcción Tradicional Local

1. **Pre-requisito de Base de Datos:** Crear una base de datos vacía en el sistema local PostgreSQL que concuerde con la cadena informada en `DATABASE_URL`. SQLAlchemy creará dinámicamente el esquema de tablas sobre esta base instanciada.

2. Creación de un subsistema aislado de dependencias (entorno virtual):
   ```bash
   python -m venv venv
   # Terminal local Windows:
   venv\Scripts\activate
   # Terminal Unix / Bash:
   source venv/bin/activate
   ```

3. Resolución de dependencias librerías del proyecto:
   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. Instanciación del servidor Uvicorn en caliente:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## Documentación de la API Interactiva

Suministrada por FastAPI de forma nativa. Una vez expuesto el servidor, los componentes y sus esquemas son visibles interactuando en las siguientes URL:

- Plataforma de pruebas **Swagger UI:** `http://localhost:8000/swagger`
- Vista documental compacta **ReDoc:** `http://localhost:8000/redoc`

## Procesos Autónomos

A través del evento contextual `lifespan` en `main.py`:

1. El orquestador del ciclo de vida arranca **APScheduler**. Proporciona disparadores en segundo plano para envío de alertas (emails preconfigurados) sin interrumpir los Event Loops entrantes.
2. Si la variable de entorno actual equivale al ambiente de desarrollo (`ENV="development"`), los módulos **seeders** proceden a insertar registros iniciales controlados para agilizar validaciones.

## Comandos y Utilidades Rápidas

A continuación se listan atajos comunes para la operativa diaria del repositorio:

| Acción | Comando |
| :--- | :--- |
| **Arrancar el servidor** | `uvicorn app.main:app --reload` |
| **Instalar requerimientos** | `pip install -r requirements.txt` |
| **Construir Docker** | `docker-compose up --build` |
| **Limpiar caché de Python** | `find . -type d -name __pycache__ -exec rm -r {} \+` |
