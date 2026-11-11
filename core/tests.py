from datetime import timedelta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from core.models import Application, Area, Company, Notification, Offer, StudentProfile, User


class PPOLCoreTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.area_tech = Area.objects.create(name="Tecnología")
        self.area_data = Area.objects.create(name="Datos")

        # Admin
        self.admin_user = User.objects.create_superuser(
            "admin@test.com", "admin@test.com", "pass12345", role="ADM", first_name="Admin Test"
        )

        # Empresa
        self.company_user = User.objects.create_user(
            "empresa@test.com", "empresa@test.com", "pass12345", role="EMP", first_name="Empresa Test"
        )
        self.company = Company.objects.create(
            user=self.company_user,
            name="Empresa Test S.A.S.",
            nit="800999000-1",
            sector="Tecnología",
            contact="Juan Pérez",
            status="APR"
        )

        # Estudiante
        self.student_user = User.objects.create_user(
            "estudiante@test.com", "estudiante@test.com", "pass12345", role="EST", first_name="Estudiante Test"
        )
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            code="20261001",
            program="Ingeniería de Sistemas",
            semester=8,
            skills="Python, Django, SQL",
            languages="Español, Inglés",
            experience="Desarrollo de proyectos académicos",
            notify_new_offers=True
        )

        # Oferta
        self.offer = Offer.objects.create(
            company=self.company,
            title="Desarrollador Junior",
            description="Apoyo en backend",
            kind="EMP",
            mode="REM",
            city="Remota",
            area=self.area_tech,
            requirements="Conocimientos de Python",
            programs="Ingeniería de Sistemas",
            deadline=timezone.localdate() + timedelta(days=30),
            status="ACT"
        )

    def test_legacy_login_url_redirects_to_login_page(self):
        response = self.client.get("/login/")
        self.assertRedirects(response, reverse("login"))

    # HU01: Registro y Login Estudiante
    def test_student_registration_and_login(self):
        resp = self.client.post(reverse("register", kwargs={"kind": "estudiante"}), {
            "name": "Nuevo Alumno",
            "email": "nuevo@test.com",
            "password": "password123",
            "code": "20269999",
            "program": "Ingeniería de Sistemas",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(email="nuevo@test.com").exists())
        self.assertTrue(StudentProfile.objects.filter(code="20269999").exists())

    # HU02: Perfil y Hoja de Vida PDF
    def test_student_profile_update_and_cv_validation(self):
        self.client.login(username="estudiante@test.com", password="pass12345")
        pdf_file = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 ...", content_type="application/pdf")
        resp = self.client.post(reverse("profile"), {
            "name": "Estudiante Actualizado",
            "phone": "3001234567",
            "program": "Ingeniería de Sistemas",
            "semester": 9,
            "skills": "Python, Django, AWS",
            "languages": "Inglés B2",
            "experience": "Pasantía en desarrollo",
            "cv": pdf_file,
            "notify_new_offers": True,
            "interests": [self.area_tech.id],
        })
        self.assertEqual(resp.status_code, 302)
        self.student_profile.refresh_from_db()
        self.student_user.refresh_from_db()
        self.assertEqual(self.student_user.first_name, "Estudiante Actualizado")
        self.assertEqual(self.student_profile.semester, 9)
        self.assertTrue(self.student_profile.cv)
        self.assertEqual(self.student_profile.completeness, 100)

    # HU03: Búsqueda y Filtrado de Ofertas (incluyendo filtro por empresa)
    def test_offers_filtering(self):
        self.client.login(username="estudiante@test.com", password="pass12345")
        # Filtrar por palabra clave
        resp = self.client.get(reverse("offers"), {"q": "Desarrollador"})
        self.assertContains(resp, "Desarrollador Junior")

        # Filtrar por empresa
        resp = self.client.get(reverse("offers"), {"company": self.company.id})
        self.assertContains(resp, "Empresa Test S.A.S.")

        # Filtrar por área
        resp = self.client.get(reverse("offers"), {"area": self.area_tech.id})
        self.assertContains(resp, "Desarrollador Junior")

    # HU04: Postulación a Oferta
    def test_application_to_offer(self):
        # Asignar CV primero
        self.student_profile.cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 sample", content_type="application/pdf")
        self.student_profile.save()

        self.client.login(username="estudiante@test.com", password="pass12345")
        resp = self.client.post(reverse("offer_detail", kwargs={"pk": self.offer.pk}))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Application.objects.filter(student=self.student_user, offer=self.offer).exists())

        # Validar que no permita postularse dos veces
        resp2 = self.client.post(reverse("offer_detail", kwargs={"pk": self.offer.pk}))
        self.assertEqual(resp2.status_code, 302)
        self.assertEqual(Application.objects.filter(student=self.student_user, offer=self.offer).count(), 1)

    # HU05: Retirar Postulación
    def test_withdraw_application(self):
        app = Application.objects.create(student=self.student_user, offer=self.offer, status="ENV")
        self.client.login(username="estudiante@test.com", password="pass12345")
        resp = self.client.post(reverse("withdraw", kwargs={"pk": app.pk}))
        self.assertEqual(resp.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, "RET")

    # HU06: Registro y Edición de Perfil de Empresa
    def test_company_registration_and_profile_edit(self):
        resp = self.client.post(reverse("register", kwargs={"kind": "empresa"}), {
            "name": "Nueva Empresa Corp",
            "nit": "900888777-2",
            "sector": "Finanzas",
            "contact": "Ana Gómez",
            "email": "contacto@nueva.com",
            "password": "password123",
        })
        self.assertEqual(resp.status_code, 302)
        comp = Company.objects.get(nit="900888777-2")
        self.assertEqual(comp.status, "PEN")

        # Edición de perfil de empresa aprobada
        self.client.login(username="empresa@test.com", password="pass12345")
        resp_edit = self.client.post(reverse("company_profile"), {
            "name": "Empresa Test Renovada",
            "sector": "Fintech",
            "contact": "Juan Pérez",
            "phone": "+57 300 000 1122",
            "city": "Montería",
            "website": "https://empresatest.com",
            "description": "Innovación en servicios financieros",
        })
        self.assertEqual(resp_edit.status_code, 302)
        self.company.refresh_from_db()
        self.assertEqual(self.company.name, "Empresa Test Renovada")
        self.assertEqual(self.company.city, "Montería")

    # HU07: Publicar y Gestionar Convocatorias
    def test_offer_creation_and_status_toggle(self):
        self.client.login(username="empresa@test.com", password="pass12345")
        # Pausar oferta activa
        resp_p = self.client.post(reverse("offer_status", kwargs={"pk": self.offer.pk, "status": "pausar"}))
        self.assertEqual(resp_p.status_code, 302)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "PAU")

        # Reanudar oferta
        resp_r = self.client.post(reverse("offer_status", kwargs={"pk": self.offer.pk, "status": "reanudar"}))
        self.assertEqual(resp_r.status_code, 302)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "ACT")

    # HU08 & HU09: Revisión de Postulantes, Cambiar Estado y Favoritos
    def test_applicants_management_and_favorites(self):
        app = Application.objects.create(student=self.student_user, offer=self.offer, status="ENV")
        self.client.login(username="empresa@test.com", password="pass12345")

        # Cambiar estado a Entrevista
        resp = self.client.post(reverse("applicants", kwargs={"pk": self.offer.pk}), {
            "app": app.pk,
            "action": "status",
            "status": "ENT"
        })
        self.assertEqual(resp.status_code, 302)
        app.refresh_from_db()
        self.assertEqual(app.status, "ENT")

        # Marcar favorito
        resp_fav = self.client.post(reverse("applicants", kwargs={"pk": self.offer.pk}), {
            "app": app.pk,
            "action": "fav",
        })
        self.assertEqual(resp_fav.status_code, 302)
        app.refresh_from_db()
        self.assertTrue(app.favorite)

    # HU10: Administrador - Gestión de Usuarios y Áreas
    def test_admin_user_management_and_areas(self):
        self.client.login(username="admin@test.com", password="pass12345")

        # Suspender usuario estudiante
        resp = self.client.post(reverse("admin_user_toggle", kwargs={"pk": self.student_user.pk}))
        self.assertEqual(resp.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertFalse(self.student_user.is_active)

        # Reactivar usuario
        resp2 = self.client.post(reverse("admin_user_toggle", kwargs={"pk": self.student_user.pk}))
        self.assertEqual(resp2.status_code, 302)
        self.student_user.refresh_from_db()
        self.assertTrue(self.student_user.is_active)

        # Crear nueva área
        resp_area = self.client.post(reverse("admin_areas"), {
            "create_area": "1",
            "name": "Inteligencia Artificial"
        })
        self.assertEqual(resp_area.status_code, 302)
        self.assertTrue(Area.objects.filter(name="Inteligencia Artificial").exists())

    def test_admin_user_delete_and_self_delete_protection(self):
        self.client.login(username="admin@test.com", password="pass12345")

        response = self.client.post(
            reverse("admin_user_delete", kwargs={"pk": self.student_user.pk})
        )
        self.assertRedirects(response, reverse("admin_users"))
        self.assertFalse(User.objects.filter(pk=self.student_user.pk).exists())
        self.assertFalse(StudentProfile.objects.filter(pk=self.student_profile.pk).exists())

        response = self.client.post(
            reverse("admin_user_delete", kwargs={"pk": self.admin_user.pk})
        )
        self.assertRedirects(response, reverse("admin_users"))
        self.assertTrue(User.objects.filter(pk=self.admin_user.pk).exists())

    def test_admin_area_edit_delete_and_duplicate_validation(self):
        self.client.login(username="admin@test.com", password="pass12345")
        edit_url = reverse("admin_area_edit", kwargs={"pk": self.area_data.pk})

        response = self.client.post(edit_url, {"name": "Ciencia de Datos"})
        self.assertRedirects(response, reverse("admin_areas"))
        self.area_data.refresh_from_db()
        self.assertEqual(self.area_data.name, "Ciencia de Datos")

        response = self.client.post(edit_url, {"name": self.area_tech.name})
        self.assertRedirects(response, reverse("admin_areas"))
        self.area_data.refresh_from_db()
        self.assertEqual(self.area_data.name, "Ciencia de Datos")

        response = self.client.post(
            reverse("admin_area_delete", kwargs={"pk": self.area_tech.pk})
        )
        self.assertRedirects(response, reverse("admin_areas"))
        self.assertTrue(Area.objects.filter(pk=self.area_tech.pk).exists())

        response = self.client.post(
            reverse("admin_area_delete", kwargs={"pk": self.area_data.pk})
        )
        self.assertRedirects(response, reverse("admin_areas"))
        self.assertFalse(Area.objects.filter(pk=self.area_data.pk).exists())

    def test_company_offer_actions_reject_invalid_actions_and_get_requests(self):
        self.client.login(username="empresa@test.com", password="pass12345")
        offer_url = reverse(
            "offer_status", kwargs={"pk": self.offer.pk, "status": "invalid"}
        )

        response = self.client.post(offer_url)
        self.assertRedirects(response, reverse("company_offers"))
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "ACT")

        response = self.client.get(
            reverse(
                "offer_status", kwargs={"pk": self.offer.pk, "status": "pausar"}
            )
        )
        self.assertEqual(response.status_code, 405)
        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "ACT")

    def test_notification_read_requires_post_and_is_user_scoped(self):
        notification = Notification.objects.create(
            user=self.student_user,
            title="Prueba",
            message="Notificación de prueba.",
            link=reverse("offers"),
        )
        self.client.login(username="estudiante@test.com", password="pass12345")
        notification_url = reverse(
            "mark_notification_read", kwargs={"pk": notification.pk}
        )

        response = self.client.get(notification_url)
        self.assertEqual(response.status_code, 405)
        notification.refresh_from_db()
        self.assertFalse(notification.read)

        response = self.client.post(notification_url)
        self.assertRedirects(response, reverse("offers"))
        notification.refresh_from_db()
        self.assertTrue(notification.read)

        self.client.login(username="empresa@test.com", password="pass12345")
        response = self.client.post(notification_url)
        self.assertEqual(response.status_code, 404)

    def test_registration_rejects_unknown_account_types(self):
        response = self.client.get(reverse("register", kwargs={"kind": "other"}))
        self.assertEqual(response.status_code, 404)

    # HU11: Reportes - Exportación a CSV, Excel (.xlsx) y PDF (.pdf)
    def test_reports_exports(self):
        self.client.login(username="admin@test.com", password="pass12345")

        # CSV
        resp_csv = self.client.get(reverse("reports"), {"export": "csv"})
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv["Content-Type"], "text/csv; charset=utf-8")

        # Excel
        resp_xlsx = self.client.get(reverse("reports"), {"export": "xlsx"})
        self.assertEqual(resp_xlsx.status_code, 200)
        self.assertEqual(resp_xlsx["Content-Type"], "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertTrue(len(resp_xlsx.content) > 0)

        # PDF
        resp_pdf = self.client.get(reverse("reports"), {"export": "pdf"})
        self.assertEqual(resp_pdf.status_code, 200)
        self.assertEqual(resp_pdf["Content-Type"], "application/pdf")
        self.assertTrue(len(resp_pdf.content) > 0)

    # HU12: Notificaciones automáticas de ofertas afines
    def test_interest_notification_on_offer_approval(self):
        # Estudiante con interés en Finanzas
        area_fin = Area.objects.create(name="Finanzas")
        self.student_profile.interests.add(area_fin)
        self.student_profile.notify_new_offers = True
        self.student_profile.save()

        # Oferta pendiente en Finanzas
        pending_offer = Offer.objects.create(
            company=self.company,
            title="Auxiliar Contable y Financiero",
            description="Revisión de estados financieros",
            kind="PRA",
            mode="PRE",
            city="Montería",
            area=area_fin,
            requirements="Conocimientos contables",
            programs="Contaduría, Administración",
            deadline=timezone.localdate() + timedelta(days=20),
            status="PEN"
        )

        # Admin aprueba la oferta
        self.client.login(username="admin@test.com", password="pass12345")
        resp = self.client.post(reverse("validations"), {
            "kind": "offer",
            "id": pending_offer.pk,
            "decision": "ok"
        })
        self.assertEqual(resp.status_code, 302)
        pending_offer.refresh_from_db()
        self.assertEqual(pending_offer.status, "ACT")

        # Validar que se generó la notificación al estudiante
        self.assertTrue(
            Notification.objects.filter(
                user=self.student_user,
                title__icontains="Nueva oferta afín"
            ).exists()
        )
