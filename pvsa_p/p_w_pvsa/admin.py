
import nested_admin
from django.contrib import admin
from django import forms

from .models import (
    Sector,
    Ubicacion,
    Piso,
    TipoLugar,
    Lugar,
    CategoriaObjeto,
    Objeto,
    TipoObjeto,
    TipoLugarObjetoTipico,
    ObjetoLugar,
    HistoricoObjeto,
    AreaMapa,
)


admin.site.site_header = "Administración PVSA"
admin.site.site_title = "PVSA"
admin.site.index_title = "Panel de administración"


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def texto_importancia(valor):
    if valor == 3:
        return "Alta / Crítica"
    if valor == 2:
        return "Media"
    return "Baja"


# =====================================================
# HISTÓRICO INLINE
# =====================================================

class HistoricoObjetoInline(nested_admin.NestedTabularInline):
    model = HistoricoObjeto
    extra = 0
    can_delete = False

    fields = (
        "cantidad_anterior",
        "cantidad_mala_anterior",
        "cantidad_pendiente_anterior",
        "minimo_operativo_anterior",
        "importancia_anterior",
        "estado_anterior",
        "detalle_anterior",
        "fecha_anterior",
    )

    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


# =====================================================
# OBJETO LUGAR INLINE
# =====================================================

class ObjetoLugarInline(nested_admin.NestedTabularInline):
    model = ObjetoLugar
    extra = 0
    inlines = [HistoricoObjetoInline]

    fields = (
        "tipo_de_objeto",
        "cantidad",
        "cantidad_buena_admin",
        "cantidad_mala",
        "cantidad_pendiente",
        "minimo_operativo",
        "importancia",
        "operatividad_objeto_admin",
        "estado_calculado_admin",
        "detalle",
        "fecha",
    )

    readonly_fields = (
        "cantidad_buena_admin",
        "operatividad_objeto_admin",
        "estado_calculado_admin",
        "fecha",
    )

    autocomplete_fields = ("tipo_de_objeto",)

    @admin.display(description="Buenas")
    def cantidad_buena_admin(self, obj):
        if obj and obj.pk:
            return obj.cantidad_buena
        return "-"

    @admin.display(description="Operatividad")
    def operatividad_objeto_admin(self, obj):
        if obj and obj.pk:
            return f"{obj.operatividad_objeto}%"
        return "-"

    @admin.display(description="Condición")
    def estado_calculado_admin(self, obj):
        if obj and obj.pk:
            if obj.estado == "B":
                return "Todo bueno"
            if obj.estado == "P":
                return "Con pendientes"
            return "Con unidades malas"
        return "-"


# =====================================================
# LUGAR INLINE
# =====================================================

class LugarInline(nested_admin.NestedStackedInline):
    model = Lugar
    extra = 0
    inlines = [ObjetoLugarInline]

    fields = (
        "nombre_del_lugar",
        "lugar_tipo_lugar",
        "operatividad_lugar_admin",
        "geom",
    )

    readonly_fields = ("operatividad_lugar_admin",)
    autocomplete_fields = ("lugar_tipo_lugar",)

    @admin.display(description="Operatividad del lugar")
    def operatividad_lugar_admin(self, obj):
        if obj and obj.pk:
            return f"{obj.operatividad_lugar}%"
        return "-"


# =====================================================
# PISO / UBICACIÓN / SECTOR
# =====================================================

class PisoInline(nested_admin.NestedStackedInline):
    model = Piso
    extra = 0
    inlines = [LugarInline]


class UbicacionInline(nested_admin.NestedStackedInline):
    model = Ubicacion
    extra = 0
    inlines = [PisoInline]

    fields = (
        "ubicacion",
        "geom",
    )


class SectorAdmin(nested_admin.NestedModelAdmin):
    inlines = [UbicacionInline]

    list_display = (
        "sector",
    )

    search_fields = (
        "sector",
    )


# =====================================================
# CATEGORÍA / OBJETO / TIPO OBJETO
# =====================================================

class TipoObjetoInline(nested_admin.NestedTabularInline):
    model = TipoObjeto
    extra = 0

    fields = (
        "marca",
        "material",
    )


