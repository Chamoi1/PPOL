import csv
from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AreaForm,
    CompanyProfileForm,
    CompanyRegisterForm,
    OfferForm,
    ProfileForm,
    StudentRegisterForm,
)
from .models import Application, Area, Company, Notification, Offer, StudentProfile, User
from .reports_export import generate_excel_report, generate_pdf_report

HOME = {"EST": "offers", "EMP": "company_offers", "ADM": "validations"}


def role_required(role):
    def deco(view):
        @wraps(view)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.effective_role != role:
                return HttpResponseForbidden("No tienes acceso a esta sección.")
            return view(request, *args, **kwargs)
        return wrapper
    return deco


def home(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return redirect(HOME[request.user.effective_role])


# ---------- Registro (HU01, HU06) ----------
def register(request, kind):
    if kind == "estudiante":
        Form = StudentRegisterForm
    elif kind == "empresa":
        Form = CompanyRegisterForm
    else:
        raise Http404("Tipo de registro no válido.")

    form = Form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        if kind == "estudiante":
            login(request, obj)
            messages.success(request, f"¡Bienvenido a PPOL, {obj.first_name}! Completa tu perfil para postularte.")
            return redirect("home")
        messages.success(request, "Registro recibido exitosamente. Tu cuenta empresarial podrá publicar cuando sea validada por el administrador.")
        return redirect("login")
    return render(request, "registration/register.html", {"form": form, "kind": kind})


# ---------- Estudiante (HU01, HU02, HU03, HU04, HU05, HU12) ----------
@role_required("EST")
def offers(request):
    qs = Offer.objects.filter(status="ACT", deadline__gte=timezone.localdate()).select_related("company", "area")
    g = request.GET
    tab = g.get("tab", "todas")

    student_profile = getattr(request.user, "student", None)

    # Pestaña "Para ti" basada en áreas de interés o programa (HU12)
    if tab == "recomendadas" and student_profile:
        interests = student_profile.interests.all()
        if interests.exists():
            qs = qs.filter(Q(area__in=interests) | Q(programs__icontains=student_profile.program))
        elif student_profile.program:
            qs = qs.filter(programs__icontains=student_profile.program)

    if g.get("q"):
        qs = qs.filter(
            Q(title__icontains=g["q"]) |
            Q(description__icontains=g["q"]) |
            Q(company__name__icontains=g["q"]) |
            Q(requirements__icontains=g["q"])
        )
    for field, param in (("kind", "kind"), ("mode", "mode"), ("area_id", "area"), ("company_id", "company")):
        if g.get(param):
            qs = qs.filter(**{field: g[param]})
    if g.get("city"):
        qs = qs.filter(city__icontains=g["city"])

    return render(request, "offers.html", {
        "offers": qs,
        "areas": Area.objects.all(),
        "companies": Company.objects.filter(status="APR").order_by("name"),
        "g": g,
        "tab": tab,
        "kinds": Offer.Kind.choices,
        "modes": Offer.Mode.choices,
    })


@role_required("EST")
def offer_detail(request, pk):
    offer = get_object_or_404(Offer, pk=pk, status__in=["ACT", "PAU", "CER"])
    existing = Application.objects.filter(student=request.user, offer=offer).first()
    if request.method == "POST":
        profile = request.user.student
        if not offer.is_open:
            messages.error(request, "Esta oferta ya no recibe postulaciones (cerrada o vencida).")
        elif not profile.cv:
            messages.error(request, "Debes adjuntar tu hoja de vida en PDF en tu perfil antes de postularte.")
            return redirect("profile")
        elif existing and existing.status != "RET":
            messages.error(request, "Ya te has postulado a esta convocatoria.")
        else:
            app = existing or Application(student=request.user, offer=offer)
            app.status = "ENV"
            app.save()
            app.set_status("ENV", notify=False)

            # Notificar a la empresa por email y notificación en la app (HU04 criterio 4)
            company_user = offer.company.user
            notif_msg = f"El estudiante {request.user.get_full_name() or request.user.email} se ha postulado a la oferta «{offer.title}»."
            Notification.objects.create(
                user=company_user,
                title="Nueva postulación recibida",
                message=notif_msg,
                link=f"/empresa/ofertas/{offer.pk}/postulantes/"
            )
            send_mail(
                f"Nueva postulación a «{offer.title}»",
                notif_msg,
                None,
                [company_user.email],
            )

            messages.success(request, f"¡Postulación enviada exitosamente! {offer.company.name} ha sido notificada.")
            return redirect("my_applications")
        return redirect("offer_detail", pk=pk)
    return render(request, "offer_detail.html", {"offer": offer, "existing": existing})


@role_required("EST")
def my_applications(request):
    apps = request.user.applications.select_related("offer__company", "offer__area").prefetch_related("log")
    return render(request, "my_applications.html", {"apps": apps})


@role_required("EST")
@require_POST
def withdraw(request, pk):
    app = get_object_or_404(Application, pk=pk, student=request.user)
    if request.method == "POST" and not app.is_final:
        app.set_status("RET", notify=False)
        messages.success(request, "Postulación retirada correctamente.")
    return redirect("my_applications")


@role_required("EST")
def profile(request):
    student_profile = request.user.student
    form = ProfileForm(request.POST or None, request.FILES or None, instance=student_profile)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado con éxito.")
            return redirect("profile")
    return render(request, "profile.html", {
        "form": form,
        "pct": student_profile.completeness,
        "areas": Area.objects.all(),
    })


# ---------- Empresa (HU06, HU07, HU08, HU09) ----------
def _company(request):
    return request.user.company


@role_required("EMP")
def company_offers(request):
    c = _company(request)
    return render(request, "company/offers.html", {
        "company": c,
        "offers": c.offers.annotate(n=Count("applications")),
    })


@role_required("EMP")
def company_profile(request):
    c = _company(request)
    form = CompanyProfileForm(request.POST or None, instance=c)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Perfil de la empresa actualizado correctamente.")
        return redirect("company_profile")
    return render(request, "company/profile.html", {"form": form, "company": c})


@role_required("EMP")
def offer_form(request, pk=None):
    c = _company(request)
    if c.status != "APR":
        messages.error(request, "Tu empresa aún no ha sido aprobada por el administrador.")
        return redirect("company_offers")
    offer = get_object_or_404(Offer, pk=pk, company=c) if pk else None
    form = OfferForm(request.POST or None, instance=offer)
    if request.method == "POST" and form.is_valid():
        o = form.save(commit=False)
        o.company = c
        o.status = "PEN"  # toda oferta nueva o editada pasa por revisión
        o.save()
        messages.success(request, "Oferta guardada y enviada a revisión. Será visible cuando el administrador la apruebe.")
        return redirect("company_offers")
    return render(request, "company/offer_form.html", {"form": form, "offer": offer})


@role_required("EMP")
@require_POST
def offer_status(request, pk, status):
    offer = get_object_or_404(Offer, pk=pk, company=_company(request))
    allowed = {"pausar": ("ACT", "PAU"), "reanudar": ("PAU", "ACT"), "cerrar": (None, "CER")}
    transition = allowed.get(status)
    if transition is None:
        messages.error(request, "La acción solicitada para la convocatoria no es válida.")
        return redirect("company_offers")

    src, dst = transition
    if src is None or offer.status == src:
        offer.status = dst
        offer.save(update_fields=["status"])
        messages.success(request, f"Convocatoria «{offer.title}» actualizada.")
    else:
        messages.error(request, "La convocatoria ya no se encuentra en un estado compatible con esa acción.")
    return redirect("company_offers")


@role_required("EMP")
def applicants(request, pk):
    offer = get_object_or_404(Offer, pk=pk, company=_company(request))
    if request.method == "POST":
        app = get_object_or_404(Application, pk=request.POST.get("app"), offer=offer)
        action = request.POST.get("action")
        if action == "status" and request.POST.get("status") in dict(Application.Status.choices):
            app.set_status(request.POST["status"])
            messages.success(request, f"Estado actualizado a «{app.get_status_display()}». El estudiante fue notificado.")
        elif action == "note":
            app.note = request.POST.get("note", "")[:250]
            app.save(update_fields=["note"])
            messages.success(request, "Nota interna guardada.")
        elif action == "fav":
            app.favorite = not app.favorite
            app.save(update_fields=["favorite"])
        return redirect(request.get_full_path())
    qs = offer.applications.exclude(status="RET").select_related("student__student", "student")
    g = request.GET
    if g.get("program"):
        qs = qs.filter(student__student__program__icontains=g["program"])
    if g.get("semester"):
        qs = qs.filter(student__student__semester=g["semester"])
    if g.get("skills"):
        qs = qs.filter(student__student__skills__icontains=g["skills"])
    if g.get("languages"):
        qs = qs.filter(student__student__languages__icontains=g["languages"])
    if g.get("fav"):
        qs = qs.filter(favorite=True)
    return render(request, "company/applicants.html", {
        "offer": offer, "apps": qs, "g": g, "statuses": Application.Status.choices,
    })


@role_required("EMP")
def compare(request, pk):
    offer = get_object_or_404(Offer, pk=pk, company=_company(request))
    apps = offer.applications.filter(pk__in=request.GET.getlist("ids")).select_related("student__student", "student")
    return render(request, "company/compare.html", {"offer": offer, "apps": apps})


# ---------- Administrador (HU10, HU11) ----------
@role_required("ADM")
def validations(request):
    if request.method == "POST":
        ok = request.POST.get("decision") == "ok"
        notes = request.POST.get("notes", "")[:250]
        if request.POST.get("kind") == "company":
            c = Company.objects.filter(pk=request.POST.get("id")).first()
            if not c:
                messages.warning(request, "La empresa seleccionada no se encontró en esta instancia o ya fue procesada.")
                return redirect("validations")
            c.status, c.review_notes = ("APR" if ok else "REJ"), notes
            c.save()
            action_label = "aprobada" if ok else "rechazada"
            # Notificar a la empresa
            Notification.objects.create(
                user=c.user,
                title=f"Empresa {action_label}",
                message=f"Tu registro empresarial ha sido {action_label}. {notes}",
                link="/empresa/ofertas/"
            )
            send_mail(
                f"Estado de tu registro en PPOL: {action_label.capitalize()}",
                f"Tu registro de empresa ha sido {action_label}.\nObservaciones: {notes or 'Ninguna'}",
                None, [c.user.email]
            )
            messages.success(request, f"Empresa «{c.name}» {action_label}.")
        else:
            o = Offer.objects.filter(pk=request.POST.get("id")).first()
            if not o:
                messages.warning(request, "La convocatoria seleccionada no se encontró en esta instancia o ya fue procesada.")
                return redirect("validations")
            o.status = "ACT" if ok else "REJ"
            o.save(update_fields=["status"])
            action_label = "aprobada y publicada" if ok else "rechazada"

            # Notificar a la empresa de la oferta
            Notification.objects.create(
                user=o.company.user,
                title=f"Oferta {action_label}",
                message=f"Tu convocatoria «{o.title}» fue {action_label}.",
                link="/empresa/ofertas/"
            )

            # HU12: Notificar por correo y app a estudiantes interesados en esta área
            if ok:
                interested_students = StudentProfile.objects.filter(
                    notify_new_offers=True
                ).filter(
                    Q(interests=o.area) | Q(program__icontains=o.programs)
                ).distinct()

                for stu in interested_students:
                    Notification.objects.create(
                        user=stu.user,
                        title=f"Nueva oferta afín: {o.title}",
                        message=f"{o.company.name} ha publicado una vacante de {o.get_kind_display()} en el área de {o.area.name}.",
                        link=f"/ofertas/{o.pk}/"
                    )
                    send_mail(
                        f"Nueva oferta afín en PPOL: {o.title}",
                        f"Hola {stu.user.first_name},\n\nSe ha publicado una nueva oferta de tu interés: «{o.title}» en {o.company.name} ({o.city}).\n\nRevisa los detalles en la plataforma.",
                        None,
                        [stu.user.email],
                    )

            messages.success(request, f"Convocatoria «{o.title}» {action_label}.")
        return redirect("validations")
    return render(request, "adm/validations.html", {
        "companies": Company.objects.filter(status="PEN"),
        "offers": Offer.objects.filter(status="PEN").select_related("company", "area"),
    })


@role_required("ADM")
def reports(request):
    g = request.GET
    offers_qs, apps_qs = Offer.objects.all(), Application.objects.all()
    filter_desc = []
    if g.get("desde"):
        offers_qs = offers_qs.filter(created__date__gte=g["desde"])
        apps_qs = apps_qs.filter(created__date__gte=g["desde"])
        filter_desc.append(f"Desde {g['desde']}")
    if g.get("hasta"):
        offers_qs = offers_qs.filter(created__date__lte=g["hasta"])
        apps_qs = apps_qs.filter(created__date__lte=g["hasta"])
        filter_desc.append(f"Hasta {g['hasta']}")
    if g.get("empresa"):
        offers_qs = offers_qs.filter(company_id=g["empresa"])
        apps_qs = apps_qs.filter(offer__company_id=g["empresa"])
        c_obj = Company.objects.filter(id=g["empresa"]).first()
        if c_obj:
            filter_desc.append(f"Empresa: {c_obj.name}")
    if g.get("tipo"):
        offers_qs = offers_qs.filter(kind=g["tipo"])
        apps_qs = apps_qs.filter(offer__kind=g["tipo"])
        filter_desc.append(f"Tipo: {dict(Offer.Kind.choices).get(g['tipo'], g['tipo'])}")
    if g.get("programa"):
        apps_qs = apps_qs.filter(student__student__program__icontains=g["programa"])
        filter_desc.append(f"Programa: {g['programa']}")

    data = {
        "ofertas": offers_qs.count(),
        "postulaciones": apps_qs.count(),
        "vinculaciones": apps_qs.filter(status="ACE").count(),
        "empresas_activas": offers_qs.values("company").distinct().count(),
    }
    top_areas = list(apps_qs.values("offer__area__name").annotate(n=Count("id")).order_by("-n")[:5])
    top_programs = list(apps_qs.values("student__student__program").annotate(n=Count("id")).order_by("-n")[:5])

    offers_list = offers_qs.select_related("company", "area").annotate(apps_count=Count("applications")).order_by("-created")
    active_company_ids = offers_qs.values_list("company_id", flat=True).distinct()
    active_companies = (
        Company.objects.filter(id__in=active_company_ids)
        .select_related("user")
        .prefetch_related("offers__area")
        .annotate(
            offers_count=Count("offers", distinct=True),
            apps_count=Count("offers__applications", distinct=True),
        )
    )
    apps_list = (
        apps_qs.select_related("student", "student__student", "offer", "offer__company", "offer__area")
        .prefetch_related("log")
        .order_by("-created")
    )
    placements_list = [a for a in apps_list if a.status == "ACE"]

    # Exportación a CSV
    if g.get("export") == "csv":
        r = HttpResponse(content_type="text/csv; charset=utf-8")
        r["Content-Disposition"] = 'attachment; filename="reporte_ppol.csv"'
        r.write("\ufeff")  # BOM para Excel
        w = csv.writer(r)
        w.writerows([["Indicador", "Valor"], *data.items(), [], ["Área", "Postulaciones"],
                     *[(a["offer__area__name"] or "Sin área", a["n"]) for a in top_areas], [], ["Programa", "Postulaciones"],
                     *[(p["student__student__program"] or "Sin programa", p["n"]) for p in top_programs]])
        return r

    # Exportación a Excel (.xlsx) nativo con formato profesional
    if g.get("export") == "xlsx":
        xlsx_bytes = generate_excel_report(data, top_areas, top_programs, offers_list, active_companies, apps_list, placements_list)
        response = HttpResponse(
            xlsx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="reporte_ejecutivo_ppol.xlsx"'
        return response

    # Exportación a PDF oficial institucional
    if g.get("export") == "pdf":
        pdf_bytes = generate_pdf_report(data, top_areas, top_programs, offers_list, placements_list, filter_summary=", ".join(filter_desc))
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="informe_institucional_ppol.pdf"'
        return response

    return render(request, "adm/reports.html", {
        "data": data, "top_areas": top_areas, "top_programs": top_programs, "g": g,
        "companies": Company.objects.filter(status="APR").order_by("name"), "kinds": Offer.Kind.choices,
        "offers_list": offers_list,
        "active_companies": active_companies,
        "apps_list": apps_list,
        "placements_list": placements_list,
    })


# ---------- Gestión Administrativa (HU10: Usuarios y Áreas) ----------
@role_required("ADM")
def admin_users(request):
    qs = User.objects.all().select_related("student", "company").order_by("-date_joined")
    g = request.GET
    if g.get("q"):
        query = g["q"]
        qs = qs.filter(Q(first_name__icontains=query) | Q(email__icontains=query))
    if g.get("role"):
        qs = qs.filter(role=g["role"])
    if g.get("status"):
        if g["status"] == "active":
            qs = qs.filter(is_active=True)
        elif g["status"] == "inactive":
            qs = qs.filter(is_active=False)

    return render(request, "adm/users.html", {
        "users_list": qs,
        "g": g,
        "roles": User.Role.choices,
    })


@role_required("ADM")
@require_POST
def admin_user_toggle(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u.is_superuser and request.user == u:
        messages.error(request, "No puedes suspender tu propia cuenta de superadministrador.")
    else:
        u.is_active = not u.is_active
        u.save(update_fields=["is_active"])
        status_text = "activado" if u.is_active else "suspendido"
        messages.success(request, f"Usuario {u.email} ha sido {status_text}.")
    return redirect("admin_users")


@role_required("ADM")
@require_POST
def admin_user_delete(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario actual.")
    else:
        email = u.email
        u.delete()
        messages.success(request, f"Usuario {email} eliminado exitosamente.")
    return redirect("admin_users")


@role_required("ADM")
def admin_areas(request):
    areas_qs = Area.objects.annotate(offers_count=Count("offer")).order_by("name")
    form = AreaForm(request.POST or None)
    if request.method == "POST" and "create_area" in request.POST:
        if form.is_valid():
            area = form.save()
            messages.success(request, f"Área «{area.name}» creada correctamente.")
            return redirect("admin_areas")
    return render(request, "adm/areas.html", {
        "areas": areas_qs,
        "form": form,
    })


@role_required("ADM")
@require_POST
def admin_area_edit(request, pk):
    area = get_object_or_404(Area, pk=pk)
    form = AreaForm(request.POST, instance=area)
    if form.is_valid():
        area = form.save()
        messages.success(request, f"Área actualizada a «{area.name}».")
    else:
        messages.error(request, "No se pudo actualizar el área. Revisa que el nombre no esté vacío ni duplicado.")
    return redirect("admin_areas")


@role_required("ADM")
@require_POST
def admin_area_delete(request, pk):
    area = get_object_or_404(Area, pk=pk)
    if area.offer_set.exists():
        messages.error(request, f"No se puede eliminar «{area.name}» porque tiene convocatorias vinculadas.")
    else:
        name = area.name
        area.delete()
        messages.success(request, f"Área «{name}» eliminada.")
    return redirect("admin_areas")


# ---------- Notificaciones en App ----------
@login_required
def notifications_list(request):
    qs = request.user.notifications.all()
    if request.method == "POST" and "mark_all_read" in request.POST:
        qs.filter(read=False).update(read=True)
        messages.success(request, "Todas las notificaciones fueron marcadas como leídas.")
        return redirect("notifications_list")
    return render(request, "notifications.html", {"notifications": qs})


@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.read = True
    notif.save(update_fields=["read"])
    if notif.link:
        return redirect(notif.link)
    return redirect("notifications_list")


# ---------- Manejo de Errores Personalizado ----------
def error_404_view(request, exception=None):
    return render(request, "404.html", status=404)


def error_500_view(request):
    return render(request, "500.html", status=500)


def error_403_view(request, exception=None):
    return render(request, "403.html", status=403)
