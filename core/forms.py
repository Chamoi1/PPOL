from django import forms
from .models import Area, Company, Offer, StudentProfile, User


class _RegisterBase(forms.Form):
    email = forms.EmailField(label="Correo")
    password = forms.CharField(label="Contraseña", min_length=8, widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return email


class StudentRegisterForm(_RegisterBase):
    name = forms.CharField(label="Nombre completo", max_length=150)
    code = forms.CharField(label="Código estudiantil", max_length=20)
    program = forms.CharField(label="Programa académico", max_length=120)
    phone = forms.CharField(label="Teléfono / WhatsApp", max_length=20, required=False)

    def clean_code(self):
        if StudentProfile.objects.filter(code=self.cleaned_data["code"]).exists():
            raise forms.ValidationError("Este código ya está registrado.")
        return self.cleaned_data["code"]

    def save(self):
        d = self.cleaned_data
        user = User.objects.create_user(d["email"], d["email"], d["password"], first_name=d["name"], role="EST")
        StudentProfile.objects.create(
            user=user,
            code=d["code"],
            program=d["program"],
            phone=d.get("phone", ""),
        )
        return user


class CompanyRegisterForm(_RegisterBase):
    name = forms.CharField(label="Razón social", max_length=150)
    nit = forms.CharField(label="NIT", max_length=20)
    sector = forms.CharField(max_length=100)
    contact = forms.CharField(label="Persona de contacto", max_length=120)
    phone = forms.CharField(label="Teléfono corporativo", max_length=20, required=False)
    city = forms.CharField(label="Ciudad sede", max_length=80, required=False)

    def clean_nit(self):
        if Company.objects.filter(nit=self.cleaned_data["nit"]).exists():
            raise forms.ValidationError("Este NIT ya está registrado.")
        return self.cleaned_data["nit"]

    def save(self):
        d = self.cleaned_data
        user = User.objects.create_user(d["email"], d["email"], d["password"], first_name=d["name"], role="EMP")
        return Company.objects.create(
            user=user,
            name=d["name"],
            nit=d["nit"],
            sector=d["sector"],
            contact=d["contact"],
            phone=d.get("phone", ""),
            city=d.get("city", ""),
        )


class ProfileForm(forms.ModelForm):
    name = forms.CharField(label="Nombre completo", max_length=150)

    class Meta:
        model = StudentProfile
        fields = [
            "program", "semester", "phone", "skills", "languages",
            "experience", "cv", "interests", "notify_new_offers"
        ]
        widgets = {
            "experience": forms.Textarea(attrs={"rows": 3}),
            "interests": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields["name"].initial = self.instance.user.first_name

    def clean_cv(self):
        cv = self.cleaned_data.get("cv")
        if cv and hasattr(cv, "name") and not cv.name.lower().endswith(".pdf"):
            raise forms.ValidationError("La hoja de vida debe ser un archivo PDF.")
        return cv

    def save(self, commit=True):
        profile = super().save(commit=commit)
        name = self.cleaned_data.get("name")
        if name and profile.user.first_name != name:
            profile.user.first_name = name
            profile.user.save(update_fields=["first_name"])
        return profile


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "sector", "contact", "phone", "city", "website", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ["name"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Nombre del área o categoría..."}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["title", "description", "kind", "mode", "city", "area", "requirements", "programs", "deadline"]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "description": forms.Textarea(attrs={"rows": 3}),
            "requirements": forms.Textarea(attrs={"rows": 3}),
        }
