from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Application, Area, Company, Notification, Offer, StudentProfile, User


class Command(BaseCommand):
    help = "Carga o actualiza datos de ejemplo para probar la plataforma PPOL al 100%."

    def handle(self, *args, **opts):
        # 1. Áreas profesionales
        area_names = ["Tecnología", "Datos", "Finanzas", "Mercadeo", "Ciberseguridad", "Redes"]
        areas = {}
        for name in area_names:
            areas[name], _ = Area.objects.get_or_create(name=name)

        # 2. Administrador
        admin_user, _ = User.objects.get_or_create(
            email="admin@ppol.co",
            defaults={"username": "admin@ppol.co", "role": "ADM", "first_name": "Coordinador UCC", "is_superuser": True, "is_staff": True}
        )
        admin_user.set_password("admin12345")
        admin_user.save()

        # 3. Empresa Aprobada (Tecnova)
        tec_user, _ = User.objects.get_or_create(
            email="rrhh@tecnova.co",
            defaults={"username": "rrhh@tecnova.co", "role": "EMP", "first_name": "Tecnova Solutions"}
        )
        tec_user.set_password("empresa12345")
        tec_user.save()

        co, _ = Company.objects.get_or_create(
            user=tec_user,
            defaults={
                "name": "Tecnova S.A.S.",
                "nit": "900123456-7",
                "sector": "Tecnología",
                "contact": "Marta Ruiz",
                "phone": "+57 300 456 7890",
                "city": "Montería",
                "status": "APR",
                "description": "Empresa especializada en soluciones de software en la nube y consultoría tecnológica.",
            }
        )
        if co.status != "APR":
            co.status = "APR"
            co.save()

        # 4. Empresa Pendiente de Validación (AgroSol)
        agro_user, _ = User.objects.get_or_create(
            email="talento@agrosol.co",
            defaults={"username": "talento@agrosol.co", "role": "EMP", "first_name": "AgroSol del Sinú"}
        )
        agro_user.set_password("empresa12345")
        agro_user.save()

        Company.objects.get_or_create(
            user=agro_user,
            defaults={
                "name": "AgroSol Ltda.",
                "nit": "901114882-5",
                "sector": "Agroindustria",
                "contact": "Luis Gil",
                "phone": "+57 311 987 6543",
                "city": "Cereté - Córdoba",
                "status": "PEN",
                "description": "Líderes en biotecnología agrícola y procesamiento sostenible de cultivos.",
            }
        )

        # 5. Estudiantes
        def get_or_create_student(email, name, code, prog, sem, skills, langs, phone=""):
            u, _ = User.objects.get_or_create(
                email=email,
                defaults={"username": email, "first_name": name, "role": "EST"}
            )
            u.first_name = name
            u.set_password("estudiante12345")
            u.save()

            sp, _ = StudentProfile.objects.get_or_create(
                user=u,
                defaults={
                    "code": code,
                    "program": prog,
                    "semester": sem,
                    "skills": skills,
                    "languages": langs,
                    "phone": phone,
                    "notify_new_offers": True,
                }
            )
            return sp

        laura = get_or_create_student("laura@uni.edu.co", "Laura Pérez", "2021105", "Ingeniería de Sistemas", 8, "Python, Django, PostgreSQL, Git", "Inglés B2", "+57 310 111 2233")
        laura.interests.add(areas["Tecnología"], areas["Datos"])

        carlos = get_or_create_student("carlos@uni.edu.co", "Carlos Mejía", "2020088", "Ingeniería de Sistemas", 9, "React, Node, SQL, Docker", "Inglés B1", "+57 320 444 5566")
        carlos.interests.add(areas["Tecnología"], areas["Ciberseguridad"])

        sara = get_or_create_student("sara@uni.edu.co", "Sara Urzola", "2022019", "Ingeniería de Sistemas", 7, "Machine Learning, Python, Power BI", "Inglés C1", "+57 301 777 8899")
        sara.interests.add(areas["Datos"], areas["Tecnología"])

        # 6. Ofertas
        today = timezone.localdate()
        specs = [
            ("Práctica en desarrollo web Full Stack", "PRA", "HIB", "Montería", "Tecnología", "ACT", 40, "Estudiantes de 7mo semestre en adelante con bases en Python o JavaScript."),
            ("Analista de datos e inteligencia de negocios", "EMP", "PRE", "Montería", "Datos", "ACT", 50, "Manejo de SQL, Python o Power BI. Capacidad de análisis."),
            ("Ingeniero de soporte técnico cloud", "EMP", "REM", "Remota", "Tecnología", "ACT", 25, "Conocimientos en Linux, redes y resolución de incidencias."),
            ("Asistente de seguridad informática", "PRA", "REM", "Remota", "Ciberseguridad", "ACT", 30, "Interés en auditorías de sistemas y hardening de servidores."),
            ("Pasantía en mercadeo y analítica digital", "PRA", "HIB", "Montería", "Mercadeo", "PEN", 35, "Creatividad y afinidad con métricas de plataformas."),
        ]
        created_offers = []
        for t, k, m, c, a, s, d, req in specs:
            off, _ = Offer.objects.get_or_create(
                company=co,
                title=t,
                defaults={
                    "description": f"Oportunidad académica y profesional para vincularse al equipo de {co.name} durante el semestre formativo.",
                    "kind": k,
                    "mode": m,
                    "city": c,
                    "area": areas[a],
                    "requirements": req,
                    "programs": "Ingeniería de Sistemas, Administración",
                    "deadline": today + timedelta(days=d),
                    "status": s,
                }
            )
            created_offers.append(off)

        # 7. Postulaciones y trazabilidad (HU05, HU08, HU11)
        if created_offers:
            # Postulación de Carlos (Preseleccionado)
            app1, _ = Application.objects.get_or_create(student=carlos.user, offer=created_offers[0])
            app1.status = "PRE"
            app1.note = "Buen perfil técnico. Programar prueba técnica."
            app1.favorite = True
            app1.save()

            # Postulación de Sara (Aceptada / Vinculada para reportes)
            app2, _ = Application.objects.get_or_create(student=sara.user, offer=created_offers[1])
            app2.status = "ACE"
            app2.note = "Excelente desempeño en la entrevista con la gerencia."
            app2.favorite = True
            app2.save()

        # 8. Notificaciones de ejemplo (HU12)
        Notification.objects.get_or_create(
            user=laura.user,
            title="¡Bienvenida a PPOL!",
            defaults={"message": "Recuerda completar tu hoja de vida en PDF para postularte a las convocatorias de prácticas.", "link": "/perfil/"}
        )
        Notification.objects.get_or_create(
            user=carlos.user,
            title="Postulación preseleccionada",
            defaults={"message": "Tecnova S.A.S. ha preseleccionado tu postulación para «Práctica en desarrollo web Full Stack».", "link": "/mis-postulaciones/"}
        )

        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("✓ DATOS DE EJEMPLO CARGADOS CON ÉXITO"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write("Credenciales de acceso:")
        self.stdout.write("  • Administrador : admin@ppol.co     / admin12345")
        self.stdout.write("  • Empresa       : rrhh@tecnova.co   / empresa12345")
        self.stdout.write("  • Estudiante 1  : carlos@uni.edu.co / estudiante12345 (Perfil completo)")
        self.stdout.write("  • Estudiante 2  : laura@uni.edu.co  / estudiante12345 (Para subir CV)")
        self.stdout.write("  • Estudiante 3  : sara@uni.edu.co   / estudiante12345 (Vinculada)")
        self.stdout.write(self.style.SUCCESS("=" * 60))