class ObjetoInline(nested_admin.NestedStackedInline):
    model = Objeto
    extra = 0
    inlines = [TipoObjetoInline]

    fields = (
        "nombre_del_objeto",
    )


class CategoriaObjetoAdmin(nested_admin.NestedModelAdmin):
    inlines = [ObjetoInline]

    list_display = (
        "nombre_de_categoria",
    )

    search_fields = (
        "nombre_de_categoria",
    )


# =====================================================
# TIPO DE LUGAR Y OBJETOS TÍPICOS
# =====================================================

class TipoLugarObjetoTipicoInline(admin.TabularInline):
    model = TipoLugarObjetoTipico
    extra = 0

    fields = (
        "tipo_objeto",
        "importancia",
        "orden",
        "activo",
    )

    autocomplete_fields = (
        "tipo_objeto",
    )


class TipoLugarAdmin(admin.ModelAdmin):
    inlines = [TipoLugarObjetoTipicoInline]

    list_display = (
        "tipo_de_lugar",
        "cantidad_tipicos_admin",
    )

    search_fields = (
        "tipo_de_lugar",
    )

    @admin.display(description="Objetos típicos")
    def cantidad_tipicos_admin(self, obj):
        return obj.tipicos.count()


# =====================================================
# ADMIN INDIVIDUAL: UBICACIÓN / PISO / LUGAR
# =====================================================

class UbicacionAdmin(admin.ModelAdmin):
    list_display = (
        "ubicacion",
        "sector",
    )

    list_filter = (
        "sector",
    )

    search_fields = (
        "ubicacion",
        "sector__sector",
    )


class PisoAdmin(admin.ModelAdmin):
    list_display = (
        "piso",
        "ubicacion",
        "sector_admin",
    )

    list_filter = (
        "ubicacion__sector",
        "ubicacion",
    )

    search_fields = (
        "piso",
        "ubicacion__ubicacion",
        "ubicacion__sector__sector",
    )

    @admin.display(description="Sector")
    def sector_admin(self, obj):
        return obj.ubicacion.sector


class LugarAdmin(nested_admin.NestedModelAdmin):
    inlines = [ObjetoLugarInline]

    list_display = (
        "nombre_del_lugar",
        "tipo_lugar_admin",
        "piso",
        "ubicacion_admin",
        "sector_admin",
        "operatividad_lugar_admin",
    )

    list_filter = (
        "lugar_tipo_lugar",
        "piso__ubicacion__sector",
        "piso__ubicacion",
        "piso",
    )

    search_fields = (
        "nombre_del_lugar",
        "lugar_tipo_lugar__tipo_de_lugar",
        "piso__ubicacion__ubicacion",
        "piso__ubicacion__sector__sector",
    )

    readonly_fields = (
        "operatividad_lugar_admin",
    )

    fields = (
        "nombre_del_lugar",
        "piso",
        "lugar_tipo_lugar",
        "operatividad_lugar_admin",
        "geom",
    )

    @admin.display(description="Tipo de lugar")
    def tipo_lugar_admin(self, obj):
        return obj.lugar_tipo_lugar

    @admin.display(description="Ubicación")
    def ubicacion_admin(self, obj):
        return obj.piso.ubicacion

    @admin.display(description="Sector")
    def sector_admin(self, obj):
        return obj.piso.ubicacion.sector

    @admin.display(description="Operatividad")
    def operatividad_lugar_admin(self, obj):
        if obj and obj.pk:
            return f"{obj.operatividad_lugar}%"
        return "-"


# =====================================================
# ADMIN INDIVIDUAL: OBJETO / TIPO OBJETO
# =====================================================

class ObjetoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_del_objeto",
        "objeto_categoria",
    )

    list_filter = (
        "objeto_categoria",
    )

    search_fields = (
        "nombre_del_objeto",
        "objeto_categoria__nombre_de_categoria",
    )


class TipoObjetoAdmin(admin.ModelAdmin):
    list_display = (
        "objeto",
        "categoria_admin",
        "marca",
        "material",
    )

    list_filter = (
        "objeto__objeto_categoria",
        "marca",
        "material",
    )

    search_fields = (
        "objeto__nombre_del_objeto",
        "objeto__objeto_categoria__nombre_de_categoria",
        "marca",
        "material",
    )

    @admin.display(description="Categoría")
    def categoria_admin(self, obj):
        return obj.objeto.objeto_categoria


