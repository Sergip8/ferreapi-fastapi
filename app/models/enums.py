from enum import Enum as PyEnum

class UserType(PyEnum):
    customer = "customer"
    distributor = "distributor"
    administrator = "administrator"
    employee = "employee"

class ProductStatus(PyEnum):
    active = "active"
    out_of_stock = "out_of_stock"
    by_order = "by_order"
    discontinued = "discontinued"

class PromotionType(PyEnum):
    percentage = "percentage"
    fixed_amount = "fixed_amount"
    bundle = "bundle"

class PromotionStatus(PyEnum):
    active = "active"
    inactive = "inactive"

class OrderStatus(PyEnum):
    pending = "pending"
    processing = "processing"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

class ManufacturingStatus(PyEnum):
    operational = "operational"
    maintenance = "maintenance"
    repair = "repair"
    offline = "offline"

class QualityCheckStatus(PyEnum):
    pending = "pending"
    passed = "passed"
    failed = "failed"

class QCStatus(PyEnum):
    passed = "passed"
    failed = "failed"

class PaymentStatus(PyEnum):
    paid = "paid"
    partially_paid = "partially_paid"
    pending = "pending"
    overdue = "overdue"

class ShippingStatus(PyEnum):
    processing = "processing"
    shipped = "shipped"
    in_transit = "in_transit"
    delivered = "delivered"
    failed = "failed"

class ReturnStatus(PyEnum):
    pending = "pending"
    processed = "processed"
    rejected = "rejected" 