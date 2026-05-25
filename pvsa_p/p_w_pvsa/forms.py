from django.forms import ModelForm, formset_factory
from django import forms
from .models import (
    Sector,
    Ubicacion,
    Piso,
    Lugar,
    TipoLugar,
    TipoObjeto,
    CategoriaObjeto,
    ObjetoLugar,
    Objeto,
    HistoricoObjeto,
)

# -------------------
# CREAR
# -------------------


class CrearSector(ModelForm):
    class Meta:
        model = Sector
        fields = ["sector"]
        widgets = {
            "sector": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: Patio Norte"})
        }


class CrearUbicacion(ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["ubicacion", "sector"]


class CrearPiso(ModelForm):
    class Meta:
        model = Piso
        fields = ["piso", "ubicacion"]


class CrearLugar(ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre_del_lugar", "piso", "lugar_tipo_lugar"]


class CrearObjetoLugar(forms.ModelForm):
    class Meta:
        model = ObjetoLugar
        fields = [
            "tipo_de_objeto",
            "cantidad",
            "detalle",
            "importancia",
            "cantidad_mala",
            "cantidad_pendiente",
            "minimo_operativo",
        ]

        widgets = {
            "tipo_de_objeto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "detalle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Detalle u observación opcional",
                }
            ),
            "importancia": forms.Select(attrs={"class": "form-select"}),
            "cantidad_mala": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "cantidad_pendiente": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "minimo_operativo": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

        labels = {
            "tipo_de_objeto": "Tipo de objeto",
            "cantidad": "Cantidad total",
            "detalle": "Detalle",
            "importancia": "Importancia",
            "cantidad_mala": "Unidades malas",
            "cantidad_pendiente": "Unidades pendientes",
            "minimo_operativo": "Mínimo operativo",
        }

        help_texts = {
            "cantidad": "Cantidad total de unidades existentes.",
            "cantidad_mala": "Cantidad de unidades que no están funcionando.",
            "cantidad_pendiente": "Cantidad de unidades pendientes de revisión.",
            "minimo_operativo": "Cantidad mínima que debe estar funcionando para considerar aceptable este objeto.",
            "importancia": "Nivel de peso del objeto dentro del lugar.",
        }

    def clean(self):
        cleaned = super().clean()

        cantidad = cleaned.get("cantidad") or 0
        cantidad_mala = cleaned.get("cantidad_mala") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente") or 0
        minimo_operativo = cleaned.get("minimo_operativo") or 1

        if cantidad <= 0:
            raise forms.ValidationError("La cantidad total debe ser mayor a 0.")

        if cantidad_mala < 0:
            raise forms.ValidationError("Las unidades malas no pueden ser negativas.")

        if cantidad_pendiente < 0:
            raise forms.ValidationError("Las unidades pendientes no pueden ser negativas.")

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise forms.ValidationError(
                "La suma de unidades malas y pendientes no puede superar la cantidad total."
            )

        if minimo_operativo <= 0:
            raise forms.ValidationError("El mínimo operativo debe ser mayor a 0.")

        if minimo_operativo > cantidad:
            raise forms.ValidationError(
                "El mínimo operativo no puede ser mayor que la cantidad total."
            )

        return cleaned


class CrearTipoLugar(ModelForm):
    class Meta:
        model = TipoLugar
        fields = ["tipo_de_lugar"]


class CrearCategoriaObjeto(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_categoria"]


class CrearObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "objeto_categoria"]


class CrearTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]

