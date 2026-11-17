# PPOL · Plataforma de Prácticas y Oportunidades Laborales

> **Universidad Cooperativa de Colombia — Sede Montería**<br>
> **Facultad de Ingeniería de Sistemas**<br>
> **Asignatura:** Herramientas Computacionales para Interpretación y Validación de Resultados<br>
> **Docente:** Delia Marina Herazo Tuiran<br>
> **Año:** 2026

---

### Integrantes del Proyecto:
- **Sara Urzola Causil**
- **Santiago Herrera Jimenez**
- **Juan Santiago Blanco Herrera**
- **Jhonny Alexander Hernández Escudero**

---

## 1. Descripción del Proyecto y Problemática

En las instituciones de educación superior, la conexión entre estudiantes, empresas y convocatorias de práctica formativa o primer empleo suele verse afectada por:
1. **Gestión manual y dispersa:** Ofertas divulgadas por cadenas de correos, carteleras o grupos de mensajería, con hojas de vida recibidas en formatos heterogéneos y hojas de cálculo sueltas.
2. **Falta de visibilidad y trazabilidad:** Los estudiantes desconocen el estado de sus postulaciones y las empresas no logran filtrar ágilmente a los mejores talentos.
3. **Ausencia de indicadores centrales:** La institución carece de métricas cuantitativas sobre tasas de vinculación, demanda por programa académico y áreas más activas.

**PPOL** es una aplicación web Full Stack diseñada en Python (Django) que centraliza el proceso de intermediación laboral-académica con trazabilidad en tiempo real, validación administrativa, indicadores dinámicos y generación de informes institucionales en Excel y PDF.

---

## 2. Arquitectura del Sistema (Full Stack MVT)

El sistema implementa una arquitectura desacoplada basada en el patrón **MVT (Model-View-Template)**:

```
[ FRONTEND ]
HTML5 Semántico + Bootstrap 5.3 + CSS3 Minimalista Enterprise + Bootstrap Icons
(Validación cliente, feedback reactivo, microinteracciones, tabs dinámicos)
              │
              ▼ (HTTP / Fetch / Form POST con CSRF)
[ BACKEND (Django 5/6 + Python 3.x) ]
Controladores y Vistas funcionales (core/views.py)
Middlewares de Seguridad, Autenticación y Context Processors
              │
              ├──► [ MODELOS & ORM ] ──► [ BASE DE DATOS (MySQL/MariaDB XAMPP) ]
              │    (User, StudentProfile, Company, Offer, Application, StatusLog, Area, Notification)
              │
              └──► [ EXPORTADORES & SERVICIOS ]
                   ├──► openpyxl (Reportes nativos en Excel .xlsx)
                   ├──► reportlab (Informes institucionales en PDF .pdf)
                   └──► SMTP / Console Mail (Notificaciones automáticas)
```

---

## 3. Módulos funcionales implementados

