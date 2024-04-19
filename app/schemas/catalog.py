from decimal import Decimal

from pydantic import BaseModel, validator

# from app.schemas.types import ItemQuanity


class Option(BaseModel):
    id: int
    name: str


class OptionValue(BaseModel):
    id: int
    option_id: int
    value: str


class PriceInfo(BaseModel):
    subtotal: float
    delivery_price: float | None = None


class CatalogItem(BaseModel):
    id: int
    item_name: str
    item_description: str | None = None
    item_category: str | None = None
    options: list[Option]
    price_map: list[tuple[PriceInfo, list[OptionValue]]]

    @validator("price_map")
    def validate_price_map(cls, price_map, values):
        options = values.get("options")
        if options is None:
            raise ValueError("Options must be defined before validating price_map")

        option_ids = {option.id for option in options}

        for price_info, option_values in price_map:
            for option_value in option_values:
                if option_value.option_id not in option_ids:
                    raise ValueError(
                        f'Option value {option_value.id} does not correspond to any option in "options"'
                    )

            option_value_ids = {
                option_value.option_id for option_value in option_values
            }
            if len(option_value_ids) != len(options):
                raise ValueError(
                    "Each option must have exactly one option value in the price map"
                )

        return price_map


class Catalog(BaseModel):
    id: int
    catalog_name: str
    items: list[CatalogItem]

    def get_item_by_id(self, item_id: int) -> CatalogItem | None:
        for item in self.items:
            if item.id == item_id:
                return item
        return None


# Create options
size_option = Option(id=1, name="Tamaño")
quantity_option = Option(id=2, name="Piezas")

# Create option values
size_21_5x14_cm = OptionValue(id=1, option_id=1, value="21.5 x 14 cm")
quantity_1000 = OptionValue(id=2, option_id=2, value="1000")
quantity_2000 = OptionValue(id=3, option_id=2, value="2000")
quantity_3000 = OptionValue(id=4, option_id=2, value="3000")
quantity_4000 = OptionValue(id=5, option_id=2, value="4000")
quantity_5000 = OptionValue(id=6, option_id=2, value="5000")

# Create the catalog item
RECETAS_ECONOMICAS_CATALOG_ITEM = CatalogItem(
    id=1,
    item_name="Recetas Medicas Económicas",
    item_description="""Si eres Médico ahora puedes imprimir tus recetas médicas en una forma muy sencilla y económica. Selecciona algunos de nuestros diseños de recetas médicas que tenemos y personalizalos con toda tu información sin ningún costo!

- Impresión a 1 tinta color azul en Papel Bond de 90g

- Terminado en blocks de 50 recetas.

""",
    item_category="Medical Forms",
    options=[size_option, quantity_option],
    price_map=[
        (
            PriceInfo(subtotal=1590.00, delivery_price=280.00),
            [size_21_5x14_cm, quantity_1000],
        ),
        (
            PriceInfo(subtotal=1850.00, delivery_price=390.00),
            [size_21_5x14_cm, quantity_2000],
        ),
        (
            PriceInfo(subtotal=2090.00, delivery_price=780.00),
            [size_21_5x14_cm, quantity_3000],
        ),
        (
            PriceInfo(subtotal=2350.00, delivery_price=780.00),
            [size_21_5x14_cm, quantity_4000],
        ),
        (
            PriceInfo(subtotal=2610.00, delivery_price=780.00),
            [size_21_5x14_cm, quantity_5000],
        ),
    ],
)


CATALOG_PIXZ = Catalog(
    id=1, catalog_name="pixz", items=[RECETAS_ECONOMICAS_CATALOG_ITEM]
)


# pan_con_semillas = CatalogItem(
#     id=1, item_name="Pan con Semillas", item_price=Decimal("160"), item_category="1kg"
# )
# pan_rustico = CatalogItem(
#     id=2, item_name="Pan Rústico", item_price=Decimal("150"), item_category="1kg"
# )
# pan_campestre = CatalogItem(
#     id=3, item_name="Pan Campestre", item_price=Decimal("145"), item_category="1kg"
# )
# pan_de_centeno = CatalogItem(
#     id=4, item_name="Pan de Centeno", item_price=Decimal("180"), item_category="1kg"
# )
# pan_brioche = CatalogItem(
#     id=5, item_name="Pan Brioche", item_price=Decimal("180"), item_category="½ kg"
# )
# pan_brioche_con_hierbas = CatalogItem(
#     id=6,
#     item_name="Pan Brioche con hierbas",
#     item_price=Decimal("190"),
#     item_category="½ kg",
# )
# bollo_brioche_hamburguesa = CatalogItem(
#     id=7,
#     item_name="Bollo Brioche para hamburguesa p/pieza chico",
#     item_price=Decimal("12"),
#     item_category="gde 20.-",
# )
# mini_focaccia = CatalogItem(
#     id=8,
#     item_name="Mini focaccia individual c/romero y sal de grano",
#     item_price=Decimal("45"),
# )
# pan_dátil_nuez = CatalogItem(
#     id=9, item_name="Pan con dátil y nuez ½ kg", item_price=Decimal("145")
# )
# pan_arándano_nuez = CatalogItem(
#     id=10, item_name="Pan con arándano y nuez ½ kg", item_price=Decimal("145")
# )
# pan_higo_turco = CatalogItem(
#     id=11, item_name="Pan con higo turco ½ kg", item_price=Decimal("145")
# )
# cafe_especialidad = CatalogItem(
#     id=12,
#     item_name="1 kg de café de especialidad de Chiapas mezcla y tostado para",
#     item_description="Prolecto Bullé en grano o molido",
#     item_price=Decimal("480"),
# )

# # Create the Catalog instance
# bulle_pan_y_cafe = Catalog(
#     id=1,
#     catalog_name="BULLÉ PAN Y CAFÉ",
#     items=[
#         pan_con_semillas,
#         pan_rustico,
#         pan_campestre,
#         pan_de_centeno,
#         pan_brioche,
#         pan_brioche_con_hierbas,
#         bollo_brioche_hamburguesa,
#         mini_focaccia,
#         pan_dátil_nuez,
#         pan_arándano_nuez,
#         pan_higo_turco,
#         cafe_especialidad,
#     ],
# )
