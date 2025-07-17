from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class Product(BaseModel):
    codigo: int
    name: str
    marca: str
    precio: int
    status: bool = True
      
products = [
    Product(codigo=1, name="Platano", marca="antioquia", precio=30, status=True),
    Product(codigo=2, name="Yuca", marca="medellin", precio=25, status=True),
    Product(codigo=3, name="Maiz", marca="cali", precio=25, status=True)
]

@router.get("/products")
async def get_products():
    return products


@router.get("/products/{codigo}")
async def get_product(codigo: int):
    product = next((p for p in products if p.codigo == codigo), None)
    if product:
        return product
    raise HTTPException(status_code=404, detail="Producto no encontrado")

@router.post("/products/")
async def create_product(product: Product):
    existing_product = next((p for p in products if p.codigo == product.codigo), None)
    if existing_product:
        raise HTTPException(status_code=400, detail="El producto ya existe")
    products.append(product)
    return {"message": "Producto creado exitosamente", "product": product}