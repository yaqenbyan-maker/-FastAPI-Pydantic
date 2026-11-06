# تقرير تحليلي وتوثيقي لتطبيق إداراة المنتجات (FastAPI & SQLite)

---

## 1. المقدمة (Overview)
يقوم هذا الكود بإنشاء واجهة برمجة تطبيقات مستقرة (RESTful API) باستخدام إطار العمل **FastAPI** وقاعدة بيانات **SQLite3** للتحكم في المنتجات وإدارتها (إضافة منتج جديد، وحلب قائمة المنتجات المخزنة).

---

## 2. المكونات والتقنيات المستخدمة (Tech Stack)

* **Python**: اللغة الأساسية للمشروع.
* **FastAPI**: إطار عمل سريع لبناء واجهات برمجية RESTful APIs عالية الأداء.
* **Pydantic**: للتحقق من صحة البيانات (Data Validation) وتحديد نصوص الإدخال المتوقعة.
* **SQLite3**: قاعدة بيانات علاقات خفيفة ومحليّة لتخزين البيانات.

---

## 3. التحليل التفصيلي لمكونات الكود (Detailed Code Breakdown)

### أ. تهيئة واستدعاء المكتبات (Imports & Initialization)
```python
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()
```
* تم استدعاء `sqlite3` للتعامل مع قاعدة البيانات.
* تم إنشاء كائن التطبيق الأساسي `app` بواسطة `FastAPI()`.
* استدعاء `BaseModel` و `Field` للتحقق من صحة المدخلات.

---

### ب. تهيئة قاعدة البيانات (`init_db`)
```python
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

init_db()
```
* **الوظيفة:** تقوم الدالة بإنشاء ملف قاعدة البيانات `database.db` وجدول باسم `products` إذا لم يكن موجوداً من قبل (`IF NOT EXISTS`).
* **الحقول والتفاصيل:**
  * `id`: معرّف فريد للمنتج يتزايد تلقائياً (`INTEGER PRIMARY KEY AUTOINCREMENT`).
  * `name`: اسم المنتج (نص لا يمكن أن يكون فارغاً `TEXT NOT NULL`).
  * `price`: سعر المنتج (عدد حقيقي `REAL NOT NULL`).
  * `quantity`: كمية المنتج المخزنة (عدد صحيح `INTEGER NOT NULL`).

---

### ج. هيكل التحقق من البيانات (Pydantic Schema)
```python
class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="اسم المنتج لا يمكن أن يكون فارغاً")
    price: float = Field(..., gt=0, description="السعر يجب أن يكون أكبر من صفر")
    quantity: int = Field(..., ge=0, description="الكمية يجب أن تكون 0 أو أكثر")
```
يضمن هذا النموذج عدم قبول بيانات خاطئة أو غير مقبولة:
1. **`name`**: يجب أن يكون نصاً بطول لا يقل عن حرف واحد (`min_length=1`).
2. **`price`**: يجب أن يكون رقماً بعلامة عشرية وأكبر تماماً من الصفر (`gt=0` وتعني *Greater Than*).
3. **`quantity`**: يجب أن تكون رقماً صحيحاً وأكبر من أو تساوي الصفر (`ge=0` وتعني *Greater than or Equal to*).

---

### د. نقطة النهاية لإضافة منتج جديد (`POST /products`)
```python
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
```
* **نوع الطلب:** `POST` على المسار `/products`.
* **رمز الاستجابة النجاح (Status Code):** `201 Created`.
* **آلية العمل:** 
  1. استقبال كائن من نوع `ProductCreate`.
  2. إدخال السجل في قاعدة البيانات باستخدام استعلام مسبق التجهيز (Prepared Statement) لمنع ثغرات `SQL Injection`.
  3. استخراج المعرف الجديد بواسطة `cursor.lastrowid`.
  4. إعادة المنتج المضاف شاملاً الـ `id`.

---

### هـ. نقطة النهاية لاسترجاع المنتجات (`GET /products`)
```python
@app.get("/products")
def get_products():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, price, quantity FROM products")
    rows = cursor.fetchall()
    conn.close()
    
    products = [
        {"id": row[0], "name": row[1], "price": row[2], "quantity": row[3]}
        for row in rows
    ]
    
    return products
```
* **نوع الطلب:** `GET` على المسار `/products`.
* **آلية العمل:**
  1. تنفيذ استعلام جلب لكافة المنتجات.
  2. تحويل النتائج (المكونة من صفوف tuples) إلى قائمة قواميس (List of Dicts) متوافقة مع صيغة `JSON`.
  3. إرجاع قائمة المنتجات للمستخدم.

---

## 4. نقاط القوة في الكود (Strengths)

1. **التحقق من البيانات (Validation):** استخدام Pydantic يمنع تماماً تخزين بيانات خاطئة (مثل سعر بالسالب أو كمية غير صحيحة).
2. **الأمان (Security):** استخدام الرُموز المستعارة `?` في استعلامات SQL يحمي من هجمات حقن SQL.
3. **وضوح البنية والتوثيق:** الكود منظم، واضح ومرفق بتعليقات تشرح عمل كل جزء بشكل كافٍ.
4. **التوثيق التلقائي:** توفير توثيق تلاؤمي تلقائي من خلال OpenAPI في FastAPI عبر المسارات `/docs` و `/redoc`.

---

## 5. مقترحات للتحسين والتطوير (Recommendations)

* **استخدام الاتصال مع المولدات (Yield / Dependency Injection):** فتح الاتصال وإغلاقه يدوياً في كل دالة يمكن استبداله بـ FastAPI Dependencies لإدارة الاتصال بشكل أكفأ.
* **دعم العمليات غير المتزامنة (Async):** لأن `sqlite3` مكتبة تزامن Blocking، يمكن تحسين الأداء عند زيادة استخدام التطبيق بالانتقال إلى مكتبة مثل `databases` أو `aiosqlite`.
* **معالجة الأخطاء (Error Handling):** استخدام `try...except...finally` لضمان إغلاق الاتصال بقاعدة البيانات دائماً حتى في حال حدوث خطأ أثناء تنفيذ الاستعلام.
```

لقد أنشأت التقرير المرتكز على الكود بأسلوب Markdown منظم وشامل يشرح كل جزء ومميزاته مع توصيات للتحسين. هل هناك نقاط إضافية تود التوسع فيها؟