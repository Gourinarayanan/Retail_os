"""
RetailWise AI — SQLAlchemy 2.0 ORM Models
Section 5 of full_flow.md — All models defined exactly as specified.
"""

from datetime import date, datetime
from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ── Base ──────────────────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    pass


# ── Products ──────────────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    # "staples" | "dairy" | "snacks" | "spices" | "beverages" | "cleaning" | "personal_care"
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    # "packet" | "kg" | "litre" | "piece" | "tray"
    unit_size: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    selling_price: Mapped[float] = mapped_column(Float, nullable=False)  # ₹ per unit
    cost_price: Mapped[float] = mapped_column(Float, nullable=False)     # ₹ per unit (average purchase price)

    # Ordering schedule
    order_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    # "daily" | "weekly" | "monthly"
    order_day: Mapped[str | None] = mapped_column(String(20), nullable=True)
    # Weekly: "Monday". Monthly: "1" (day of month). None for daily.
    reorder_point_days: Mapped[float] = mapped_column(Float, nullable=False, default=3.0)
    # Order when stock < X days of supply
    lead_time_days: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    # Days from order to arrival
    shelf_life_days: Mapped[int] = mapped_column(Integer, nullable=False, default=9999)
    # Max shelf life (9999 for non-perishable)

    # Minimum stock threshold
    min_threshold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Show warning when below this quantity

    # Scenario sensitivity: comma-separated event IDs this product responds to
    # e.g. "hartal_pre,onam,ramadan,rainy_day"
    demand_events: Mapped[str] = mapped_column(String(500), nullable=False, default="")

    avg_daily_demand: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Baseline units/day
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    inventory_batches: Mapped[list["InventoryBatch"]] = relationship(
        "InventoryBatch", back_populates="product", cascade="all, delete-orphan"
    )
    sales_records: Mapped[list["SalesRecord"]] = relationship(
        "SalesRecord", back_populates="product", cascade="all, delete-orphan"
    )
    supplier_prices: Mapped[list["SupplierPrice"]] = relationship(
        "SupplierPrice", back_populates="product", cascade="all, delete-orphan"
    )
    supplier_deliveries: Mapped[list["SupplierDelivery"]] = relationship(
        "SupplierDelivery", back_populates="product", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="product", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Product id={self.id} sku={self.sku!r} name={self.name!r} "
            f"category={self.category!r} unit={self.unit!r}>"
        )


# ── Inventory ─────────────────────────────────────────────────────────────────

class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False)
    # e.g. "BATCH-2024-001"
    quantity: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Current remaining quantity in units
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    # Per unit paid for this batch
    manufactured_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    # None for non-perishables
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    # "active" | "expiring_soon" | "expired" | "depleted"
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_batches")

    def __repr__(self) -> str:
        return (
            f"<InventoryBatch id={self.id} batch_number={self.batch_number!r} "
            f"product_id={self.product_id} qty={self.quantity} status={self.status!r}>"
        )


# ── Sales Records ─────────────────────────────────────────────────────────────

class SalesRecord(Base):
    __tablename__ = "sales_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity_sold: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    revenue: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    event_tag: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")
    # "onam" | "hartal_pre" | "hartal_day" | "eid" | "ramadan" | "vishu"
    # | "christmas" | "normal" | "rainy_day" | "weekend"

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="sales_records")

    def __repr__(self) -> str:
        return (
            f"<SalesRecord id={self.id} product_id={self.product_id} "
            f"date={self.date} qty_sold={self.quantity_sold} tag={self.event_tag!r}>"
        )


# ── Suppliers ─────────────────────────────────────────────────────────────────

class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    contact_name: Mapped[str] = mapped_column(String(100), nullable=False)
    whatsapp_number: Mapped[str] = mapped_column(String(20), nullable=False)
    # "+919876543210"
    email: Mapped[str | None] = mapped_column(String(200), nullable=True)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    supply_categories: Mapped[str] = mapped_column(String(500), nullable=False)
    # Comma-separated: "dairy,staples"
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relationships
    supplier_prices: Mapped[list["SupplierPrice"]] = relationship(
        "SupplierPrice", back_populates="supplier", cascade="all, delete-orphan"
    )
    supplier_deliveries: Mapped[list["SupplierDelivery"]] = relationship(
        "SupplierDelivery", back_populates="supplier", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="supplier", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Supplier id={self.id} name={self.name!r} "
            f"region={self.region!r} categories={self.supply_categories!r}>"
        )


