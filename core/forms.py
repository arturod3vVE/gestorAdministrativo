from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import Socio, ConceptoCobro

# --- FORMULARIO DE CONCEPTOS (NUEVO) ---
class ConceptoForm(forms.ModelForm):
    class Meta:
        model = ConceptoCobro
        fields = ['nombre', 'monto_sugerido', 'monto_chofer']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Ej. Mensualidad'}),
            'monto_sugerido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'monto_chofer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class RegistroSocioForm(forms.ModelForm):
    # Campos de Usuario
    username = forms.CharField(label="Usuario", widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_username'}))
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password'}))
    confirm_password = forms.CharField(label="Confirmar", widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_confirm_password'}))
    
    # Identificación
    nacionalidad = forms.ChoiceField(choices=[('V','V'),('J','J'),('E','E'),('P','P')], widget=forms.Select(attrs={'class': 'form-select'}))
    cedula_numero = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'type': 'number', 'id': 'id_cedula_num'
    }))
    
    # Teléfono
    prefijo_tlf = forms.ChoiceField(
        choices=[('0414','0414'),('0424','0424'),('0412','0412'),('0416','0416'),('0426','0426')], 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cuerpo_tlf = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'type': 'number', 'id': 'id_cuerpo_tlf'
    }))

    class Meta:
        model = Socio
        fields = ['nombre', 'unidad', 'tiene_avance', 'nombre_avance']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_unidad'}),
            'tiene_avance': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'checkAvance'}),
            'nombre_avance': forms.TextInput(attrs={'class': 'form-control', 'id': 'inputAvance'}),
        }

    def clean_cedula_numero(self):
        val = self.cleaned_data.get('cedula_numero')
        if len(val) > 9:
            raise forms.ValidationError("La cédula no puede exceder los 9 dígitos.")
        return val

    def clean_cuerpo_tlf(self):
        val = self.cleaned_data.get('cuerpo_tlf')
        if len(val) != 7:
            raise forms.ValidationError("El número debe tener exactamente 7 dígitos.")
        return val

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("password") != cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned_data

# --- FORMULARIO DE EDICIÓN DE SOCIO ---
class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nombre', 'cedula', 'telefono', 'unidad', 'tiene_avance', 'nombre_avance', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'tiene_avance': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'checkAvance'}),
            'nombre_avance': forms.TextInput(attrs={'class': 'form-control', 'id': 'inputAvance'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

from django import forms
from .models import Socio

class SocioEditForm(forms.ModelForm):
    # Prefijos con ancho justo para no quitar espacio al número
    nacionalidad = forms.ChoiceField(
        choices=[('V','V'),('J','J'),('E','E'),('P','P')], 
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'width: 75px; flex: none;'})
    )
    cedula_numero = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'id': 'id_cedula_num'})
    )
    
    prefijo_tlf = forms.ChoiceField(
        choices=[('0414','0414'),('0424','0424'),('0412','0412'),('0416','0416'),('0426','0426')], 
        widget=forms.Select(attrs={'class': 'form-select', 'style': 'width: 110px; flex: none;'})
    )
    cuerpo_tlf = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'number', 'id': 'id_cuerpo_tlf'})
    )

    class Meta:
        model = Socio
        fields = ['nombre', 'unidad', 'tiene_avance', 'nombre_avance', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'unidad': forms.TextInput(attrs={'class': 'form-control'}),
            'tiene_avance': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'checkAvance'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_activo'}),
            'nombre_avance': forms.TextInput(attrs={'class': 'form-control', 'id': 'inputAvance'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.cedula:
            self.fields['nacionalidad'].initial = self.instance.cedula[0]
            self.fields['cedula_numero'].initial = self.instance.cedula[1:].lstrip('0')
        if self.instance and self.instance.telefono:
            num = self.instance.telefono
            if num.startswith('58'):
                self.fields['prefijo_tlf'].initial = '0' + num[2:5]
                self.fields['cuerpo_tlf'].initial = num[5:]

class ConfigTelefonoForm(forms.ModelForm):
    prefijo_tlf = forms.ChoiceField(
        choices=[('0414','0414'),('0424','0424'),('0412','0412'),('0416','0416'),('0426','0426')], 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cuerpo_tlf = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'inputmode': 'numeric', 'id': 'id_cuerpo_tlf', 'placeholder': '7 dígitos'
    }))

    class Meta:
        model = Socio
        fields = [] # No editamos campos directos del modelo aquí, solo el teléfono compuesto

    def clean_cuerpo_tlf(self):
        val = self.cleaned_data.get('cuerpo_tlf')
        if len(val) != 7:
            raise forms.ValidationError("El número debe tener exactamente 7 dígitos.")
        return val