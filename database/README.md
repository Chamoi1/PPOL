# Base de datos PPOL

Este directorio contiene los archivos de preparación de la base MySQL/MariaDB usada por PPOL en XAMPP.

## Crear la base en XAMPP

1. Inicia **MySQL** desde XAMPP Control Panel.
2. Abre phpMyAdmin en `http://localhost/phpmyadmin`.
3. Selecciona **Importar** y carga `create_database.sql`, o ejecuta su contenido en la pestaña **SQL**.

El script crea `ppol_db` con codificación `utf8mb4` y puede ejecutarse más de una vez sin borrar datos existentes.

## Crear las tablas

Las tablas no se crean manualmente desde este directorio. Desde la raíz del proyecto y con el entorno virtual activado, ejecuta:

```powershell
python manage.py migrate
```

La conexión se configura en el archivo `.env` de la raíz del proyecto. Nunca guardes contraseñas en los scripts SQL.