# ── Supplier Prices ───────────────────────────────────────────────────────────

class SupplierPrice(Base):
    __tablename__ = "supplier_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    min_order_qty: Mapped[float | None] = mapped_column(Float, nullable=True)
    bulk_discount_qty: Mapped[float | None] = mapped_column(Float, nullable=True)
    bulk_discount_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="supplier_prices")
    product: Mapped["Product"] = relationship("Product", back_populates="supplier_prices")

    def __repr__(self) -> str:
        return (
            f"<SupplierPrice id={self.id} supplier_id={self.supplier_id} "
            f"product_id={self.product_id} price={self.price_per_unit} "
            f"recorded={self.recorded_date}>"
        )


# ── Supplier Delivery History ─────────────────────────────────────────────────

class SupplierDelivery(Base):
    __tablename__ = "supplier_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    expected_delivery_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_delivery_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    on_time: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    quantity_ordered: Mapped[float] = mapped_column(Float, nullable=False)
    quantity_received: Mapped[float | None] = mapped_column(Float, nullable=True)
    complaint: Mapped[str | None] = mapped_column(String(300), nullable=True)
    # "Items damaged" | "Short delivery" | None
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # 1–5

    # Relationships
    supplier: Mapped["Supplier"] = relationship(
        "Supplier", back_populates="supplier_deliveries"
    )
    product: Mapped["Product"] = relationship(
        "Product", back_populates="supplier_deliveries"
    )

    def __repr__(self) -> str:
        return (
            f"<SupplierDelivery id={self.id} supplier_id={self.supplier_id} "
            f"product_id={self.product_id} order_date={self.order_date} "
            f"on_time={self.on_time} rating={self.rating}>"
        )


# ── Orders ────────────────────────────────────────────────────────────────────

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    supplier_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    order_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    # "daily" | "weekly" | "monthly" | "emergency"

    # AI recommendation — immutable after creation
    ai_recommended_qty: Mapped[float] = mapped_column(Float, nullable=False)
    ai_reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    # Full multi-line explanation shown in UI

    # Owner decision — starts equal to ai_recommended_qty, owner can edit
    final_qty: Mapped[float] = mapped_column(Float, nullable=False)
    owner_modified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    owner_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Financials — recalculated when final_qty changes
    unit: Mapped[str] = mapped_column(String(30), nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending_approval")
    # "pending_approval" | "approved" | "sent_whatsapp" | "delivered" | "rejected"
    whatsapp_message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    supplier: Mapped["Supplier"] = relationship("Supplier", back_populates="orders")
    product: Mapped["Product"] = relationship("Product", back_populates="orders")

    def __repr__(self) -> str:
        return (
            f"<Order id={self.id} product_id={self.product_id} "
            f"supplier_id={self.supplier_id} cycle={self.order_cycle!r} "
            f"ai_qty={self.ai_recommended_qty} final_qty={self.final_qty} "
            f"status={self.status!r}>"
        )


# ── Daily Briefings ───────────────────────────────────────────────────────────

class DailyBriefing(Base):
    __tablename__ = "daily_briefings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, unique=True)
    brief_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Gemini-generated markdown brief
    context_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    # JSON: weather, hartal, festivals
    scenarios_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON: active scenarios + impacts
    inventory_alerts_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON: expiry + stockout alerts
    orders_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON: orders drafted this run
    forecast_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    # JSON: full Holt-Winters forecast for all products
    opportunities_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    # JSON: profit opportunity cards
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<DailyBriefing id={self.id} date={self.date} "
            f"created_at={self.created_at}>"
        )


# ── Chat History ──────────────────────────────────────────────────────────────

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    # "user" | "assistant"
    content: Mapped[str] = mapped_column(Text, nullable=False)
    context_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    # JSON: which RAG docs were retrieved
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<ChatMessage id={self.id} role={self.role!r} "
            f"created_at={self.created_at}>"
        )
