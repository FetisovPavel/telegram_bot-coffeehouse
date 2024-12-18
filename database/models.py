from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    role = Column(String)
    tg_user_id = Column(String)
    name = Column(String)
    contact_info = Column(String)
    loyalty_points = Column(Integer)
    account_status = Column(String)
    state = Column(String)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String)
    total_price = Column(Integer)
    order_date = Column(DateTime, server_default=func.now())
    pickup_location = Column(String)
    payment_method = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="orders")


class OrderItem(Base):
    __tablename__ = 'order_items'

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)  # Первичный ключ
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)  # Внешний ключ на заказ
    menu_item_id = Column(String, ForeignKey('menu_items.id'), nullable=False)  # Внешний ключ на пункт меню
    quantity = Column(Integer, nullable=False)  # Количество добавленного товара

    # Отношения
    order = relationship("Order", back_populates="order_items")  # Связь с таблицей заказов
    menu_item = relationship("MenuItem", back_populates="order_items")  # Связь с таблицей пунктов меню


class MenuItem(Base):
    __tablename__ = 'menu_items'

    id = Column(String, primary_key=True)  # Уникальный идентификатор пункта меню
    name = Column(String, nullable=False)  # Название пункта меню
    description = Column(String, nullable=False)  # Описание пункта меню
    image = Column(String, nullable=False)  # URL изображения

    variants = relationship("Variant", back_populates="menu_item", cascade="all, delete-orphan")


class Variant(Base):
    __tablename__ = 'variants'

    id = Column(String, primary_key=True)  # Уникальный идентификатор варианта
    menu_item_id = Column(String, ForeignKey('menu_items.id'), nullable=False)  # Внешний ключ на таблицу MenuItems
    name = Column(String, nullable=False)  # Название варианта (например, "Small")
    cost = Column(Integer, nullable=False)  # Цена варианта
    weight = Column(String, nullable=False)  # Вес варианта (например, "200g")

    menu_item = relationship("MenuItem", back_populates="variants")

