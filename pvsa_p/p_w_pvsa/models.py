from django.db import models, transaction
from django.utils import timezone
from django.conf import settings


class Sector(models.Model):
    sector = models.CharField(max_length=100, unique=True)

    # NUEVO: polígono GeoJSON (Polygon)
    geom = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.sector


class Ubicacion(models.Model):
    ubicacion = models.CharField(max_length=100, unique=True)
    sector = models.ForeignKey(
        Sector,
        verbose_name="sector",
        on_delete=models.RESTRICT,
    )

    # NUEVO: polígono GeoJSON (Polygon)
    geom = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.ubicacion} | Sector: {self.sector.sector}"



class Piso(models.Model):
    piso = models.SmallIntegerField()
    ubicacion = models.ForeignKey(
        Ubicacion,
        verbose_name="ubicacion",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        # Piso + ubicación
        return f"Piso {self.piso} | {self.ubicacion.ubicacion}"


class TipoLugar(models.Model):
    tipo_de_lugar = models.CharField(max_length=100, unique=True)

    def __str__(self):
        # Nombre del tipo de lugar
        return self.tipo_de_lugar


class Lugar(models.Model):
    nombre_del_lugar = models.CharField(max_length=100)
    piso = models.ForeignKey(
        Piso,
        verbose_name="piso",
        on_delete=models.RESTRICT,
    )
    lugar_tipo_lugar = models.ForeignKey(
        TipoLugar,
        verbose_name="tipo de lugar",
        on_delete=models.RESTRICT,
    )

    geom = models.JSONField(null=True, blank=True)


    def __str__(self):
        # Nombre del lugar + piso + ubicación
        return (
            f"{self.nombre_del_lugar} | "
            f"Piso {self.piso.piso} | "
            f"{self.piso.ubicacion.ubicacion}"
        )

    @property
    def operatividad_lugar(self):
        """
        Calcula la operatividad general del lugar según sus objetos.

        La fórmula considera:
        - operatividad individual de cada objeto
        - importancia asignada por el administrador
        """

        objetos = list(self.objetos_lugar.all())

        if not objetos:
            return 100.0

        suma_ponderada = 0
        suma_importancias = 0

        for obj in objetos:
            importancia = obj.importancia or 1
            suma_ponderada += obj.operatividad_objeto * importancia
            suma_importancias += importancia

        if suma_importancias == 0:
            return 100.0

        return round(suma_ponderada / suma_importancias, 1)


class CategoriaObjeto(models.Model):
    nombre_de_categoria = models.CharField(
        max_length=100, verbose_name="categoría", unique=True
    )

    def __str__(self):
        # Solo el nombre de la categoría
        return self.nombre_de_categoria


class Objeto(models.Model):
    nombre_del_objeto = models.CharField(
        max_length=100, verbose_name="objeto", unique=True
    )
    objeto_categoria = models.ForeignKey(
        CategoriaObjeto,
        verbose_name="categoria",
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        # Objeto + categoría entre paréntesis
        return f"{self.nombre_del_objeto} ({self.objeto_categoria.nombre_de_categoria})"


class TipoObjeto(models.Model):
    objeto = models.ForeignKey(
        Objeto,
        verbose_name="objeto",
        on_delete=models.RESTRICT,
    )
    marca = models.CharField(max_length=100, verbose_name="marca", blank=True, null=True)
    material = models.CharField(max_length=100, verbose_name="material", blank=True, null=True)

    def __str__(self):
        marca_txt = (self.marca or "").strip()
        material_txt = (self.material or "").strip()
        return f"{self.objeto.nombre_del_objeto} - {marca_txt} {material_txt}".strip()

class TipoLugarObjetoTipico(models.Model):
    tipo_lugar = models.ForeignKey(
        TipoLugar,
        verbose_name="tipo de lugar",
        on_delete=models.CASCADE,
        related_name="tipicos",
    )
    tipo_objeto = models.ForeignKey(
        TipoObjeto,
        verbose_name="tipo de objeto",
        on_delete=models.CASCADE,
        related_name="tipico_en",
    )
    activo = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    importancia = models.PositiveSmallIntegerField(
        default=1,
        choices=(
            (1, "Baja"),
            (2, "Media"),
            (3, "Alta"),
        ),
    )

    class Meta:
        unique_together = ("tipo_lugar", "tipo_objeto")
        ordering = ("orden", "id")

    def __str__(self):
        return f"{self.tipo_lugar.tipo_de_lugar} -> {self.tipo_objeto}"



class ObjetoLugar(models.Model):
    ESTADO = (
        ("B", "Bueno"),
        ("P", "Pendiente"),
        ("M", "Malo"),
    )

    IMPORTANCIA = (
        (1, "Baja"),
        (2, "Media"),
        (3, "Alta / Crítica"),
    )

    cantidad = models.SmallIntegerField()
    estado = models.CharField(max_length=1, choices=ESTADO, default="B")
    detalle = models.CharField(max_length=200, blank=True)
    fecha = models.DateField(auto_now_add=True)

    importancia = models.PositiveSmallIntegerField(
        default=1,
        choices=IMPORTANCIA,
    )

    cantidad_mala = models.SmallIntegerField(default=0)
    cantidad_pendiente = models.SmallIntegerField(default=0)

    minimo_operativo = models.SmallIntegerField(
        default=1,
        help_text="Cantidad mínima que debe estar funcionando para considerar aceptable este objeto.",
    )

    lugar = models.ForeignKey(
        "Lugar",
        verbose_name="lugar",
        on_delete=models.RESTRICT,
        related_name="objetos_lugar",
        null=True,
        blank=True,
    )

    tipo_de_objeto = models.ForeignKey(
        "TipoObjeto",
        verbose_name="tipo de objeto",
        on_delete=models.RESTRICT,
        related_name="objetos_lugar",
        blank=True,
        null=True
    )

    def __str__(self):
        # Resumen corto: qué objeto es, dónde está y su estado/cantidad
        lugar_txt = (
            f"{self.lugar.nombre_del_lugar} | "
            f"Piso {self.lugar.piso.piso} | {self.lugar.piso.ubicacion.ubicacion}"
            if self.lugar
            else "Sin lugar asignado"
        )
        return (
            f"{self.tipo_de_objeto.objeto.nombre_del_objeto} "
            f"- {self.tipo_de_objeto.marca} {self.tipo_de_objeto.material or ''} "
            f"en {lugar_txt} "
            f"(cant. {self.cantidad}, estado {self.get_estado_display()})"
        )

    @property
    def cantidad_buena(self):
        cantidad = self.cantidad or 0
        malas = self.cantidad_mala or 0
        pendientes = self.cantidad_pendiente or 0

        buenas = cantidad - malas - pendientes

        if buenas < 0:
            return 0

        return buenas

    @property
    def unidades_funcionales_equivalentes(self):
        """
        Las unidades buenas valen 1.
        Las unidades pendientes valen 0.5.
        Las unidades malas valen 0.
        """

        cantidad = self.cantidad or 0
        malas = self.cantidad_mala or 0
        pendientes = self.cantidad_pendiente or 0

        equivalentes = cantidad - malas - (pendientes * 0.5)

        if equivalentes < 0:
            return 0

        return equivalentes

    @property
    def operatividad_objeto(self):
        """
        Calcula la operatividad del objeto usando una escala profesional:

        - Si está bajo el mínimo operativo, queda bajo el 50%.
        - Si cumple justo el mínimo operativo, queda en 50%.
        - Si supera el mínimo, sube progresivamente hasta 100%.
        """

        cantidad = self.cantidad or 0

        if cantidad <= 0:
            return 0.0

        minimo = self.minimo_operativo or 1

        if minimo < 1:
            minimo = 1

        if minimo > cantidad:
            minimo = cantidad

        funcionales = self.unidades_funcionales_equivalentes

        if funcionales <= 0:
            return 0.0

        if funcionales < minimo:
            resultado = (funcionales / minimo) * 50
            return round(resultado, 1)

        if cantidad == minimo:
            resultado = (funcionales / cantidad) * 100
            return round(resultado, 1)

        resultado = 50 + ((funcionales - minimo) / (cantidad - minimo)) * 50

        if resultado > 100:
            resultado = 100

        return round(resultado, 1)

    def actualizar_estado_automatico(self):
        """
        El estado queda derivado de las cantidades.
        No debería depender de que el usuario lo elija manualmente.
        """

        if (self.cantidad_mala or 0) > 0:
            self.estado = "M"
        elif (self.cantidad_pendiente or 0) > 0:
            self.estado = "P"
        else:
            self.estado = "B"

    def clean(self):
        from django.core.exceptions import ValidationError

        super().clean()

        cantidad = self.cantidad or 0
        cantidad_mala = self.cantidad_mala or 0
        cantidad_pendiente = self.cantidad_pendiente or 0
        minimo_operativo = self.minimo_operativo or 1

        if cantidad <= 0:
            raise ValidationError({
                "cantidad": "La cantidad debe ser mayor a 0."
            })

        if cantidad_mala < 0:
            raise ValidationError({
                "cantidad_mala": "La cantidad mala no puede ser negativa."
            })

        if cantidad_pendiente < 0:
            raise ValidationError({
                "cantidad_pendiente": "La cantidad pendiente no puede ser negativa."
            })

        if cantidad_mala + cantidad_pendiente > cantidad:
            raise ValidationError(
                "La suma de cantidad mala y cantidad pendiente no puede superar la cantidad total."
            )

        if minimo_operativo < 1:
            raise ValidationError({
                "minimo_operativo": "El mínimo operativo debe ser al menos 1."
            })

        if minimo_operativo > cantidad:
            raise ValidationError({
                "minimo_operativo": "El mínimo operativo no puede ser mayor que la cantidad total."
            })

    def save(self, *args, **kwargs):
        """
        Guarda histórico automático cuando cambia información relevante
        del objeto dentro del lugar.
        """

        self.actualizar_estado_automatico()
        self.full_clean()

        if self.pk:
            anterior = ObjetoLugar.objects.get(pk=self.pk)

            hubo_cambio = (
                anterior.cantidad != self.cantidad
                or anterior.estado != self.estado
                or (anterior.detalle or "") != (self.detalle or "")
                or anterior.importancia != self.importancia
                or anterior.cantidad_mala != self.cantidad_mala
                or anterior.cantidad_pendiente != self.cantidad_pendiente
                or anterior.minimo_operativo != self.minimo_operativo
            )

            if hubo_cambio:
                with transaction.atomic():
                    super().save(*args, **kwargs)

                    HistoricoObjeto.objects.create(
                        objeto_del_lugar=self,
                        cantidad_anterior=anterior.cantidad,
                        estado_anterior=anterior.estado,
                        detalle_anterior=anterior.detalle or "",
                        fecha_anterior=anterior.fecha,
                        importancia_anterior=anterior.importancia,
                        cantidad_mala_anterior=anterior.cantidad_mala,
                        cantidad_pendiente_anterior=anterior.cantidad_pendiente,
                        minimo_operativo_anterior=anterior.minimo_operativo,
                    )
                return

        super().save(*args, **kwargs)


class HistoricoObjeto(models.Model):
    # reutilizamos las mismas choices
    ESTADO = ObjetoLugar.ESTADO
    importancia_anterior = models.PositiveSmallIntegerField(default=1)
    cantidad_mala_anterior = models.SmallIntegerField(default=0)
    cantidad_pendiente_anterior = models.SmallIntegerField(default=0)
    minimo_operativo_anterior = models.SmallIntegerField(default=1)

    objeto_del_lugar = models.ForeignKey(
        ObjetoLugar,
        verbose_name="objeto del lugar",
        on_delete=models.CASCADE,
        related_name="historicoobjeto",
    )
    cantidad_anterior = models.SmallIntegerField()
    estado_anterior = models.CharField(max_length=1, choices=ESTADO)
    detalle_anterior = models.CharField(max_length=200, blank=True)
    fecha_anterior = models.DateField()

    def __str__(self):
        # Qué objeto es, dónde estaba y cuál era la situación anterior
        obj = self.objeto_del_lugar
        lugar_txt = (
            f"{obj.lugar.nombre_del_lugar} | "
            f"Piso {obj.lugar.piso.piso} | {obj.lugar.piso.ubicacion.ubicacion}"
            if obj.lugar
            else "Sin lugar asignado"
        )
        return (
            f"Histórico de {obj.tipo_de_objeto.objeto.nombre_del_objeto} "
            f"- {obj.tipo_de_objeto.marca} {obj.tipo_de_objeto.material or ''} "
            f"en {lugar_txt} "
            f"(cant. ant. {self.cantidad_anterior}, "
            f"estado ant. {self.get_estado_anterior_display()}, "
            f"fecha {self.fecha_anterior.strftime('%d/%m/%Y')})"
        )


class AreaMapa(models.Model):
    """
    Guarda un polígono (GeoJSON) asociado a un Sector o una Ubicación.
    No usa GIS/PostGIS: solo JSONField, funciona con SQLite.
    """
    TIPO = (
        ("S", "Sector"),
        ("U", "Ubicación"),
    )

    tipo = models.CharField(max_length=1, choices=TIPO)

    sector = models.ForeignKey(
        Sector,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="areas_mapa",
    )
    ubicacion = models.ForeignKey(
        Ubicacion,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="areas_mapa",
    )

    nombre = models.CharField(max_length=120)
    geometry = models.JSONField()  # GeoJSON Geometry (Polygon o MultiPolygon)

    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.nombre}"