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


def _normalizar_nombre(valor):
    return " ".join((valor or "").split())


class CrearSector(ModelForm):
    class Meta:
        model = Sector
        fields = ["sector"]
        widgets = {
            "sector": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Patio Norte",
                    "autocomplete": "off",
                }
            )
        }

    def clean_sector(self):
        nombre = _normalizar_nombre(self.cleaned_data.get("sector"))

        if not nombre:
            return nombre

        if Sector.objects.filter(sector__iexact=nombre).exists():
            raise forms.ValidationError(
                "Ya existe un sector con este nombre."
            )

        return nombre


class CrearUbicacion(ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["ubicacion", "sector"]
        widgets = {
            "ubicacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Edificio Central",
                    "autocomplete": "off",
                }
            ),
            "sector": forms.Select(attrs={"class": "form-select"}),
        }

    def clean_ubicacion(self):
        nombre = _normalizar_nombre(self.cleaned_data.get("ubicacion"))

        if not nombre:
            return nombre

        existente = (
            Ubicacion.objects
            .select_related("sector")
            .filter(ubicacion__iexact=nombre)
            .first()
        )

        if existente:
            raise forms.ValidationError(
                f'Ya existe la ubicación "{existente.ubicacion}" '
                f'en el sector "{existente.sector.sector}".'
            )

        return nombre


class CrearPiso(ModelForm):
    class Meta:
        model = Piso
        fields = ["piso", "ubicacion"]
        widgets = {
            "piso": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "1",
                }
            ),
            "ubicacion": forms.Select(attrs={"class": "form-select"}),
        }

    def clean(self):
        cleaned = super().clean()

        piso = cleaned.get("piso")
        ubicacion = cleaned.get("ubicacion")

        if piso is not None and ubicacion:
            if Piso.objects.filter(
                piso=piso,
                ubicacion=ubicacion,
            ).exists():
                self.add_error(
                    "piso",
                    f"El piso {piso} ya existe en esta ubicación.",
                )

        return cleaned



class CrearLugar(ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre_del_lugar", "piso", "lugar_tipo_lugar"]
        widgets = {
            "nombre_del_lugar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Baño hombres principal",
                    "autocomplete": "off",
                }
            ),
            "piso": forms.Select(
                attrs={"class": "form-select"}
            ),
            "lugar_tipo_lugar": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["piso"].queryset = (
            Piso.objects
            .select_related("ubicacion", "ubicacion__sector")
            .order_by(
                "ubicacion__sector__sector",
                "ubicacion__ubicacion",
                "piso",
            )
        )

        self.fields["piso"].label_from_instance = (
            lambda piso:
            f"{piso.ubicacion.sector.sector} · "
            f"{piso.ubicacion.ubicacion} · "
            f"Piso {piso.piso}"
        )

    def clean_nombre_del_lugar(self):
        nombre = " ".join(
            (self.cleaned_data.get("nombre_del_lugar") or "").split()
        )
        return nombre

    def clean(self):
        cleaned = super().clean()

        nombre = cleaned.get("nombre_del_lugar")
        piso = cleaned.get("piso")

        if not nombre or not piso:
            return cleaned

        nombre_normalizado = nombre.casefold()

        existentes = Lugar.objects.filter(piso=piso)

        for existente in existentes:
            nombre_existente = " ".join(
                (existente.nombre_del_lugar or "").split()
            ).casefold()

            if nombre_existente == nombre_normalizado:
                self.add_error(
                    "nombre_del_lugar",
                    "Ya existe un lugar con este nombre en el piso seleccionado.",
                )
                break

        return cleaned


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
        widgets = {
            "tipo_de_lugar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Baño",
                    "autocomplete": "off",
                }
            )
        }

    def clean_tipo_de_lugar(self):
        nombre = " ".join(
            (self.cleaned_data.get("tipo_de_lugar") or "").split()
        )

        if not nombre:
            return nombre

        if TipoLugar.objects.filter(
            tipo_de_lugar__iexact=nombre
        ).exists():
            raise forms.ValidationError(
                "Ya existe un tipo de lugar con este nombre."
            )

        return nombre