class CrearHistorico(forms.ModelForm):
    fecha_anterior = forms.DateField(
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "class": "form-control",
                "placeholder": "dd/mm/aaaa",
            },
        ),
    )

    importancia_anterior = forms.TypedChoiceField(
        label="Importancia anterior",
        required=True,
        coerce=int,
        choices=(
            (1, "Baja"),
            (2, "Media"),
            (3, "Alta / Crítica"),
        ),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = HistoricoObjeto
        fields = [
            "objeto_del_lugar",
            "cantidad_anterior",
            "cantidad_mala_anterior",
            "cantidad_pendiente_anterior",
            "minimo_operativo_anterior",
            "importancia_anterior",
            "estado_anterior",
            "detalle_anterior",
            "fecha_anterior",
        ]

        widgets = {
            "objeto_del_lugar": forms.Select(attrs={"class": "form-select"}),
            "cantidad_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "cantidad_mala_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "cantidad_pendiente_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "minimo_operativo_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "estado_anterior": forms.Select(attrs={"class": "form-select"}),
            "detalle_anterior": forms.TextInput(attrs={"class": "form-control"}),
        }

        labels = {
            "objeto_del_lugar": "Objeto del lugar",
            "cantidad_anterior": "Cantidad total anterior",
            "cantidad_mala_anterior": "Cantidad mala anterior",
            "cantidad_pendiente_anterior": "Cantidad pendiente anterior",
            "minimo_operativo_anterior": "Mínimo operativo anterior",
            "estado_anterior": "Condición anterior",
            "detalle_anterior": "Detalle anterior",
            "fecha_anterior": "Fecha anterior",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.initial.get("objeto_del_lugar") or getattr(self.instance, "objeto_del_lugar_id", None):
            self.fields["objeto_del_lugar"].disabled = True

    def clean(self):
        cleaned = super().clean()

        cantidad = cleaned.get("cantidad_anterior") or 0
        cantidad_mala = cleaned.get("cantidad_mala_anterior") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente_anterior") or 0
        minimo_operativo = cleaned.get("minimo_operativo_anterior") or 1

        if cantidad <= 0:
            raise forms.ValidationError("La cantidad total anterior debe ser mayor a 0.")

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise forms.ValidationError(
                "La suma de cantidad mala anterior y cantidad pendiente anterior no puede superar la cantidad total anterior."
            )

        if minimo_operativo > cantidad:
            raise forms.ValidationError(
                "El mínimo operativo anterior no puede ser mayor que la cantidad total anterior."
            )

        return cleaned


# -------------------
# EDITAR
# -------------------


class EditarSector(ModelForm):
    class Meta:
        model = Sector
        fields = ["sector"]
        widgets = {
            "sector": forms.TextInput(attrs={"class": "form-control"})
        }


class EditarUbicacion(ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["ubicacion"]


class EditarPiso(ModelForm):
    class Meta:
        model = Piso
        fields = ["piso"]


class EditarTipoLugar(ModelForm):
    class Meta:
        model = TipoLugar
        fields = ["tipo_de_lugar"]


class EditarLugar(ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre_del_lugar", "piso", "lugar_tipo_lugar"]


class EditarCategoria(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_categoria"]


class EditarObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "objeto_categoria"]


class EditarTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]


class EditarObjetoLugar(forms.ModelForm):
    class Meta:
        model = ObjetoLugar
        fields = [
            "tipo_de_objeto",
            "cantidad",
            "detalle",
            "importancia",
            "cantidad_mala",
            "cantidad_pendiente",
            "minimo_operativo",
        ]

        widgets = {
            "tipo_de_objeto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "detalle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Detalle u observación opcional",
                }
            ),
            "importancia": forms.Select(attrs={"class": "form-select"}),
            "cantidad_mala": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "cantidad_pendiente": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "minimo_operativo": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        }

        labels = {
            "tipo_de_objeto": "Tipo de objeto",
            "cantidad": "Cantidad total",
            "detalle": "Detalle",
            "importancia": "Importancia",
            "cantidad_mala": "Unidades malas",
            "cantidad_pendiente": "Unidades pendientes",
            "minimo_operativo": "Mínimo operativo",
        }

        help_texts = {
            "cantidad": "Cantidad total de unidades existentes.",
            "cantidad_mala": "Cantidad de unidades que no están funcionando.",
            "cantidad_pendiente": "Cantidad de unidades pendientes de revisión.",
            "minimo_operativo": "Cantidad mínima que debe estar funcionando para considerar aceptable este objeto.",
            "importancia": "Nivel de peso del objeto dentro del lugar.",
        }

    def clean(self):
        cleaned = super().clean()

        cantidad = cleaned.get("cantidad") or 0
        cantidad_mala = cleaned.get("cantidad_mala") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente") or 0
        minimo_operativo = cleaned.get("minimo_operativo") or 1

        if cantidad <= 0:
            raise forms.ValidationError("La cantidad total debe ser mayor a 0.")

        if cantidad_mala < 0:
            raise forms.ValidationError("Las unidades malas no pueden ser negativas.")

        if cantidad_pendiente < 0:
            raise forms.ValidationError("Las unidades pendientes no pueden ser negativas.")

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise forms.ValidationError(
                "La suma de unidades malas y pendientes no puede superar la cantidad total."
            )

        if minimo_operativo <= 0:
            raise forms.ValidationError("El mínimo operativo debe ser mayor a 0.")

        if minimo_operativo > cantidad:
            raise forms.ValidationError(
                "El mínimo operativo no puede ser mayor que la cantidad total."
            )

        return cleaned

class EditarHistorico(forms.ModelForm):
    fecha_anterior = forms.DateField(
        input_formats=["%d/%m/%Y"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={
                "class": "form-control",
                "placeholder": "dd/mm/aaaa",
            },
        ),
    )

    importancia_anterior = forms.TypedChoiceField(
        label="Importancia anterior",
        required=True,
        coerce=int,
        choices=(
            (1, "Baja"),
            (2, "Media"),
            (3, "Alta / Crítica"),
        ),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = HistoricoObjeto
        fields = [
            "objeto_del_lugar",
            "cantidad_anterior",
            "cantidad_mala_anterior",
            "cantidad_pendiente_anterior",
            "minimo_operativo_anterior",
            "importancia_anterior",
            "estado_anterior",
            "detalle_anterior",
            "fecha_anterior",
        ]

        widgets = {
            "objeto_del_lugar": forms.Select(attrs={"class": "form-select"}),
            "cantidad_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "cantidad_mala_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "cantidad_pendiente_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
            "minimo_operativo_anterior": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "estado_anterior": forms.Select(attrs={"class": "form-select"}),
            "detalle_anterior": forms.TextInput(attrs={"class": "form-control"}),
        }

        labels = {
            "objeto_del_lugar": "Objeto del lugar",
            "cantidad_anterior": "Cantidad total anterior",
            "cantidad_mala_anterior": "Cantidad mala anterior",
            "cantidad_pendiente_anterior": "Cantidad pendiente anterior",
            "minimo_operativo_anterior": "Mínimo operativo anterior",
            "estado_anterior": "Condición anterior",
            "detalle_anterior": "Detalle anterior",
            "fecha_anterior": "Fecha anterior",
        }

    def clean(self):
        cleaned = super().clean()

        cantidad = cleaned.get("cantidad_anterior") or 0
        cantidad_mala = cleaned.get("cantidad_mala_anterior") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente_anterior") or 0
        minimo_operativo = cleaned.get("minimo_operativo_anterior") or 1

        if cantidad <= 0:
            raise forms.ValidationError("La cantidad total anterior debe ser mayor a 0.")

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise forms.ValidationError(
                "La suma de cantidad mala anterior y cantidad pendiente anterior no puede superar la cantidad total anterior."
            )

        if minimo_operativo > cantidad:
            raise forms.ValidationError(
                "El mínimo operativo anterior no puede ser mayor que la cantidad total anterior."
            )

        return cleaned

# ============================
# FORMULARIO BASE DE ESTRUCTURA
# ============================

class EstructuraCompletaForm(forms.Form):
    # --- Sector ---
    sector_existente = forms.ModelChoiceField(
        label="Sector (existente)",
        queryset=Sector.objects.all().order_by("sector"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sector_nuevo = forms.CharField(
        label="Nuevo sector",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # --- Ubicación ---
    ubicacion_existente = forms.ModelChoiceField(
        label="Ubicación (existente)",
        queryset=Ubicacion.objects.none(), # se llena por JS / __init__
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    ubicacion_nueva = forms.CharField(
        label="Nueva ubicación",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # --- Piso ---
    piso_existente = forms.ModelChoiceField(
        label="Piso (existente)",
        queryset=Piso.objects.none(), # se llena por JS / __init__
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    piso_nuevo = forms.IntegerField(
        label="Nuevo piso",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    # --- Tipo de lugar ---
    tipo_lugar_existente = forms.ModelChoiceField(
        label="Tipo de lugar (existente)",
        queryset=TipoLugar.objects.all().order_by("tipo_de_lugar"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    tipo_lugar_nuevo = forms.CharField(
        label="Nuevo tipo de lugar",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    # ✅ NUEVO: Lugar existente / nuevo
    lugar_existente = forms.ModelChoiceField(
        label="Lugar (existente)",
        queryset=Lugar.objects.none(), # se llena por JS / __init__
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    lugar_nuevo = forms.CharField(
        label="Nuevo lugar",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data = self.data or None

        # Dependientes: por defecto vacíos (para no listar TODO)
        self.fields["ubicacion_existente"].queryset = Ubicacion.objects.none()
        self.fields["piso_existente"].queryset = Piso.objects.none()
        self.fields["lugar_existente"].queryset = Lugar.objects.none()

        if not data:
            return

        sector_id = (data.get("sector_existente") or "").strip()
        ubicacion_id = (data.get("ubicacion_existente") or "").strip()
        piso_id = (data.get("piso_existente") or "").strip()
        tipo_lugar_id = (data.get("tipo_lugar_existente") or "").strip()

        if sector_id.isdigit():
            self.fields["ubicacion_existente"].queryset = (
                Ubicacion.objects.filter(sector_id=int(sector_id)).order_by("ubicacion")
            )

        if ubicacion_id.isdigit():
            self.fields["piso_existente"].queryset = (
                Piso.objects.filter(ubicacion_id=int(ubicacion_id)).order_by("piso")
            )

        if piso_id.isdigit() and tipo_lugar_id.isdigit():
            self.fields["lugar_existente"].queryset = (
                Lugar.objects.filter(
                    piso_id=int(piso_id),
                    lugar_tipo_lugar_id=int(tipo_lugar_id),
                ).order_by("nombre_del_lugar")
            )

    def clean(self):
        cleaned = super().clean()

        # Sector: existente o nuevo
        if not cleaned.get("sector_existente") and not (cleaned.get("sector_nuevo") or "").strip():
            raise forms.ValidationError("Debes seleccionar un sector existente o escribir uno nuevo.")

        # Ubicación: existente o nueva
        if not cleaned.get("ubicacion_existente") and not (cleaned.get("ubicacion_nueva") or "").strip():
            raise forms.ValidationError("Debes seleccionar una ubicación existente o escribir una nueva.")

        # Piso: existente o nuevo
        if not cleaned.get("piso_existente") and cleaned.get("piso_nuevo") in (None, ""):
            raise forms.ValidationError("Debes seleccionar un piso existente o escribir uno nuevo.")

        # Tipo de lugar: existente o nuevo
        if not cleaned.get("tipo_lugar_existente") and not (cleaned.get("tipo_lugar_nuevo") or "").strip():
            raise forms.ValidationError("Debes seleccionar un tipo de lugar existente o escribir uno nuevo.")

        # ✅ Lugar: existente o nuevo
        lugar_exist = cleaned.get("lugar_existente")
        lugar_new = (cleaned.get("lugar_nuevo") or "").strip()

        if lugar_exist and lugar_new:
            raise forms.ValidationError("Selecciona un lugar existente o escribe uno nuevo (no ambos).")

        if not lugar_exist and not lugar_new:
            raise forms.ValidationError("Debes seleccionar un lugar existente o escribir uno nuevo.")

        # Si eligió lugar existente, debe calzar con piso/tipo de lugar existentes
        piso_obj = cleaned.get("piso_existente")
        tipo_obj = cleaned.get("tipo_lugar_existente")

        if lugar_exist:
            if not piso_obj or not tipo_obj:
                raise forms.ValidationError("Para elegir un lugar existente debes seleccionar Piso y Tipo de lugar (existentes).")

            if lugar_exist.piso_id != piso_obj.id or lugar_exist.lugar_tipo_lugar_id != tipo_obj.id:
                raise forms.ValidationError("El lugar seleccionado no coincide con el Piso/Tipo de lugar.")

        return cleaned


# ============================
# FORMULARIO DE FILA DE OBJETO
# ============================

class ObjetoLugarFilaForm(forms.Form):
    # --- Categoría ---
    categoria_existente = forms.ModelChoiceField(
        label="Categoría (existente)",
        queryset=CategoriaObjeto.objects.all().order_by("nombre_de_categoria"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    categoria_nueva = forms.CharField(
        label="Nueva categoría",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )

    # --- Objeto ---
    objeto_existente = forms.ModelChoiceField(
        label="Objeto (existente)",
        queryset=Objeto.objects.select_related("objeto_categoria")
        .all()
        .order_by("objeto_categoria__nombre_de_categoria", "nombre_del_objeto"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    objeto_nuevo = forms.CharField(
        label="Nuevo objeto",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )

    # --- Tipo de objeto ---
    tipo_objeto_existente = forms.ModelChoiceField(
        label="Tipo de objeto (existente)",
        queryset=TipoObjeto.objects.select_related("objeto")
        .all()
        .order_by("objeto__nombre_del_objeto", "marca", "material"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    marca = forms.CharField(
        label="Marca",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )
    material = forms.CharField(
        label="Material",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )

    # --- Datos del objeto en el lugar ---
    cantidad = forms.IntegerField(
        label="Cantidad",
        min_value=1,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm", "style": "width: 80px;"}
        ),
    )
    estado = forms.ChoiceField(
        label="Estado",
        required=False,
        choices=ObjetoLugar.ESTADO,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    detalle = forms.CharField(
        label="Detalle",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control form-control-sm"}),
    )
    importancia = forms.TypedChoiceField(
        label="Importancia",
        required=False,
        coerce=int,
        choices=(
            (1, "Baja"),
            (2, "Media"),
            (3, "Alta / Crítica"),
        ),
        initial=1,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )

    cantidad_mala = forms.IntegerField(
        label="Cantidad mala",
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm", "style": "width: 90px;"}
        ),
    )

    cantidad_pendiente = forms.IntegerField(
        label="Cantidad pendiente",
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm", "style": "width: 90px;"}
        ),
    )

    minimo_operativo = forms.IntegerField(
        label="Mínimo operativo",
        min_value=1,
        required=False,
        initial=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm", "style": "width: 90px;"}
        ),
    )

    def clean(self):
        cleaned = super().clean()

        # Primero revisamos si la fila está realmente vacía.
        # No metemos importancia, cantidad_mala, cantidad_pendiente ni minimo_operativo
        # porque tienen valores por defecto y podrían hacer parecer usada una fila vacía.
        fields_to_check = [
            "categoria_existente", "categoria_nueva",
            "objeto_existente", "objeto_nuevo",
            "tipo_objeto_existente", "marca", "material",
            "cantidad", "detalle",
        ]

        if not any(cleaned.get(f) not in (None, "", 0) for f in fields_to_check):
            cleaned["__empty__"] = True
            return cleaned

        # Desde aquí la fila ya se considera usada.
        cantidad = cleaned.get("cantidad")
        cantidad_mala = cleaned.get("cantidad_mala") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente") or 0
        minimo_operativo = cleaned.get("minimo_operativo") or 1

        if cantidad in (None, ""):
            raise forms.ValidationError("En cada fila usada debes indicar la cantidad.")

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise forms.ValidationError(
                "La suma de cantidad mala y cantidad pendiente no puede superar la cantidad total."
            )

        if minimo_operativo > cantidad:
            raise forms.ValidationError(
                "El mínimo operativo no puede ser mayor que la cantidad total."
            )

        # Categoría: existente o nueva
        if not cleaned.get("categoria_existente") and not (cleaned.get("categoria_nueva") or "").strip():
            raise forms.ValidationError(
                "En cada fila usa una categoría existente o escribe una nueva."
            )

        # Objeto: existente o nuevo
        if not cleaned.get("objeto_existente") and not (cleaned.get("objeto_nuevo") or "").strip():
            raise forms.ValidationError(
                "En cada fila usa un objeto existente o escribe uno nuevo."
            )

        cleaned["importancia"] = cleaned.get("importancia") or 1
        cleaned["cantidad_mala"] = cantidad_mala
        cleaned["cantidad_pendiente"] = cantidad_pendiente
        cleaned["minimo_operativo"] = minimo_operativo
        cleaned["__empty__"] = False

        return cleaned


ObjetoLugarFilaFormSet = formset_factory(
    ObjetoLugarFilaForm,
    extra=1,
    can_delete=False,
)


class UploadExcelForm(forms.Form):
    archivo = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".xlsx"}
        )
    )