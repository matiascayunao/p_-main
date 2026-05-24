from django.contrib import admin
import nested_admin
from .models import Ubicacion, TipoLugar, TipoObjeto, Lugar, Objeto, ObjetoLugar, CategoriaObjeto,HistoricoObjeto, Sector, Piso



class HistoricoObjetoInline(nested_admin.NestedTabularInline):
    model = HistoricoObjeto
    extra = 0
class ObjetoLugarInline(nested_admin.NestedTabularInline):
    model = ObjetoLugar
    extra = 0
    inlines = [HistoricoObjetoInline]

class LugarInline(nested_admin.NestedStackedInline):
    model = Lugar
    extra = 0
    inlines= [ObjetoLugarInline]

class PisoInline(nested_admin.NestedStackedInline):
    model = Piso
    extra = 0
    inlines=[LugarInline]

class UbicacionInline(nested_admin.NestedStackedInline):
    model = Ubicacion
    extra = 0
    inlines = [PisoInline]


class SectorAdmin(nested_admin.NestedModelAdmin):
    inlines = [UbicacionInline]    
    list_display = ("sector",)
    search_fields=("sector",)


class TipoObjetoInline(nested_admin.NestedTabularInline):
    model = TipoObjeto
    extra = 0

class ObjetoInline(nested_admin.NestedStackedInline):
    model = Objeto
    extra = 0
    inlines = [TipoObjetoInline]

class CategoriaObjetoAdmin(nested_admin.NestedModelAdmin):
    inlines = [ObjetoInline]
    list_display= ("nombre_de_categoria",)
    search_fields=("nombre_de_categoria",)


admin.site.register(Sector, SectorAdmin)

admin.site.register(CategoriaObjeto, CategoriaObjetoAdmin)

admin.site.register(Ubicacion)
admin.site.register(TipoLugar)
admin.site.register(Lugar)
admin.site.register(Piso)
admin.site.register(Objeto)
admin.site.register(TipoObjeto)
admin.site.register(ObjetoLugar)
admin.site.register(HistoricoObjeto)