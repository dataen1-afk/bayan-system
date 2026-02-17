"""
Invoice and payment-related Pydantic models.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid


class InvoiceItem(BaseModel):
    description: str
    description_ar: str = ""
    quantity: int = 1
    unit_price: float
    total: float = 0


class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_number: str = ""  # Auto-generated: INV-2026-001
    contract_id: str  # Links to proposal/agreement
    organization_name: str
    organization_address: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    # Invoice details
    items: List[InvoiceItem] = []
    subtotal: float = 0
    tax_rate: float = 15  # VAT percentage (Saudi Arabia: 15%)
    tax_amount: float = 0
    total_amount: float = 0
    currency: str = "SAR"
    # Payment terms
    issue_date: str = ""  # When invoice was created
    due_date: str = ""  # Payment due date
    payment_terms: str = "net_30"  # net_15, net_30, net_60, due_on_receipt
    # Status tracking
    status: str = "draft"  # draft, sent, viewed, paid, overdue, cancelled
    paid_amount: float = 0
    paid_date: Optional[str] = None
    payment_method: str = ""  # bank_transfer, stripe, cash, cheque
    payment_reference: str = ""  # Transaction ID or reference
    # Stripe integration
    stripe_invoice_id: str = ""
    stripe_payment_intent_id: str = ""
    stripe_payment_url: str = ""
    # Notes
    notes: str = ""
    internal_notes: str = ""
    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None


class InvoiceCreate(BaseModel):
    contract_id: str
    items: List[InvoiceItem] = []
    tax_rate: float = 15
    due_date: str = ""
    payment_terms: str = "net_30"
    notes: str = ""


class PaymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    invoice_id: str
    amount: float
    payment_date: str
    payment_method: str  # bank_transfer, stripe, cash, cheque
    reference: str = ""  # Transaction ID
    notes: str = ""
    recorded_by: str = ""  # Admin who recorded the payment
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
