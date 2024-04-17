from langchain_core.pydantic_v1 import BaseModel, Field

from app.schemas.catalogs import bulle_pan_y_cafe

product_names = [x.item_name for x in bulle_pan_y_cafe.items]
product_names_str = ", ".join(product_names)


# Note that the docstrings here are crucial, as they will be passed along
# to the model along with the class name.
class GetProductInfo(BaseModel):
    f"""Fetch information about a product. Possible Products are: {product_names_str}"""

    product_name: str = Field(..., description="The product name")


TOOLS = [GetProductInfo]