class CrearCategoriaObjeto(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_categoria"]
        widgets = {
            "nombre_de_categoria": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Sanitarios",
                    "autocomplete": "off",
                }
            )
        }

    def clean_nombre_de_categoria(self):
        nombre = " ".join(
            (self.cleaned_data.get("nombre_de_categoria") or "").split()
        )

        if not nombre:
            return nombre

        if CategoriaObjeto.objects.filter(
            nombre_de_categoria__iexact=nombre
        ).exists():
            raise forms.ValidationError(
                "Ya existe una categoría con este nombre."
            )

        return nombre


class CrearObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "objeto_categoria"]
        widgets = {
            "nombre_del_objeto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Lavamanos",
                    "autocomplete": "off",
                }
            ),
            "objeto_categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def clean_nombre_del_objeto(self):
        nombre = " ".join(
            (self.cleaned_data.get("nombre_del_objeto") or "").split()
        )

        if not nombre:
            return nombre

        if Objeto.objects.filter(
            nombre_del_objeto__iexact=nombre
        ).exists():
            raise forms.ValidationError(
                "Ya existe un objeto con este nombre."
            )

        return nombre


class CrearTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]
        widgets = {
            "objeto": forms.Select(
                attrs={"class": "form-select"}
            ),
            "marca": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Fanaloza",
                    "autocomplete": "off",
                }
            ),
            "material": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ej: Cerámica",
                    "autocomplete": "off",
                }
            ),
        }

    def clean_marca(self):
        valor = " ".join(
            (self.cleaned_data.get("marca") or "").split()
        )
        return valor or None

    def clean_material(self):
        valor = " ".join(
            (self.cleaned_data.get("material") or "").split()
        )
        return valor or None

    def clean(self):
        cleaned = super().clean()

        objeto = cleaned.get("objeto")
        marca = cleaned.get("marca")
        material = cleaned.get("material")

        if not objeto:
            return cleaned

        marca_normalizada = (marca or "").strip().casefold()
        material_normalizado = (material or "").strip().casefold()

        for existente in TipoObjeto.objects.filter(objeto=objeto):
            if (
                (existente.marca or "").strip().casefold() == marca_normalizada
                and
                (existente.material or "").strip().casefold() == material_normalizado
            ):
                raise forms.ValidationError(
                    "Esta variante ya existe para el objeto seleccionado."
                )

        return cleaned

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


class EditarSector(ModelForm):
    class Meta:
        model = Sector
        fields = ["sector"]
        widgets = {
            "sector": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            )
        }

    def clean_sector(self):
        nombre = _normalizar_nombre(self.cleaned_data.get("sector"))

        if not nombre:
            return nombre

        existe = (
            Sector.objects
            .filter(sector__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                "Ya existe otro sector con este nombre."
            )

        return nombre


class EditarUbicacion(ModelForm):
    class Meta:
        model = Ubicacion
        fields = ["ubicacion"]
        widgets = {
            "ubicacion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            )
        }

    def clean_ubicacion(self):
        nombre = _normalizar_nombre(self.cleaned_data.get("ubicacion"))

        if not nombre:
            return nombre

        existente = (
            Ubicacion.objects
            .select_related("sector")
            .filter(ubicacion__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .first()
        )

        if existente:
            raise forms.ValidationError(
                f'Ya existe la ubicación "{existente.ubicacion}" '
                f'en el sector "{existente.sector.sector}".'
            )

        return nombre


class EditarPiso(ModelForm):
    class Meta:
        model = Piso
        fields = ["piso"]
        widgets = {
            "piso": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "1",
                }
            )
        }

    def clean_piso(self):
        piso = self.cleaned_data.get("piso")

        if piso is None:
            return piso

        existe = (
            Piso.objects
            .filter(
                piso=piso,
                ubicacion_id=self.instance.ubicacion_id,
            )
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                f"El piso {piso} ya existe en esta ubicación."
            )

        return piso



