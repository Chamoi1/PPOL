# GUÍA MAESTRA DE SUSTENTACIÓN Y PRESENTACIÓN
## PLATAFORMA DE PRÁCTICAS Y OPORTUNIDADES LABORALES (PPOL)
### Momento Evaluativo 3 · Herramientas Computacionales
**Docente:** Delia Marina Herazo Tuiran
**Facultad:** Ingeniería de Sistemas, Universidad Cooperativa de Colombia — Montería, 2026
**Integrantes:**
1. **Sara Urzola Causil**
2. **Santiago Herrera Jimenez**
3. **Juan Santiago Blanco Herrera**
4. **Jhonny Alexander Hernández Escudero**

---

## ⏱️ Estructura Cronometrada de la Sustentación (10 Minutos Estrictos)

```
┌────────────────────────────────────────────────────────┐
│ TOTAL: 10 MINUTOS                                     │
├─────────────────────────┬──────────────────────────────┤
│ PARTE 1: DIAPOSITIVAS   │ PARTE 2: DEMO EN VIVO        │
│ (Máximo 3 Minutos)      │ (Máximo 7 Minutos)           │
│ Integrantes 1 y 2       │ Integrantes 3 y 4 (y apoyo)  │
└─────────────────────────┴──────────────────────────────┘
```

---

## PARTE 1: SOPORTE VISUAL / DIAPOSITIVAS (Máximo 3 minutos)

### 📌 Diapositiva 1: Portada Institucional
- **Título:** Plataforma de Prácticas y Oportunidades Laborales (PPOL)
- **Subtítulo:** Sistema Full Stack para la vinculación laboral y seguimiento de prácticas formativas
- **Presentado por:** Sara Urzola, Santiago Herrera, Juan Santiago Blanco, Jhonny Hernández
- **Docente:** Delia Marina Herazo Tuiran
- **Universidad Cooperativa de Colombia** — 2026

---

### 📌 Diapositiva 2: El Problema y Justificación (Obligatorio)
**Orador Asignado:** Sara Urzola Causil (Tiempo: ~1:00 min)
- **Contexto:** La vinculación a prácticas profesionales es un pilar fundamental en la educación superior, pero tradicionalmente se gestiona de manera informal y descentralizada.
- **Puntos Críticos Identificados:**
  1. *Dispersión de canales:* Convocatorias transmitidas por correos masivos, cadenas de mensajería y carteleras físicas.
  2. *Hojas de vida no estandarizadas:* Formatos dispares que dificultan el filtrado y comparación ágil por parte de las empresas.
  3. *Incertidumbre estudiantil:* Cero visibilidad sobre el estado de las postulaciones (sin feedback ni trazabilidad).
  4. *Falta de analítica institucional:* La universidad carece de cifras consolidadas sobre tasas de vinculación efectiva, programas con mayor demanda y empresas activas.
- **Justificación:** Se requiere una solución centralizada, profesional y segura que conecte a estudiantes, empresas y administradores en un único ecosistema digital con datos persistentes y trazables.

---

### 📌 Diapositiva 3: Objetivos del Proyecto (Obligatorio)
**Orador Asignado:** Santiago Herrera Jimenez (Tiempo: ~0:45 min)
- **Objetivo General:**
  Diseñar y desarrollar una aplicación web Full Stack en Python que centralice la divulgación de ofertas laborales y de práctica, optimice la gestión de perfiles de talento y permita el seguimiento en tiempo real de los procesos de selección para la comunidad académica.
- **Objetivos Específicos:**
  1. Centralizar la publicación y consulta de ofertas con filtros avanzados (empresa, modalidad, tipo, área y ciudad).
  2. Estructurar perfiles con indicador dinámico de completitud y validación estricta de hojas de vida en PDF.
  3. Proporcionar trazabilidad bidireccional de postulaciones con notificaciones en app y correo.
  4. Generar reportes ejecutivos e indicadores clave exportables a Excel (.xlsx) y PDF (.pdf) para la toma de decisiones institucionales.

