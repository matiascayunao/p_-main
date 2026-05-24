from django.urls import path
from . import views

urlpatterns = [

    path("excel/sectores/",views.descargar_excel_sectores, name="descargar_excel_sectores"),
    # Auth
    path("", views.home, name="home"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.signout, name="signout"),

    # SECTOR
    path("sectores/", views.lista_sectores, name="lista_sectores"),
    path("sector/crear/", views.crear_sector, name="crear_sector"),
    path("sectores/<int:sector_id>/", views.detalle_sector, name="detalle_sector"),
    path("sectores/<int:sector_id>/editar/", views.editar_sector, name="editar_sector"),
    path("sectores/<int:sector_id>/borrar/", views.borrar_sector, name="borrar_sector"),

    # UBICACION
    path("ubicaciones/", views.lista_ubicaciones, name="lista_ubicaciones"),
    path("ubicacion/crear/", views.crear_ubicacion, name="crear_ubicacion"),
    path("ubicaciones/<int:ubicacion_id>/", views.detalle_ubicacion, name="detalle_ubicacion"),
    path("ubicaciones/<int:ubicacion_id>/editar/", views.editar_ubicacion, name="editar_ubicacion"),
    path("ubicaciones/<int:ubicacion_id>/borrar/", views.borrar_ubicacion, name="borrar_ubicacion"),

    # PISO
    path("pisos/", views.lista_pisos, name="lista_pisos"),
    path("piso/crear/", views.crear_piso, name="crear_piso"),
    path("pisos/<int:piso_id>/", views.detalle_piso, name="detalle_piso"),
    path("pisos/<int:piso_id>/editar/", views.editar_piso, name="editar_piso"),
    path("pisos/<int:piso_id>/borrar/", views.borrar_piso, name="borrar_piso"),

    # LUGAR
    path("lugares/", views.lista_lugares, name="lista_lugares"),
    path("lugar/crear/", views.crear_lugar, name="crear_lugar"),
    path("lugar/<int:lugar_id>/", views.detalle_lugar, name="detalle_lugar"),
    path("lugar/<int:lugar_id>/editar/", views.editar_lugar, name="editar_lugar"),
    path("lugar/<int:lugar_id>/borrar/", views.borrar_lugar, name="borrar_lugar"),

    # OBJETO DEL LUGAR
    path("objetos-lugar/", views.lista_objetos_lugar, name="lista_objetos_lugar"),
    path("objetos-lugar/<int:objeto_lugar_id>/", views.detalle_objeto_lugar, name="detalle_objeto_lugar"),
    path("objetos-lugar/<int:objeto_lugar_id>/editar/", views.editar_objeto_lugar, name="editar_objeto_lugar"),
    path("objetos-lugar/<int:objeto_lugar_id>/borrar/", views.borrar_objeto_lugar, name="borrar_objeto_lugar"),
    path("lugar/<int:lugar_id>/objeto/crear/", views.crear_objeto_lugar, name="crear_objeto_lugar"),

    # TIPO LUGAR
    path("tipo-lugar/", views.lista_tipos_lugar, name="lista_tipos_lugar"),
    path("tipo-lugar/crear/", views.crear_tipo_lugar, name="crear_tipo_lugar"),
    path("tipo-lugar/<int:tipo_lugar_id>/", views.detalle_tipo_lugar, name="detalle_tipo_lugar"),
    path("tipo-lugar/<int:tipo_lugar_id>/editar/", views.editar_tipo_lugar, name="editar_tipo_lugar"),
    path("tipo-lugar/<int:tipo_lugar_id>/borrar/", views.borrar_tipo_lugar, name="borrar_tipo_lugar"),

    # CATEGORIA
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categoria/crear/", views.crear_categoria_objeto, name="crear_categoria_objeto"),
    path("categoria/<int:categoria_id>/", views.detalle_categoria, name="detalle_categoria"),
    path("categoria/<int:categoria_id>/editar/", views.editar_categoria, name="editar_categoria"),
    path("categoria/<int:categoria_id>/borrar/", views.borrar_categoria, name="borrar_categoria"),

    # OBJETO
    path("objetos/", views.lista_objetos, name="lista_objetos"),
    path("objeto/crear/", views.crear_objeto, name="crear_objeto"),
    path("objeto/<int:objeto_id>/", views.detalle_objeto, name="detalle_objeto"),
    path("objeto/<int:objeto_id>/editar/", views.editar_objeto, name="editar_objeto"),
    path("objeto/<int:objeto_id>/borrar/", views.borrar_objeto, name="borrar_objeto"),

    # TIPO OBJETO
    path("tipos-objeto/", views.lista_tipos_objeto, name="lista_tipos_objeto"),
    path("tipo-objeto/crear/", views.crear_tipo_objeto, name="crear_tipo_objeto"),
    path("tipo-objeto/<int:tipo_objeto_id>/", views.detalle_tipo_objeto, name="detalle_tipo_objeto"),
    path("tipo-objeto/<int:tipo_objeto_id>/editar/", views.editar_tipo_objeto, name="editar_tipo_objeto"),
    path("tipo-objeto/<int:tipo_objeto_id>/borrar/", views.borrar_tipo_objeto, name="borrar_tipo_objeto"),

    # HISTORICO
    path("historicos/", views.lista_historicos, name="lista_historicos"),
    path("historico/", views.lista_historicos),  # alias para tu home actual
    path("historico/<int:historico_id>/", views.detalle_historico, name="detalle_historico"),
    path("historico/<int:historico_id>/editar/", views.editar_historico, name="editar_historico"),
    path("historico/<int:historico_id>/borrar/", views.borrar_historico, name="borrar_historico"),
    path("objetos-lugar/<int:objeto_lugar_id>/historico/crear/", views.crear_historico, name="crear_historico"),


    # ESTRUCTURA
    path("estructura/crear/", views.crear_estructura, name="crear_estructura"),

    # RESUMEN
    path("resumen/", views.resumen_general, name="resumen_general"),

    path("ajax/ubicaciones-por-sector/",views.ajax_ubicaciones_por_sector,name="ajax_ubicaciones_por_sector",),
    path("ajax/pisos-por-ubicacion/",views.ajax_pisos_por_ubicacion,name="ajax_pisos_por_ubicacion",),
    path("ajax/lugares-por-piso/",views.ajax_lugares_por_piso,name="ajax_lugares_por_piso",),
    path("ajax/objetos-por-categoria/",views.ajax_objetos_por_categoria,name="ajax_objetos_por_categoria",),
    path("ajax/tipos-por-objeto/",views.ajax_tipos_por_objeto,name="ajax_tipos_por_objeto",),

    path("api/objetos-tipicos/<int:tipo_lugar_pk>/", views.objetos_tipicos_por_tipo_lugar, name="objetos_tipicos_por_tipo_lugar"),


    # =========================
    # MAPA (ADMIN + EDITOR)
    # =========================
    path("mapa/", views.mapa_admin, name="mapa_admin"),
    path("mapa/stats/",views.mapa_admin_stats, name="mapa_admin_stats"),
    path("mapa/crear/", views.mapa_editor_crear, name="mapa_crear"),
    path("mapa/guardar/", views.mapa_guardar, name="mapa_guardar"),

    path("mapa/sector/<int:sector_id>/", views.mapa_sector_detalle, name="mapa_sector_detalle"),
    path("mapa/sector/<int:sector_id>/editar-geom/", views.mapa_sector_editar_geom, name="mapa_sector_editar_geom"),
    path("mapa/sector/<int:sector_id>/quitar-geom/", views.mapa_sector_quitar_geom, name="mapa_sector_quitar_geom"),

    path("mapa/ubicacion/<int:ubicacion_id>/", views.mapa_ubicacion_detalle, name="mapa_ubicacion_detalle"),
    path("mapa/ubicacion/<int:ubicacion_id>/editar-geom/", views.mapa_ubicacion_editar_geom, name="mapa_ubicacion_editar_geom"),
    path("mapa/ubicacion/<int:ubicacion_id>/quitar-geom/", views.mapa_ubicacion_quitar_geom, name="mapa_ubicacion_quitar_geom"),

    path("carga-masiva", views.carga_masiva, name="carga_masiva"),
    
    path("excel/plantilla-carga-masiva/", views.descargar_plantilla_carga_masiva, name="descargar_plantilla_carga_masiva"),

    path("mapa/lugar/<int:lugar_id>/editar/", views.mapa_lugar_editar_geom, name="mapa_lugar_editar_geom"),
    path("mapa/lugar/<int:lugar_id>/quitar/", views.mapa_lugar_quitar_geom, name="mapa_lugar_quitar_geom"),



]