class EditarTipoLugar(ModelForm):
    class Meta:
        model = TipoLugar
        fields = ["tipo_de_lugar"]
        widgets = {
            "tipo_de_lugar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            )
        }

    def clean_tipo_de_lugar(self):
        nombre = " ".join(
            (self.cleaned_data.get("tipo_de_lugar") or "").split()
        )

        if not nombre:
            return nombre

        existe = (
            TipoLugar.objects
            .filter(tipo_de_lugar__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                "Ya existe otro tipo de lugar con este nombre."
            )

        return nombre



class EditarLugar(ModelForm):
    class Meta:
        model = Lugar
        fields = ["nombre_del_lugar", "piso", "lugar_tipo_lugar"]
        widgets = {
            "nombre_del_lugar": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "piso": forms.Select(
                attrs={"class": "form-select"}
            ),
            "lugar_tipo_lugar": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["piso"].queryset = (
            Piso.objects
            .select_related("ubicacion", "ubicacion__sector")
            .order_by(
                "ubicacion__sector__sector",
                "ubicacion__ubicacion",
                "piso",
            )
        )

        self.fields["piso"].label_from_instance = (
            lambda piso:
            f"{piso.ubicacion.sector.sector} · "
            f"{piso.ubicacion.ubicacion} · "
            f"Piso {piso.piso}"
        )

    def clean_nombre_del_lugar(self):
        nombre = " ".join(
            (self.cleaned_data.get("nombre_del_lugar") or "").split()
        )
        return nombre

    def clean(self):
        cleaned = super().clean()

        nombre = cleaned.get("nombre_del_lugar")
        piso = cleaned.get("piso")

        if not nombre or not piso:
            return cleaned

        nombre_normalizado = nombre.casefold()

        existentes = (
            Lugar.objects
            .filter(piso=piso)
            .exclude(pk=self.instance.pk)
        )

        for existente in existentes:
            nombre_existente = " ".join(
                (existente.nombre_del_lugar or "").split()
            ).casefold()

            if nombre_existente == nombre_normalizado:
                self.add_error(
                    "nombre_del_lugar",
                    "Ya existe otro lugar con este nombre en el piso seleccionado.",
                )
                break

        return cleaned


class EditarCategoria(ModelForm):
    class Meta:
        model = CategoriaObjeto
        fields = ["nombre_de_categoria"]
        widgets = {
            "nombre_de_categoria": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            )
        }

    def clean_nombre_de_categoria(self):
        nombre = " ".join(
            (self.cleaned_data.get("nombre_de_categoria") or "").split()
        )

        if not nombre:
            return nombre

        existe = (
            CategoriaObjeto.objects
            .filter(nombre_de_categoria__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                "Ya existe otra categoría con este nombre."
            )

        return nombre


class EditarObjeto(ModelForm):
    class Meta:
        model = Objeto
        fields = ["nombre_del_objeto", "objeto_categoria"]
        widgets = {
            "nombre_del_objeto": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "objeto_categoria": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    def clean_nombre_del_objeto(self):
        nombre = " ".join(
            (self.cleaned_data.get("nombre_del_objeto") or "").split()
        )

        if not nombre:
            return nombre

        existe = (
            Objeto.objects
            .filter(nombre_del_objeto__iexact=nombre)
            .exclude(pk=self.instance.pk)
            .exists()
        )

        if existe:
            raise forms.ValidationError(
                "Ya existe otro objeto con este nombre."
            )

        return nombre



class EditarTipoObjeto(ModelForm):
    class Meta:
        model = TipoObjeto
        fields = ["objeto", "marca", "material"]
        widgets = {
            "objeto": forms.Select(
                attrs={"class": "form-select"}
            ),
            "marca": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
            "material": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "autocomplete": "off",
                }
            ),
        }

    def clean_marca(self):
        valor = " ".join(
            (self.cleaned_data.get("marca") or "").split()
        )
        return valor or None

    def clean_material(self):
        valor = " ".join(
            (self.cleaned_data.get("material") or "").split()
        )
        return valor or None

    def clean(self):
        cleaned = super().clean()

        objeto = cleaned.get("objeto")
        marca = cleaned.get("marca")
        material = cleaned.get("material")

        if not objeto:
            return cleaned

        marca_normalizada = (marca or "").strip().casefold()
        material_normalizado = (material or "").strip().casefold()

        existentes = (
            TipoObjeto.objects
            .filter(objeto=objeto)
            .exclude(pk=self.instance.pk)
        )

        for existente in existentes:
            if (
                (existente.marca or "").strip().casefold() == marca_normalizada
                and
                (existente.material or "").strip().casefold() == material_normalizado
            ):
                raise forms.ValidationError(
                    "Ya existe otra variante con esta misma marca y material."
                )

        return cleaned


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


class EstructuraCompletaForm(forms.Form):
    sector_existente = forms.ModelChoiceField(
        label="Sector existente",
        queryset=Sector.objects.all().order_by("sector"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sector_nuevo = forms.CharField(
        label="Nuevo sector",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
            }
        ),
    )

    ubicacion_existente = forms.ModelChoiceField(
        label="Ubicación existente",
        queryset=Ubicacion.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    ubicacion_nueva = forms.CharField(
        label="Nueva ubicación",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
            }
        ),
    )

    piso_existente = forms.ModelChoiceField(
        label="Piso existente",
        queryset=Piso.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    piso_nuevo = forms.IntegerField(
        label="Nuevo piso",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    tipo_lugar_existente = forms.ModelChoiceField(
        label="Tipo de lugar existente",
        queryset=TipoLugar.objects.all().order_by("tipo_de_lugar"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    tipo_lugar_nuevo = forms.CharField(
        label="Nuevo tipo de lugar",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
            }
        ),
    )

    lugar_existente = forms.ModelChoiceField(
        label="Lugar existente",
        queryset=Lugar.objects.none(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    lugar_nuevo = forms.CharField(
        label="Nuevo lugar",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "off",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        data = self.data or None

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
                Ubicacion.objects
                .filter(sector_id=int(sector_id))
                .order_by("ubicacion")
            )

        if ubicacion_id.isdigit():
            self.fields["piso_existente"].queryset = (
                Piso.objects
                .filter(ubicacion_id=int(ubicacion_id))
                .order_by("piso")
            )

        if piso_id.isdigit() and tipo_lugar_id.isdigit():
            self.fields["lugar_existente"].queryset = (
                Lugar.objects
                .filter(
                    piso_id=int(piso_id),
                    lugar_tipo_lugar_id=int(tipo_lugar_id),
                )
                .order_by("nombre_del_lugar")
            )

    def clean(self):
        cleaned = super().clean()

        def texto(valor):
            return " ".join((valor or "").split())

        pares = (
            ("sector_existente", "sector_nuevo", "sector"),
            ("ubicacion_existente", "ubicacion_nueva", "ubicación"),
            ("piso_existente", "piso_nuevo", "piso"),
            ("tipo_lugar_existente", "tipo_lugar_nuevo", "tipo de lugar"),
            ("lugar_existente", "lugar_nuevo", "lugar"),
        )

        for existente, nuevo, nombre in pares:
            valor_existente = cleaned.get(existente)
            valor_nuevo = cleaned.get(nuevo)

            if isinstance(valor_nuevo, str):
                valor_nuevo = texto(valor_nuevo)
                cleaned[nuevo] = valor_nuevo

            vacio_nuevo = valor_nuevo in (None, "")

            if valor_existente and not vacio_nuevo:
                self.add_error(
                    nuevo,
                    f"Selecciona un {nombre} existente o crea uno nuevo, no ambos.",
                )
            elif not valor_existente and vacio_nuevo:
                self.add_error(
                    nuevo,
                    f"Selecciona un {nombre} existente o crea uno nuevo.",
                )

        sector_nuevo = cleaned.get("sector_nuevo")
        if sector_nuevo and Sector.objects.filter(
            sector__iexact=sector_nuevo
        ).exists():
            self.add_error(
                "sector_nuevo",
                "Ya existe un sector con este nombre. Selecciónalo como existente.",
            )

        ubicacion_nueva = cleaned.get("ubicacion_nueva")
        if ubicacion_nueva:
            existente = (
                Ubicacion.objects
                .select_related("sector")
                .filter(ubicacion__iexact=ubicacion_nueva)
                .first()
            )
            if existente:
                self.add_error(
                    "ubicacion_nueva",
                    f"Ya existe esta ubicación en el sector {existente.sector.sector}. "
                    "Selecciónala como existente.",
                )

        piso_nuevo = cleaned.get("piso_nuevo")
        ubicacion_existente = cleaned.get("ubicacion_existente")

        if piso_nuevo not in (None, "") and ubicacion_existente:
            if Piso.objects.filter(
                ubicacion=ubicacion_existente,
                piso=piso_nuevo,
            ).exists():
                self.add_error(
                    "piso_nuevo",
                    "Este piso ya existe en la ubicación seleccionada.",
                )

        tipo_lugar_nuevo = cleaned.get("tipo_lugar_nuevo")
        if tipo_lugar_nuevo and TipoLugar.objects.filter(
            tipo_de_lugar__iexact=tipo_lugar_nuevo
        ).exists():
            self.add_error(
                "tipo_lugar_nuevo",
                "Ya existe un tipo de lugar con este nombre. Selecciónalo como existente.",
            )

        lugar_existente = cleaned.get("lugar_existente")
        lugar_nuevo = cleaned.get("lugar_nuevo")
        piso_existente = cleaned.get("piso_existente")
        tipo_lugar_existente = cleaned.get("tipo_lugar_existente")

        if lugar_existente:
            if not piso_existente or not tipo_lugar_existente:
                self.add_error(
                    "lugar_existente",
                    "Para usar un lugar existente debes seleccionar un piso y tipo de lugar existentes.",
                )
            elif (
                lugar_existente.piso_id != piso_existente.id
                or lugar_existente.lugar_tipo_lugar_id != tipo_lugar_existente.id
            ):
                self.add_error(
                    "lugar_existente",
                    "El lugar seleccionado no coincide con el piso y tipo de lugar elegidos.",
                )

        if lugar_nuevo and piso_existente:
            if Lugar.objects.filter(
                piso=piso_existente,
                nombre_del_lugar__iexact=lugar_nuevo,
            ).exists():
                self.add_error(
                    "lugar_nuevo",
                    "Ya existe un lugar con este nombre en el piso seleccionado.",
                )

        return cleaned


class ObjetoLugarFilaForm(forms.Form):
    categoria_existente = forms.ModelChoiceField(
        label="Categoría existente",
        queryset=CategoriaObjeto.objects.all().order_by("nombre_de_categoria"),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    categoria_nueva = forms.CharField(
        label="Nueva categoría",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "autocomplete": "off",
            }
        ),
    )

    objeto_existente = forms.ModelChoiceField(
        label="Objeto existente",
        queryset=(
            Objeto.objects
            .select_related("objeto_categoria")
            .all()
            .order_by(
                "objeto_categoria__nombre_de_categoria",
                "nombre_del_objeto",
            )
        ),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    objeto_nuevo = forms.CharField(
        label="Nuevo objeto",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "autocomplete": "off",
            }
        ),
    )

    tipo_objeto_existente = forms.ModelChoiceField(
        label="Variante existente",
        queryset=(
            TipoObjeto.objects
            .select_related("objeto")
            .all()
            .order_by("objeto__nombre_del_objeto", "marca", "material")
        ),
        required=False,
        widget=forms.Select(attrs={"class": "form-select form-select-sm"}),
    )
    marca = forms.CharField(
        label="Marca",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "autocomplete": "off",
            }
        ),
    )
    material = forms.CharField(
        label="Material",
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-sm",
                "autocomplete": "off",
            }
        ),
    )

    cantidad = forms.IntegerField(
        label="Cantidad total",
        min_value=1,
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm"}
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
        widget=forms.TextInput(
            attrs={"class": "form-control form-control-sm"}
        ),
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
        label="Con falla",
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm"}
        ),
    )
    cantidad_pendiente = forms.IntegerField(
        label="Por revisar",
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm"}
        ),
    )
    minimo_operativo = forms.IntegerField(
        label="Mínimo operativo",
        min_value=1,
        required=False,
        initial=1,
        widget=forms.NumberInput(
            attrs={"class": "form-control form-control-sm"}
        ),
    )

    def clean(self):
        cleaned = super().clean()

        def texto(valor):
            return " ".join((valor or "").split())

        fields_to_check = [
            "categoria_existente",
            "categoria_nueva",
            "objeto_existente",
            "objeto_nuevo",
            "tipo_objeto_existente",
            "marca",
            "material",
            "cantidad",
            "detalle",
        ]

        if not any(
            cleaned.get(field) not in (None, "", 0)
            for field in fields_to_check
        ):
            cleaned["__empty__"] = True
            return cleaned

        categoria_existente = cleaned.get("categoria_existente")
        categoria_nueva = texto(cleaned.get("categoria_nueva"))
        objeto_existente = cleaned.get("objeto_existente")
        objeto_nuevo = texto(cleaned.get("objeto_nuevo"))
        tipo_existente = cleaned.get("tipo_objeto_existente")
        marca = texto(cleaned.get("marca"))
        material = texto(cleaned.get("material"))

        cleaned["categoria_nueva"] = categoria_nueva
        cleaned["objeto_nuevo"] = objeto_nuevo
        cleaned["marca"] = marca
        cleaned["material"] = material

        if categoria_existente and categoria_nueva:
            self.add_error(
                "categoria_nueva",
                "Usa una categoría existente o crea una nueva, no ambas.",
            )
        elif not categoria_existente and not categoria_nueva:
            self.add_error(
                "categoria_nueva",
                "Selecciona una categoría existente o crea una nueva.",
            )

        if categoria_nueva and CategoriaObjeto.objects.filter(
            nombre_de_categoria__iexact=categoria_nueva
        ).exists():
            self.add_error(
                "categoria_nueva",
                "Esta categoría ya existe. Selecciónala como existente.",
            )

        if objeto_existente and objeto_nuevo:
            self.add_error(
                "objeto_nuevo",
                "Usa un objeto existente o crea uno nuevo, no ambos.",
            )
        elif not objeto_existente and not objeto_nuevo:
            self.add_error(
                "objeto_nuevo",
                "Selecciona un objeto existente o crea uno nuevo.",
            )

        if objeto_nuevo and Objeto.objects.filter(
            nombre_del_objeto__iexact=objeto_nuevo
        ).exists():
            self.add_error(
                "objeto_nuevo",
                "Este objeto ya existe. Selecciónalo como existente.",
            )

        if (
            categoria_existente
            and objeto_existente
            and objeto_existente.objeto_categoria_id != categoria_existente.id
        ):
            self.add_error(
                "objeto_existente",
                "El objeto seleccionado no pertenece a la categoría elegida.",
            )

        if tipo_existente and (marca or material):
            self.add_error(
                "tipo_objeto_existente",
                "Usa una variante existente o escribe marca/material para crear una nueva, no ambas.",
            )

        if (
            tipo_existente
            and objeto_existente
            and tipo_existente.objeto_id != objeto_existente.id
        ):
            self.add_error(
                "tipo_objeto_existente",
                "La variante seleccionada no pertenece al objeto elegido.",
            )

        if not tipo_existente and objeto_existente:
            marca_normalizada = marca.casefold()
            material_normalizado = material.casefold()

            for existente in TipoObjeto.objects.filter(objeto=objeto_existente):
                if (
                    (existente.marca or "").strip().casefold()
                    == marca_normalizada
                    and
                    (existente.material or "").strip().casefold()
                    == material_normalizado
                ):
                    self.add_error(
                        "tipo_objeto_existente",
                        "Esta variante ya existe. Selecciónala como variante existente.",
                    )
                    break

        cantidad = cleaned.get("cantidad")
        cantidad_mala = cleaned.get("cantidad_mala") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente") or 0
        minimo_operativo = cleaned.get("minimo_operativo") or 1

        if cantidad in (None, ""):
            self.add_error(
                "cantidad",
                "Indica la cantidad total.",
            )
        else:
            if cantidad_mala + cantidad_pendiente > cantidad:
                raise forms.ValidationError(
                    "La suma de unidades con falla y por revisar no puede superar la cantidad total."
                )

            if minimo_operativo > cantidad:
                self.add_error(
                    "minimo_operativo",
                    "El mínimo operativo no puede ser mayor que la cantidad total.",
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

