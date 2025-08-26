# 🚀 Cómo Ejecutar el Proyecto - MercadoLibre Items API

Este documento explica cómo configurar y ejecutar la API RESTful de productos con arquitectura DDD.

## 📋 **Prerrequisitos**

- **Python 3.8+** (recomendado 3.11 o superior)
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

## 🛠️ **Instalación y Configuración**

### **1. Clonar el Repositorio**
```bash
git clone <url-del-repositorio>
cd tecnica4.0
```

### **2. Crear Entorno Virtual**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### **3. Instalar Dependencias**
```bash
pip install -r requirements.txt
```

### **3. Configurar Variables de Entorno**
```bash
# Copiar archivo de configuración
copy .env.example .env

# O en Linux/macOS
cp .env.example .env
```

## 🏃‍♂️ **Ejecutar la Aplicación**

### **Método Recomendado**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### **Alternativas**
```bash
# Puerto 8000 (por defecto)
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Solo localhost
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

## 🌐 **Acceder a la API**

Una vez ejecutada la aplicación, puedes acceder a:

- **API Base URL**: `http://localhost:8001`
- **Documentación Swagger UI**: `http://localhost:8001/docs`
- **Documentación ReDoc**: `http://localhost:8001/redoc`
- **Health Check**: `http://localhost:8001/api/v1/health`
- **Endpoint de Prueba**: `http://localhost:8001/test`

## 🧪 **Ejecutar Tests**

### **Ejecutar Todos los Tests**
```bash
pytest
```

### **Ejecutar Tests con Verbosidad**
```bash
pytest -v
```

### **Ejecutar Tests Específicos**
```bash
pytest tests/test_items.py -v
```

### **Ejecutar Tests con Cobertura**
```bash
pytest --cov=app tests/
```

## 📊 **Endpoints Disponibles**

### **Endpoints Principales**
- `GET /api/v1/health` - Verificar estado del servicio
- `GET /api/v1/items/{item_id}` - Obtener detalle de producto
- `GET /api/v1/items` - Buscar productos
- `GET /api/v1/items/{item_id}/recommendations` - Obtener recomendaciones
- `GET /api/v1/items/popular` - Productos populares
- `GET /api/v1/items/available` - Productos disponibles

### **Ejemplos de Uso**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Obtener producto específico
curl http://localhost:8000/api/v1/items/MLA123456789

# Buscar productos
curl "http://localhost:8000/api/v1/items?q=iphone&limit=5"

# Obtener recomendaciones
curl http://localhost:8000/api/v1/items/MLA123456789/recommendations?k=3
```

## 🔧 **Configuración del Entorno**

### **Variables de Entorno (Opcional)**
Crea un archivo `.env` en la raíz del proyecto:

```env
# Configuración de la aplicación
APP_NAME=Item Detail API
APP_VERSION=1.0.0
DEBUG=true

# Configuración del servidor
HOST=0.0.0.0
PORT=8000

# Configuración de datos
DATA_FILE=app/data/items.json
```

## 📁 **Estructura del Proyecto**

```
tecnica/
├── app/
│   ├── core/           # Configuración y excepciones
│   ├── domain/         # Entidades y lógica de negocio
│   ├── infrastructure/ # Repositorios y serializadores
│   ├── presentation/   # Controladores y routers
│   ├── data/          # Archivos de datos JSON
│   └── main.py        # Punto de entrada
├── tests/             # Tests unitarios
├── docs/              # Documentación
├── requirements.txt   # Dependencias
└── README.md         # Documentación principal
```

## 🐛 **Solución de Problemas**

### **Error: Puerto ya en uso**
```bash
# Cambiar puerto
uvicorn app.main:app --reload --port 8001
```

### **Error: Módulo no encontrado**
```bash
# Verificar que el entorno virtual esté activado
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### **Error: Dependencias faltantes**
```bash
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

## 📈 **Monitoreo y Logs**

### **Ver Logs en Tiempo Real**
```bash
# Con uvicorn
uvicorn app.main:app --reload --log-level debug
```

### **Verificar Estado del Servicio**
```bash
curl http://localhost:8000/api/v1/health
```

## 🚀 **Despliegue en Producción**

### **Usando Gunicorn (Recomendado)**
```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### **Usando Docker (Opcional)**
```bash
# Construir imagen
docker build -t item-detail-api .

# Ejecutar contenedor
docker run -p 8000:8000 item-detail-api
```

## 📞 **Soporte**

Si encuentras problemas:

1. **Verificar logs**: Revisar la salida de la consola
2. **Documentación**: Consultar `/docs` en el navegador
3. **Tests**: Ejecutar `pytest` para verificar funcionalidad
4. **Issues**: Crear un issue en el repositorio

---

**¡La API está lista para usar!** 🎉

Para más información, consulta el `README.md` principal del proyecto.
