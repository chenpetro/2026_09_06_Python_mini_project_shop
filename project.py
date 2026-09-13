from flask import Flask, render_template, request, redirect, url_for, flash
from base import Product, Order, add_new_product, create_order, delete_all_products, get_all_products, get_product_by_id, get_all_orders
from werkzeug.utils import secure_filename
from pydantic import ValidationError
import os
import shutil
import magic

mime = magic.Magic(mime=True)

FILE_PATH = os.path.join(os.getcwd(), "static", "img")
os.makedirs(FILE_PATH, exist_ok=True)

# Sync existing img folder to static/img if present
ROOT_IMG_PATH = os.path.join(os.getcwd(), "img")
if os.path.exists(ROOT_IMG_PATH):
    for f in os.listdir(ROOT_IMG_PATH):
        src = os.path.join(ROOT_IMG_PATH, f)
        dst = os.path.join(FILE_PATH, f)
        if os.path.isfile(src) and not os.path.exists(dst):
            shutil.copy(src, dst)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "default-fallback-key") 


@app.route("/")
def main_handler():
    return render_template("main.html")


@app.route("/products")
def products_handler():
    products = get_all_products()
    return render_template("products.html", products=products)


@app.route("/orders")
def orders_handler():
    orders = get_all_orders()
    return render_template("orders.html", orders=orders)


@app.route("/make_order", methods=["GET", "POST"])
def make_order():
    if request.method == "POST":
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        product_id = request.form.get("product_id")

        if not email or not phone_number or not product_id:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("make_order"))

        try:
            create_order(email=email, phone_number=int(phone_number), product_id=int(product_id))
            flash("Order created successfully!", "success")
            return redirect(url_for("products_handler"))
        except Exception as e:
            flash(f"Error creating order: {e}", "danger")
            return redirect(url_for("make_order"))

    selected_id = request.args.get("product_id", type=int)
    products = get_all_products()
    return render_template("make_order.html", products=products, selected_id=selected_id)


@app.route("/add_new_product", methods=["GET"])
def add_new_product_page():
    return render_template("add_new_product.html")


@app.route("/add_new_product/", methods=["POST"])
def add_new_product_route():
    image = request.files.get("image")
    if not image or image.filename == "":
        return "No file", 400

    image_type = mime.from_buffer(image.read(1024))
    image.seek(0)

    if image_type not in ["image/png", "image/jpeg", "image/jpg"]:
        return "Wrong image type"

    if image.content_length and image.content_length > 10 * 1024 ** 2:
        return "File size reached allowed limit."

    image_name = secure_filename(image.filename)
    if not image_name:
        return "Wrong image filename"

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    image_path = os.path.join(FILE_PATH, image_name)
    image.save(image_path)

    # Додавання в базу даних
    try:
        add_new_product(
            name=name,
            description=description,
            price=float(price),
            image_filename=f"img/{image_name}",
        )
    except Exception as e:
        return f"Database error: {e}", 500

    return redirect(url_for("main_handler"))


if __name__ == "__main__":
    app.run(debug=True)