# =====================================================
# ADMIN INDIVIDUAL: OBJETO LUGAR
# =====================================================

class ObjetoLugarAdmin(nested_admin.NestedModelAdmin):
    inlines = [HistoricoObjetoInline]

    list_display = (
        "objeto_admin",
        "lugar",
        "cantidad",
        "cantidad_buena_admin",
        "cantidad_mala",
        "cantidad_pendiente",
        "minimo_operativo",
        "importancia_admin",
        "operatividad_objeto_admin",
        "estado_calculado_admin",
        "fecha",
    )

    list_filter = (
        "estado",
        "importancia",
        "lugar__lugar_tipo_lugar",
        "lugar__piso__ubicacion__sector",
        "lugar__piso__ubicacion",
        "tipo_de_objeto__objeto__objeto_categoria",
    )

    search_fields = (
        "tipo_de_objeto__objeto__nombre_del_objeto",
        "tipo_de_objeto__marca",
        "tipo_de_objeto__material",
        "lugar__nombre_del_lugar",
        "lugar__piso__ubicacion__ubicacion",
        "lugar__piso__ubicacion__sector__sector",
        "detalle",
    )

    autocomplete_fields = (
        "lugar",
        "tipo_de_objeto",
    )

    readonly_fields = (
        "cantidad_buena_admin",
        "operatividad_objeto_admin",
        "estado_calculado_admin",
        "fecha",
    )

    fieldsets = (
        (
            "Objeto y lugar",
            {
                "fields": (
                    "lugar",
                    "tipo_de_objeto",
                )
            },
        ),
        (
            "Cantidades y cálculo",
            {
                "fields": (
                    "cantidad",
                    "cantidad_buena_admin",
                    "cantidad_mala",
                    "cantidad_pendiente",
                    "minimo_operativo",
                    "importancia",
                    "operatividad_objeto_admin",
                    "estado_calculado_admin",
                )
            },
        ),
        (
            "Detalle",
            {
                "fields": (
                    "detalle",
                    "fecha",
                )
            },
        ),
    )

    date_hierarchy = "fecha"

    @admin.display(description="Objeto")
    def objeto_admin(self, obj):
        return obj.tipo_de_objeto.objeto.nombre_del_objeto

    @admin.display(description="Buenas")
    def cantidad_buena_admin(self, obj):
        return obj.cantidad_buena

    @admin.display(description="Importancia")
    def importancia_admin(self, obj):
        return obj.get_importancia_display()

    @admin.display(description="Operatividad")
    def operatividad_objeto_admin(self, obj):
        return f"{obj.operatividad_objeto}%"

    @admin.display(description="Condición")
    def estado_calculado_admin(self, obj):
        if obj.estado == "B":
            return "Todo bueno"
        if obj.estado == "P":
            return "Con pendientes"
        return "Con unidades malas"


# =====================================================
# ADMIN INDIVIDUAL: HISTÓRICO
# =====================================================
class HistoricoObjetoAdminForm(forms.ModelForm):
    importancia_anterior = forms.TypedChoiceField(
        label="Importancia anterior",
        required=True,
        coerce=int,
        choices=(
            (1, "Baja"),
            (2, "Media"),
            (3, "Alta / Crítica"),
        ),
        widget=forms.Select,
    )
    estado_anterior = forms.ChoiceField(
        label="Condición anterior",
        required=True,
        choices=(
            ("B", "Todo bueno"),
            ("P", "Con pendientes"),
            ("M", "Con unidades malas"),
        ),
        widget=forms.Select,
    )

    class Meta:
        model = HistoricoObjeto
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()

        cantidad = cleaned.get("cantidad_anterior") or 0
        cantidad_mala = cleaned.get("cantidad_mala_anterior") or 0
        cantidad_pendiente = cleaned.get("cantidad_pendiente_anterior") or 0
        minimo_operativo = cleaned.get("minimo_operativo_anterior") or 1

        if cantidad <= 0:
            raise forms.ValidationError("La cantidad anterior debe ser mayor a 0.")

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise forms.ValidationError(
                "La suma de unidades malas y pendientes no puede superar la cantidad total."
            )

        if minimo_operativo > cantidad:
            raise forms.ValidationError(
                "El mínimo operativo no puede ser mayor que la cantidad total."
            )

        return cleaned
