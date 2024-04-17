from decimal import Decimal

from pydantic import BaseModel


class CatalogItem(BaseModel):
    id: int
    item_name: str
    item_description: str | None = None
    item_price: Decimal
    item_category: str | None = None


class Catalog(BaseModel):
    id: int
    catalog_name: str
    items: list[CatalogItem]


pan_con_semillas = CatalogItem(
    id=1, item_name="Pan con Semillas", item_price=Decimal("160"), item_category="1kg"
)
pan_rustico = CatalogItem(
    id=2, item_name="Pan Rústico", item_price=Decimal("150"), item_category="1kg"
)
pan_campestre = CatalogItem(
    id=3, item_name="Pan Campestre", item_price=Decimal("145"), item_category="1kg"
)
pan_de_centeno = CatalogItem(
    id=4, item_name="Pan de Centeno", item_price=Decimal("180"), item_category="1kg"
)
pan_brioche = CatalogItem(
    id=5, item_name="Pan Brioche", item_price=Decimal("180"), item_category="½ kg"
)
pan_brioche_con_hierbas = CatalogItem(
    id=6,
    item_name="Pan Brioche con hierbas",
    item_price=Decimal("190"),
    item_category="½ kg",
)
bollo_brioche_hamburguesa = CatalogItem(
    id=7,
    item_name="Bollo Brioche para hamburguesa p/pieza chico",
    item_price=Decimal("12"),
    item_category="gde 20.-",
)
mini_focaccia = CatalogItem(
    id=8,
    item_name="Mini focaccia individual c/romero y sal de grano",
    item_price=Decimal("45"),
)
pan_dátil_nuez = CatalogItem(
    id=9, item_name="Pan con dátil y nuez ½ kg", item_price=Decimal("145")
)
pan_arándano_nuez = CatalogItem(
    id=10, item_name="Pan con arándano y nuez ½ kg", item_price=Decimal("145")
)
pan_higo_turco = CatalogItem(
    id=11, item_name="Pan con higo turco ½ kg", item_price=Decimal("145")
)
cafe_especialidad = CatalogItem(
    id=12,
    item_name="1 kg de café de especialidad de Chiapas mezcla y tostado para",
    item_description="Prolecto Bullé en grano o molido",
    item_price=Decimal("480"),
)

# Create the Catalog instance
bulle_pan_y_cafe = Catalog(
    id=1,
    catalog_name="BULLÉ PAN Y CAFÉ",
    items=[
        pan_con_semillas,
        pan_rustico,
        pan_campestre,
        pan_de_centeno,
        pan_brioche,
        pan_brioche_con_hierbas,
        bollo_brioche_hamburguesa,
        mini_focaccia,
        pan_dátil_nuez,
        pan_arándano_nuez,
        pan_higo_turco,
        cafe_especialidad,
    ],
)
