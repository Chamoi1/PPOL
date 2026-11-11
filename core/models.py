from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "EST", "Estudiante"
        COMPANY = "EMP", "Empresa"
        ADMIN = "ADM", "Administrador"

    role = models.CharField(max_length=3, choices=Role.choices, default=Role.STUDENT)
    email = models.EmailField(unique=True)

    @property
    def effective_role(self):
        return "ADM" if self.is_superuser else self.role


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student")
    code = models.CharField("Código estudiantil", max_length=20, unique=True)
    program = models.CharField("Programa académico", max_length=120)
    semester = models.PositiveSmallIntegerField("Semestre", default=1)
    phone = models.CharField("Teléfono / WhatsApp", max_length=20, blank=True)
    skills = models.CharField("Habilidades", max_length=250, blank=True)
    languages = models.CharField("Idiomas", max_length=120, blank=True)
    experience = models.TextField("Experiencia", blank=True)
    cv = models.FileField("Hoja de vida (PDF)", upload_to="cvs/", blank=True)
    interests = models.ManyToManyField("Area", blank=True, related_name="interested_students", verbose_name="Áreas de interés")
    notify_new_offers = models.BooleanField("Recibir notificaciones de nuevas ofertas afines", default=True)

    @property
    def completeness(self):
        fields = [self.user.first_name, self.program, self.skills, self.languages, self.experience, self.cv]
        return round(100 * sum(1 for f in fields if f) / len(fields))

    def __str__(self):
        return self.user.get_full_name() or self.user.email


class Company(models.Model):
    class Status(models.TextChoices):
        PENDING = "PEN", "Pendiente"
        APPROVED = "APR", "Aprobada"
        REJECTED = "REJ", "Rechazada"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    name = models.CharField("Razón social", max_length=150)
    nit = models.CharField("NIT", max_length=20, unique=True)
    sector = models.CharField(max_length=100)
    contact = models.CharField("Persona de contacto", max_length=120)
    phone = models.CharField("Teléfono de contacto", max_length=20, blank=True)
    website = models.URLField("Sitio web", blank=True)
    description = models.TextField("Descripción de la organización", blank=True)
    city = models.CharField("Ciudad sede", max_length=80, blank=True)
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING)
    review_notes = models.CharField("Observaciones del administrador", max_length=250, blank=True)

    class Meta:
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class Offer(models.Model):
    class Kind(models.TextChoices):
        INTERNSHIP = "PRA", "Práctica"
        JOB = "EMP", "Empleo"

    class Mode(models.TextChoices):
        ONSITE = "PRE", "Presencial"
        HYBRID = "HIB", "Híbrida"
        REMOTE = "REM", "Remota"

    class Status(models.TextChoices):
        PENDING = "PEN", "Pendiente de aprobación"
        ACTIVE = "ACT", "Activa"
        PAUSED = "PAU", "Pausada"
        CLOSED = "CER", "Cerrada"
        REJECTED = "REJ", "Rechazada"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="offers")
    title = models.CharField("Título", max_length=150)
    description = models.TextField("Descripción")
    kind = models.CharField("Tipo", max_length=3, choices=Kind.choices)
    mode = models.CharField("Modalidad", max_length=3, choices=Mode.choices)
    city = models.CharField("Ciudad", max_length=80)
    area = models.ForeignKey(Area, on_delete=models.PROTECT, verbose_name="Área")
    requirements = models.TextField("Requisitos")
    programs = models.CharField("Programas dirigidos", max_length=250)
    deadline = models.DateField("Fecha de cierre")
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    @property
    def is_open(self):
        return self.status == self.Status.ACTIVE and self.deadline >= timezone.localdate()

    def __str__(self):
        return self.title


class Application(models.Model):
    class Status(models.TextChoices):
        SENT = "ENV", "Enviada"
        REVIEW = "REV", "En revisión"
        SHORTLIST = "PRE", "Preseleccionada"
        INTERVIEW = "ENT", "Entrevista"
        ACCEPTED = "ACE", "Aceptada"
        REJECTED = "REC", "Rechazada"
        WITHDRAWN = "RET", "Retirada"

    FINAL = ("ACE", "REC", "RET")

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=3, choices=Status.choices, default=Status.SENT)
    note = models.CharField("Observación interna", max_length=250, blank=True)
    favorite = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "offer")
        ordering = ["-created"]

    @property
    def is_final(self):
        return self.status in self.FINAL

    def set_status(self, status, notify=True):
        self.status = status
        self.save(update_fields=["status"])
        StatusLog.objects.create(application=self, status=status)
        if notify:
            msg = f"Tu postulación a «{self.offer.title}» en {self.offer.company.name} cambió de estado a: {self.get_status_display()}."
            send_mail(
                f"Tu postulación a «{self.offer.title}» cambió de estado",
                msg,
                None, [self.student.email],
            )
            Notification.objects.create(
                user=self.student,
                title="Actualización de postulación",
                message=msg,
                link="/mis-postulaciones/",
            )


class StatusLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="log")
    status = models.CharField(max_length=3, choices=Application.Status.choices)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created"]


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField("Título", max_length=150)
    message = models.TextField("Mensaje")
    link = models.CharField("Enlace", max_length=255, blank=True)
    read = models.BooleanField("Leída", default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.user.email} - {self.title}"
