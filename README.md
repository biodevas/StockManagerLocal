# Sistema de Inventario de Bebidas

Un sistema de gestión de inventario de bebidas multilingüe con interfaz táctil, implementando seguimiento de stock, gestión de reabastecimiento y análisis de ventas basado en productos.

## Características Principales

- Interfaz táctil amigable
- Gestión de inventario y reabastecimiento
- Autenticación de usuarios y rutas protegidas
- Notificaciones por email para stock bajo
- Seguimiento detallado de transacciones
- Exportación de reportes en formato CSV
- Análisis de ventas con filtros por fecha
- Gráficos interactivos y análisis de rendimiento por producto
- Soporte multilingüe (Español e Inglés)
- Gestión de imágenes con soporte para WebP, AVIF, JPG, PNG

## Requisitos del Sistema

- Python 3.11 o superior
- PostgreSQL 12 o superior
- Cuenta de Gmail para notificaciones SMTP

## Instrucciones de Instalación Local

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Configurar Base de Datos PostgreSQL

1. Instalar PostgreSQL si aún no está instalado
2. Crear una nueva base de datos:
```sql
CREATE DATABASE beverage_inventory;
```

### 3. Configurar Variables de Entorno

Crear un archivo `.env` en el directorio raíz con las siguientes variables:

```
DATABASE_URL=postgresql://usuario:contraseña@localhost:5432/beverage_inventory
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu-email@gmail.com
SMTP_PASSWORD=tu-contraseña-de-aplicación
```

Notas importantes sobre la configuración del email:
- Para Gmail, necesitarás generar una "Contraseña de aplicación" específica
- Activar la verificación en dos pasos en tu cuenta de Gmail
- En la configuración de seguridad de Gmail, generar una contraseña de aplicación

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Crear Imagen por Defecto

```bash
python create_default_image.py
```

### 6. Inicializar la Base de Datos

```bash
python update_schema.py
python verify_schema.py
```

### 7. Ejecutar la Aplicación

```bash
python main.py
```

La aplicación estará disponible en `http://localhost:5000`

## Estructura del Proyecto

```
├── app.py                 # Aplicación principal Flask
├── models.py             # Modelos de base de datos
├── email_service.py      # Servicio de notificaciones por email
├── static/              # Archivos estáticos
│   ├── css/            # Hojas de estilo
│   ├── js/             # Scripts JavaScript
│   └── uploads/        # Imágenes subidas
└── templates/          # Plantillas HTML
```

## Configuración de Desarrollo

- El modo debug está activado por defecto en desarrollo
- Los archivos estáticos se sirven automáticamente
- Las plantillas se recargan automáticamente al hacer cambios

## Notas de Seguridad

- Todas las contraseñas se almacenan hasheadas usando Werkzeug
- Las rutas están protegidas mediante Flask-Login
- Las imágenes subidas se validan y procesan de forma segura
- Las consultas SQL utilizan SQLAlchemy para prevenir inyecciones

## Soporte

Para reportar problemas o solicitar nuevas características, por favor crear un issue en el repositorio de GitHub.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.
