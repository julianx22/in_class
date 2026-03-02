from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django import forms


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    def clean(self):
        cleaned = super().clean()
        username = self.cleaned_data.get('username')
        if username and '@' in username:
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(email__iexact=username)
                self.cleaned_data['username'] = user.get_username()
            except UserModel.DoesNotExist:
                pass
        return cleaned


User = get_user_model()


class ProfileEditForm(forms.ModelForm):
    """
    Form para editar nombre, apellido y correo del usuario actual.
    Valida que el email no esté usado por otro usuario.
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "ui-input",
                "placeholder": "Nombre",
                "autocomplete": "given-name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "ui-input",
                "placeholder": "Apellido",
                "autocomplete": "family-name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "ui-input",
                "placeholder": "Correo",
                "autocomplete": "email",
            }),
        }

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            return email
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Este correo ya está en uso.")
        return email


class PublicRegistrationForm(UserCreationForm):
    """
    Formulario público de registro:
    - Crea un usuario de auth_user
    - Sin rol / programa / ficha (eso lo configura el admin después).
    """
    first_name = forms.CharField(
        label="Nombre",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "ui-input",
            "placeholder": "Nombre",
            "autocomplete": "given-name",
        }),
    )
    last_name = forms.CharField(
        label="Apellido",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "ui-input",
            "placeholder": "Apellido",
            "autocomplete": "family-name",
        }),
    )
    email = forms.EmailField(
        label="Correo electrónico",
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "ui-input",
            "placeholder": "Correo",
            "autocomplete": "email",
        }),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip()
        if not email:
            raise forms.ValidationError("El correo es obligatorio.")
        qs = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con este correo.")
        return email
