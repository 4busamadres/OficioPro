# OficioPro

Prototipo Django para administrar y ofrecer servicios de trabajadores independientes.

## Base de datos

El desarrollo usa SQLite porque es gratuito, no requiere un servidor y permite validar el producto. La configuración admite PostgreSQL o MySQL mediante variables de entorno. Para producción con varios usuarios concurrentes se recomienda PostgreSQL.

## Instalación local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Django no carga `.env` automáticamente. En desarrollo puedes conservar los valores predeterminados seguros solo para uso local o definir las variables en PowerShell antes de iniciar. Nunca uses la clave de desarrollo en producción.

Abre `http://127.0.0.1:8000/`.

`seed_demo` crea un cliente y un prestador y muestra contraseñas temporales aleatorias una sola vez. Si los usuarios ya existen, no cambia sus claves.

## Pruebas

```powershell
python manage.py test
python manage.py check
```

## Flujo disponible

1. Crear una cuenta como cliente o prestador.
2. Iniciar y cerrar sesión.
3. Acceder al panel correspondiente al rol.
4. Administrar usuarios desde `/admin/` usando un superusuario.

El registro público nunca permite crear administradores.

## Producción

Antes de desplegar:

- Define `DJANGO_SECRET_KEY` con una clave secreta real.
- Usa `DJANGO_DEBUG=False`.
- Configura `DJANGO_ALLOWED_HOSTS` y `DJANGO_CSRF_TRUSTED_ORIGINS`.
- Usa PostgreSQL y define todas las variables `DATABASE_*`.
- Instala un servidor WSGI y un controlador PostgreSQL.
- Ejecuta `python manage.py check --deploy`, migraciones y recolección de estáticos.

### Ruta de despliegue recomendada

1. Publicar el código en un repositorio Git privado o público.
2. Crear una base PostgreSQL administrada y guardar sus datos solo como variables de entorno.
3. Crear un servicio web conectado al repositorio.
4. Instalar las dependencias de producción (`gunicorn`, `psycopg` y `whitenoise`).
5. Ejecutar migraciones durante cada despliegue.
6. Configurar almacenamiento de objetos para las imágenes del portafolio; no guardarlas en el disco temporal del servidor.
7. Hacer una copia de seguridad antes de migrar datos desde SQLite.

Para una demostración sin presupuesto, SQLite puede alojarse en un servicio que conserve el disco. Si el proveedor usa un sistema de archivos efímero, hay que utilizar PostgreSQL externo: de lo contrario, las cuentas y reservas desaparecerán al reiniciar el servicio.

El archivo `index.html` original se conserva sin modificaciones como referencia del prototipo visual inicial.
