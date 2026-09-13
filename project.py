from flask import Flask, render_template, request, redirect, url_for, flash
from base import Product, Order, add_new_product, create_order, delete_all_products, get_all_products, get_product_by_id
from werkzeug.utils import secure_filename
from pydantic import ValidationError
import os
import shutil

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


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        product_id = request.form.get("product_id")

        if not email or not phone_number or not product_id:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("add_product"))

        try:
            create_order(email=email, phone_number=int(phone_number), product_id=int(product_id))
            flash("Order created successfully!", "success")
            return redirect(url_for("products_handler"))
        except Exception as e:
            flash(f"Error creating order: {e}", "danger")
            return redirect(url_for("add_product"))

    selected_id = request.args.get("product_id", type=int)
    products = get_all_products()
    return render_template("add_product.html", products=products, selected_id=selected_id)


@app.route("/add_new_product", methods=["GET"])
def add_new_product_page():
    return render_template("add_new_product.html")


@app.route("/add_new_product/", methods=["POST"])
def add_new_product_route():
    image = request.files.get("image")
    if not image or image.filename == "" or not allowed_file(image.filename):
        flash("Invalid image file. Allowed formats: PNG, JPG, JPEG", "danger")
        return redirect(url_for("add_new_product_page"))

    filename = secure_filename(image.filename)

    try:
        image.save(os.path.join(FILE_PATH, filename))
        add_new_product(
            name=request.form.get("name"),
            description=request.form.get("description"),
            price=float(request.form.get("price")),
            image_filename=f"img/{filename}",
        )
        flash("New product added successfully!", "success")
        return redirect(url_for("products_handler"))
    except ValidationError as e:
        flash(str(e), "danger")
        return redirect(url_for("add_new_product_page"))
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("add_new_product_page"))


if __name__ == "__main__":
    app.run(debug=True)