---

### 📌 Diapositiva 4: Arquitectura del Sistema Full Stack (Obligatorio)
**Orador Asignado:** Santiago Herrera Jimenez (Tiempo: ~1:15 min)
- **Explicación del Diagrama Técnico:**

```
                  ┌────────────────────────────────────────────────────────┐
                  │                 FRONTEND (Presentación)                │
                  │  HTML5 Semántico + Bootstrap 5.3 + CSS Minimalista     │
                  │  • Formularios validados en cliente (PDF, campos)      │
                  │  • Interacciones reactivas, modales y tabs dinámicos   │
                  └─────────────────────────┬──────────────────────────────┘
                                            │ HTTP / JSON / POST (CSRF Seguro)
                                            ▼
                  ┌────────────────────────────────────────────────────────┐
                  │                  BACKEND (Lógica & MVT)                │
                  │                 Python 3.x + Django 5/6                │
                  │  • Enrutador semántico RESTful (core/urls.py)          │
                  │  • Controladores y Vistas funcionales (core/views.py)  │
                  │  • Generadores: openpyxl (Excel) & reportlab (PDF)     │
                  │  • Sistema de Notificaciones & Correo en consola       │
                  └─────────────────────────┬──────────────────────────────┘
                                            │ ORM Relacional
                                            ▼
                  ┌────────────────────────────────────────────────────────┐
                  │           BASE DE DATOS RELACIONAL (MySQL/MariaDB)     │
                  │  Modelos con llaves primarias, foráneas e integridad:  │
                  │  User ── 1:1 ── StudentProfile / Company               │
                  │  Company ── 1:N ── Offer ── 1:N ── Application         │
                  │  Application ── 1:N ── StatusLog                       │
                  │  Area ── 1:N ── Offer / M:N ── StudentProfile          │
                  │  User ── 1:N ── Notification                           │
                  └────────────────────────────────────────────────────────┘
```

---

## PARTE 2: DEMOSTRACIÓN EN VIVO / LIVE DEMO (Máximo 7 minutos)

### 🎬 Cronograma de Navegación y Pruebas en Vivo:

#### Minuto 3:00 a 4:30 · Rol Estudiante (Navegación + Modificación de Datos)
**Orador:** Juan Santiago Blanco Herrera
1. **Inicio de Sesión:** Ingresar con `laura@uni.edu.co` / `estudiante12345`.
2. **Mi Perfil (HU02):**
   - Mostrar el porcentaje de completitud del perfil.
   - Demostrar la validación en tiempo real: subir un archivo que no sea PDF y mostrar el bloqueo.
   - Cargar un PDF válido y guardar: el porcentaje sube al 100%.
   - Configurar áreas de interés (HU12: Tecnología y Datos) y activar la casilla de alertas por correo.
3. **Exploración de Ofertas (HU03):**
   - Mostrar la pestaña "Recomendadas para ti" basada en sus intereses.
   - Usar el filtro por Empresa (seleccionar "Tecnova S.A.S.") y por tipo "Práctica".
4. **Postulación en Tiempo Real (HU04 - Persistencia):**
   - Entrar al detalle de la oferta «Práctica en desarrollo web Full Stack».
   - Hacer clic en «Postularme a esta convocatoria».
   - Mostrar la confirmación instantánea y redirigir a «Mis postulaciones» (HU05), donde se observa el estado «Enviada».

---

#### Minuto 4:30 a 5:45 · Rol Empresa (Gestión de Candidatos + Persistencia)
**Orador:** Jhonny Alexander Hernández Escudero
1. **Cambio de Usuario:** Salir y entrar con `rrhh@tecnova.co` / `empresa12345`.
2. **Mis Convocatorias (HU07):**
   - Mostrar la oferta donde Laura se acaba de postular: el contador de postulantes se actualizó dinámicamente.