| ID | Prioridad | Historia de Usuario | Estado | Funcionalidad Implementada |
|---|---|---|:---:|---|
| **HU01** | Must Have | Registro e inicio de sesión de estudiante | Implementado | Validación de código estudiantil único, correo único y control de acceso por rol (`/registro/estudiante/`). |
| **HU02** | Must Have | Gestión del perfil del estudiante | Implementado | Información académica, competencias, carga de CV PDF, intereses y porcentaje de completitud (`/perfil/`). |
| **HU03** | Must Have | Búsqueda y filtrado de ofertas | Implementado | Filtros por palabra clave, empresa, modalidad, tipo de oferta, área y ciudad (`/ofertas/`). |
| **HU04** | Must Have | Postulación a convocatorias | Implementado | Validación de CV y vigencia, prevención de duplicados y notificación a la empresa (`/ofertas/<id>/`). |
| **HU05** | Should Have | Seguimiento y retiro de postulaciones | Implementado | Estados, retiro no destructivo y registro histórico (`/mis-postulaciones/`). |
| **HU06** | Must Have | Registro y perfil corporativo de la empresa | Implementado | Registro con NIT único, validación administrativa y edición del perfil (`/empresa/perfil/`). |
| **HU07** | Must Have | Publicación y administración de ofertas | Implementado | Crear y editar ofertas, revisión administrativa, pausa, reanudación y cierre (`/empresa/ofertas/`). |
| **HU08** | Must Have | Revisión y gestión de candidatos | Implementado | Gestión de estados, notas y notificaciones (`/empresa/ofertas/<id>/postulantes/`). |
| **HU09** | Should Have | Filtrado y comparación de candidatos | Implementado | Filtros por programa, semestre, habilidades e idiomas, favoritos y comparación (`/empresa/ofertas/<id>/comparar/`). |
| **HU10** | Must Have | Gestión de usuarios, validaciones y áreas | Implementado | Aprobación/rechazo, administración de cuentas y CRUD de áreas (`/panel/validaciones/`, `/panel/usuarios/`, `/panel/areas/`). |
| **HU11** | Should Have | Reportes e indicadores institucionales | Implementado | Filtros, indicadores y exportaciones a CSV, Excel y PDF (`/panel/reportes/`). |
| **HU12** | Could Have | Alertas y ofertas afines al perfil | Implementado | Intereses, preferencias de notificación, recomendaciones y avisos al aprobar ofertas afines. |

La matriz documenta módulos disponibles; el grado de cumplimiento de la asignatura debe sustentarse con la demostración y los entregables indicados en los lineamientos.

---

## 4. Tecnologías Empleadas

- **Lenguaje:** Python 3.13 / 3.x
- **Framework Web:** Django (arquitectura MVT)
- **Base de Datos:** MySQL/MariaDB de XAMPP con llaves primarias, foráneas e integridad referencial (SQLite opcional para desarrollo local)
- **Frontend:** HTML5 semántico, Bootstrap 5.3, diseño UI minimalista y profesional para software corporativo/universitario (paleta neutral pizarra `#0f172a`, bordes nítidos, sin clichés de IA), tipografía Google Fonts (Inter), Bootstrap Icons y JavaScript nativo (ES6) para interactividad y validaciones dinámicas.
- **Bibliotecas Complementarias:**
  - `openpyxl`: Generación y formateo de libros de cálculo Excel (.xlsx) con estilos y paleta institucional.
  - `reportlab`: Renderizado vectorial de documentos PDF oficiales con encabezados, tablas y KPIs.
  - `Pillow`: Manejo y procesamiento seguro de archivos multimedia.

---

## 5. Instrucciones de Puesta en Marcha

### Prerrequisitos:
- Python 3.10 o superior instalado en el equipo.
- XAMPP con MySQL/MariaDB activo si se elige ese motor. Para desarrollo local también se puede usar SQLite sin instalar XAMPP.

### Paso 1: Abrir el proyecto
```bash
cd ppol
```

### Paso 2: Crear y activar el entorno virtual
En Windows PowerShell:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

En Windows CMD:
```bat
python -m venv venv
venv\Scripts\activate.bat
```

En Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Elegir y configurar la base de datos
Si todavía no tienes un archivo `.env`, crea uno a partir de la plantilla:
```powershell
Copy-Item .env.example .env
```
En Linux / macOS usa `cp .env.example .env`.

Elige **una** de estas opciones en `.env`:

- **SQLite (recomendado para iniciar localmente):** configura `DB_ENGINE=sqlite`. No requiere XAMPP ni crear una base manualmente; Django creará `db.sqlite3` al aplicar las migraciones.
- **MySQL/MariaDB con XAMPP:** deja `DB_ENGINE=mysql`, inicia **MySQL** desde el panel de XAMPP y crea `ppol_db` en phpMyAdmin (`http://localhost/phpmyadmin`) ejecutando [`database/create_database.sql`](./database/create_database.sql). Si tu instalación no usa los valores predeterminados, ajusta `DB_USER`, `DB_PASSWORD`, `DB_HOST` y `DB_PORT` en `.env`.

