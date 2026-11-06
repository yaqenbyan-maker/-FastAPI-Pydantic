import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

# ----------------------------------------------------
# 1. إنشاء قاعدة البيانات والجدول بالحقول المحددة
# ----------------------------------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# تشغيل دالة إنشاء قاعدة البيانات عند بدء التطبيق
init_db()


# ----------------------------------------------------
# 2. إنشاء نموذج Pydantic للتحقق من البيانات
# ----------------------------------------------------
class ProductCreate(BaseModel):
    # اسم المنتج غير فارغ
    name: str = Field(..., min_length=1, description="اسم المنتج لا يمكن أن يكون فارغاً")
    # السعر أكبر من صفر (gt = greater than)
    price: float = Field(..., gt=0, description="السعر يجب أن يكون أكبر من صفر")
    # الكمية عدد صحيح لا يقل عن صفر (ge = greater than or equal to)
    quantity: int = Field(..., ge=0, description="الكمية يجب أن تكون 0 أو أكثر")


# ----------------------------------------------------
# 3. إنشاء مسار POST /products لإضافة منتج جديد
# ----------------------------------------------------
@app.post("/products", status_code=201)
def create_product(product: ProductCreate):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
        (product.name, product.price, product.quantity)
    )
    
    product_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        "id": product_id,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity
    }


# ----------------------------------------------------
# 4. إنشاء مسار GET /products لعرض جميع المنتجات
# ----------------------------------------------------
@app.get("/products")
def get_products():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price, quantity FROM products")
    rows = cursor.fetchall()
    conn.close()
    
    # تحويل البيانات إلى قائمة من القواميس
    products = [
        {"id": row[0], "name": row[1], "price": row[2], "quantity": row[3]}
        for row in rows
    ]
    
    return products