3. **Gestión de Postulantes (HU08 & HU09):**
   - Entrar a «Ver postulantes».
   - Ver el perfil de Laura y su PDF cargado.
   - **Prueba de Modificación en tiempo real:**
     - Cambiar el estado de Laura de «Enviada» a «Preseleccionada».
     - Agregar nota interna: *"Candidata con excelentes competencias técnicas"*.
     - Marcar con la estrella de ★ Favorito.
4. **Comparación de Candidatos (HU09):**
   - Seleccionar a Carlos y Laura con las casillas de verificación.
   - Presionar «Comparar candidatos seleccionados» y mostrar la matriz comparativa de habilidades, semestre y nivel de inglés.
5. **Perfil de Empresa (HU06):**
   - Entrar a «Perfil empresa» y modificar la ciudad o teléfono corporativo, guardando los cambios.

---

#### Minuto 5:45 a 7:00 · Rol Administrador (Validaciones, CRUD y Reportes)
**Orador:** Sara Urzola y Santiago Herrera
1. **Inicio de Sesión Admin:** Entrar con `admin@ppol.co` / `admin12345`.
2. **Centro de Validaciones (HU10):**
   - Mostrar la empresa AgroSol en estado pendiente y la oferta pendiente.
   - Aprobar una oferta: el sistema dispara la notificación a los estudiantes afines (HU12).
3. **Gestión Integral de Usuarios (HU10 - CRUD Persistencia):**
   - Entrar a `/panel/usuarios/`.
   - Filtrar usuarios por rol o buscar por correo.
   - **Demostrar cambio de estado en tiempo real:** Suspender un usuario con el botón interactivo y volver a reactivarlo.
4. **Gestión de Áreas (HU10):**
   - Entrar a `/panel/areas/`, registrar una nueva área (ej. *Ciberseguridad Aplicada*) y demostrar que persiste.
5. **Indicadores y Reportes Institucionales (HU11):**
   - Mostrar los 4 KPIs principales (Ofertas, Empresas activas, Postulaciones, Vinculaciones).
   - Mostrar los gráficos/tablas de áreas y programas con mayor demanda.
   - **Demostrar Exportación en Vivo:**
     - Clic en **«Descargar Excel (.xlsx)»** y abrirlo (o mostrar la descarga del archivo estructurado con colores y tablas).
     - Clic en **«Descargar PDF (.pdf)»** y abrir el documento oficial con membrete de la Universidad Cooperativa de Colombia.

---

## 📋 Lista de Chequeo Final de la Sustentación (Rúbrica de Evaluación)

La siguiente tabla relaciona la rúbrica con evidencia que debe presentarse. No es una calificación anticipada: el equipo debe validar cada flujo durante el ensayo y la demostración.

| Criterio Evaluado | % | Evidencia / Estado | Justificación Técnica |
|---|:---:|:---:|---|
| **Cumplimiento técnico (Backend)** | 25% | Implementado; verificar en vivo | Django MVT, rutas, formularios, validaciones y lógica de acceso por rol. |
| **Desarrollo Frontend (Diseño + JS)** | 20% | Implementado; ensayar responsive | HTML semántico, CSS personalizado, Bootstrap, eventos y validación de formularios. |
| **Funcionalidad y Estabilidad** | 15% | 16 pruebas automatizadas | Ejecutar `python manage.py test --settings=ppol.test_settings` y ensayar flujos con la base del equipo. |
| **Uso del Framework** | 10% | Implementado | ORM, decoradores de autorización, context processors y vistas de autenticación de Django. |
| **Base de Datos** | 10% | XAMPP requerido para la demo | Modelo relacional con llaves, unicidad e integridad referencial. Iniciar MySQL y comprobar conexión antes de presentar. |
| **Documentación** | 10% | Documentada | README, dependencias, configuración de entorno y guía de sustentación. |
| **Creatividad e Integración** | 10% | Implementado; demostrar | Exportación CSV/XLSX/PDF, notificaciones y panel administrativo. |