### Paso 5: Aplicar migraciones y cargar datos de demostración
En Windows PowerShell, habilita la salida UTF-8 para que los símbolos del comando `seed` se impriman correctamente:
```powershell
$env:PYTHONIOENCODING = "utf-8"
```

Luego ejecuta:
```powershell
python manage.py migrate
python manage.py seed
```
> `seed` crea o actualiza las cuentas de demostración. No lo ejecutes sobre una base de producción.

### Paso 6: Ejecutar el servidor de desarrollo
```powershell
python manage.py runserver
```

Abre en tu navegador: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**. Si aparece un error de conexión a `127.0.0.1:3306`, MySQL no está activo; inicia MySQL en XAMPP o cambia `DB_ENGINE=sqlite` en `.env`.

---

## 6. Usuarios de Prueba y Credenciales de Demostración

El comando `python manage.py seed` aprovisiona los siguientes usuarios listos para la sustentación:

| Rol | Correo Electrónico | Contraseña | Finalidad en la Demostración |
|---|---|---|---|
| **Administrador** | `admin@ppol.co` | `admin12345` | Validar empresas y ofertas, ver reportes, exportar Excel/PDF, activar/suspender usuarios y gestionar áreas. |
| **Empresa (Aprobada)** | `rrhh@tecnova.co` | `empresa12345` | Publicar ofertas, evaluar candidatos, marcar favoritos, comparar y cambiar estados de postulación. |
| **Empresa (Pendiente)** | `talento@agrosol.co` | `empresa12345` | Demostrar el flujo de validación institucional de nuevas organizaciones. |
| **Estudiante (Completo)** | `carlos@uni.edu.co` | `estudiante12345` | Ver estado de postulaciones, timeline histórico, retirar aplicación y filtrar ofertas afines. |
| **Estudiante (Para postular)** | `laura@uni.edu.co` | `estudiante12345` | Demostrar edición de perfil (HU02), carga de PDF y postulación a una vacante en tiempo real (HU04). |
| **Estudiante (Vinculada)** | `sara@uni.edu.co` | `estudiante12345` | Evidenciar postulaciones en estado «Aceptada» (vinculación efectiva para reportes). |

---

## 7. Pruebas automatizadas

Las pruebas usan SQLite en memoria para no necesitar XAMPP, no tocar la base local y permitir integración continua:

```powershell
python manage.py check --settings=ppol.test_settings
python manage.py test --settings=ppol.test_settings
```

Para comprobar la conexión y las migraciones de XAMPP, inicia MySQL en XAMPP y ejecuta:

```powershell
python manage.py migrate --plan
python manage.py check
```

GitHub Actions ejecuta estas pruebas para Python 3.10–3.14 mediante [`.github/workflows/tests.yml`](./.github/workflows/tests.yml).

## 8. Publicar el proyecto en GitHub

Crea un repositorio vacío en GitHub y, desde PowerShell en la carpeta del proyecto, publica los archivos con:

```powershell
git add .
git commit -m "Publicar plataforma PPOL"
git branch -M main
git remote add origin https://github.com/<usuario>/<repositorio>.git
git push -u origin main
```

No agregues `.env`, bases de datos locales ni archivos subidos en `media/`; están excluidos por [`.gitignore`](./.gitignore). Revisa `git status` antes de publicar.

## 9. Sustentación y entrega

- Guía de navegación y sustentación: [`docs/GUIA_SUSTENTACION_Y_PRESENTACION.md`](./docs/GUIA_SUSTENTACION_Y_PRESENTACION.md).
- Los lineamientos también piden diapositivas (máximo 3 minutos) y un video de hasta 10 minutos. Esos materiales no forman parte del código de la aplicación.
- **Padlet de la asignatura:** [Entrega institucional](https://padlet.com/ingdeliamarherazo/padlet-hcomputacionales-r4qf9trzhqw8qpnd).