class HistoricoObjetoAdmin(admin.ModelAdmin):
    form = HistoricoObjetoAdminForm

    fieldsets = (
        (
            "Objeto asociado",
            {
                "fields": (
                    "objeto_del_lugar",
                )
            },
        ),
        (
            "Unidades anteriores",
            {
                "fields": (
                    "cantidad_anterior",
                    "cantidad_mala_anterior",
                    "cantidad_pendiente_anterior",
                    "minimo_operativo_anterior",
                )
            },
        ),
        (
            "Condición anterior",
            {
                "fields": (
                    "importancia_anterior",
                    "estado_anterior",
                    "detalle_anterior",
                    "fecha_anterior",
                )
            },
        ),
    )

    list_display = (
        "objeto_admin",
        "lugar_admin",
        "cantidad_anterior",
        "cantidad_mala_anterior",
        "cantidad_pendiente_anterior",
        "minimo_operativo_anterior",
        "importancia_anterior_admin",
        "estado_anterior_admin",
        "fecha_anterior",
    )

    list_filter = (
        "estado_anterior",
        "importancia_anterior",
        "fecha_anterior",
        "objeto_del_lugar__lugar__piso__ubicacion__sector",
        "objeto_del_lugar__lugar__piso__ubicacion",
    )

    search_fields = (
        "objeto_del_lugar__tipo_de_objeto__objeto__nombre_del_objeto",
        "objeto_del_lugar__tipo_de_objeto__marca",
        "objeto_del_lugar__tipo_de_objeto__material",
        "objeto_del_lugar__lugar__nombre_del_lugar",
        "detalle_anterior",
    )

    autocomplete_fields = (
        "objeto_del_lugar",
    )

    date_hierarchy = "fecha_anterior"

    @admin.display(description="Objeto")
    def objeto_admin(self, obj):
        return obj.objeto_del_lugar.tipo_de_objeto.objeto.nombre_del_objeto

    @admin.display(description="Lugar")
    def lugar_admin(self, obj):
        return obj.objeto_del_lugar.lugar

    @admin.display(description="Importancia anterior")
    def importancia_anterior_admin(self, obj):
        return texto_importancia(obj.importancia_anterior)

    @admin.display(description="Condición anterior")
    def estado_anterior_admin(self, obj):
        if obj.estado_anterior == "B":
            return "Todo bueno"
        if obj.estado_anterior == "P":
            return "Con pendientes"
        return "Con unidades malas"


# =====================================================
# ADMIN MAPA
# =====================================================

class AreaMapaAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "tipo",
        "sector",
        "ubicacion",
        "creado_por",
        "creado",
        "actualizado",
    )

    list_filter = (
        "tipo",
        "sector",
        "ubicacion",
        "creado",
    )

    search_fields = (
        "nombre",
        "sector__sector",
        "ubicacion__ubicacion",
    )

    readonly_fields = (
        "creado",
        "actualizado",
    )


# =====================================================
# REGISTROS
# =====================================================

admin.site.register(Sector, SectorAdmin)
admin.site.register(Ubicacion, UbicacionAdmin)
admin.site.register(Piso, PisoAdmin)
admin.site.register(TipoLugar, TipoLugarAdmin)
admin.site.register(Lugar, LugarAdmin)

admin.site.register(CategoriaObjeto, CategoriaObjetoAdmin)
admin.site.register(Objeto, ObjetoAdmin)
admin.site.register(TipoObjeto, TipoObjetoAdmin)
admin.site.register(TipoLugarObjetoTipico)

admin.site.register(ObjetoLugar, ObjetoLugarAdmin)
admin.site.register(HistoricoObjeto, HistoricoObjetoAdmin)

admin.site.register(AreaMapa, AreaMapaAdmin)