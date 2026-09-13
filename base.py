from sqlalchemy import create_engine, String, Float, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship, sessionmaker, DeclarativeBase, joinedload

from pydantic import ValidationError


PG_USER = "postgres"
PG_PASSWORD = "Tesla31!"
PG_DBNAME = "onlineshop"
engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@localhost:5432/{PG_DBNAME}", echo=False)

SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    def create_db(self):
        Base.metadata.create_all(engine)

    def drop_db(self):
        Base.metadata.drop_all(engine)

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    phone_number: Mapped[int] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(String(20), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    product: Mapped["Product"] = relationship("Product", back_populates="order")

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    image_filename: Mapped[str] = mapped_column(String(1000), nullable=False)
    order: Mapped[list["Order"]] = relationship("Order", back_populates="product")

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(20), nullable=False)
    password: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False)


def init_db():
    base = Base()
    base.create_db()
    main()


def main():
    with SessionLocal() as session:
        try:
            if session.query(Product).count() > 0:
                return

            products = [
                Product(name="Nike Air Max", description="Класичні кросівки для бігу", price=4300,
                        image_filename="img/nike_air_max.png"),
                Product(name="Adidas Ultraboost", description="Легкі та комфортні кросівки", price=3100,
                        image_filename="/img/adidas_ultrboost.png"),
                Product(name="Puma RS-X", description="Стильні кросівки для міста", price=3750,
                        image_filename="img/puma_rsx.png")
            ]

            session.add_all(products)
            session.commit()

        except Exception as e:
            session.rollback()
            print(f"Error seeding database: {e}")


def create_order(email, phone_number, product_id):
    with SessionLocal() as session:
        new_order = Order(email=email, phone_number=phone_number, product_id=product_id)
        session.add(new_order)
        session.commit()


def add_new_product(name, description, price, image_filename):
    with SessionLocal() as session:
        new_product = Product(name=name, description=description, price=price, image_filename=image_filename)
        session.add(new_product)
        session.commit()


def delete_all_products():
    with SessionLocal() as session:
        session.query(Product).delete()
        session.commit()

def get_all_products():
    with SessionLocal() as session:
        try:
            all_products = session.query(Product).all()
            return all_products
        except Exception as e:
            print(f"Error fetching products: {e}")
            return []

def get_product_by_id(id):
    with SessionLocal() as session:
        return session.get(Product, id)


def get_all_orders():
    with SessionLocal() as session:
        try:
            return session.query(Order).options(joinedload(Order.product)).all()
        except Exception as e:
            print(f"Error fetching orders: {e}")
            return []


init_db()

if __name__ == "__main__":
    main()