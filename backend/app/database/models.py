"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database.session import Base


# Enums
class BusinessType(str, enum.Enum):
    """Business entity types."""
    LLC = "llc"
    CORPORATION = "corporation"
    PARTNERSHIP = "partnership"
    SOLE_PROPRIETOR = "sole-proprietor"


class Industry(str, enum.Enum):
    """Industry verticals."""
    LOGISTICS = "logistics"
    AGRICULTURE = "agriculture"
    MANUFACTURING = "manufacturing"
    DELIVERY = "delivery"
    CONSTRUCTION = "construction"
    RETAIL = "retail"


class PrequalificationStatus(str, enum.Enum):
    """Prequalification application status."""
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    NEEDS_REVIEW = "needs_review"


class MessageRole(str, enum.Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


# Models
class Tenant(Base):
    """Multi-tenant organization model."""

    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    settings = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    prequalifications = relationship("Prequalification", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """User model with auth and profile information."""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    user_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    threads = relationship("Thread", back_populates="user", cascade="all, delete-orphan")


class Prequalification(Base):
    """Equipment lease prequalification application."""

    __tablename__ = "prequalifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    application_number = Column(String(50), unique=True, nullable=False, index=True)

    # Business Information
    business_name = Column(String(255), nullable=False)
    business_type = Column(Enum(BusinessType), nullable=False)
    industry = Column(Enum(Industry), nullable=False)

    # Contact
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=False)

    # Equipment Needs
    selected_equipment = Column(JSON, nullable=False)  # Array of equipment IDs
    quantity = Column(String(20), nullable=False)

    # Financials
    annual_revenue = Column(String(20), nullable=False)
    business_age = Column(String(10), nullable=False)
    credit_rating = Column(String(20), nullable=False)

    # Consent
    consent = Column(Boolean, nullable=False)

    # Status and Results
    status = Column(Enum(PrequalificationStatus), default=PrequalificationStatus.PENDING, nullable=False)
    estimated_decision_date = Column(DateTime, nullable=True)

    # Agent Processing Results
    agent_analysis = Column(JSON, nullable=True)
    preliminary_terms = Column(JSON, nullable=True)  # estimated payments, terms, etc.

    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="prequalifications")


class Robot(Base):
    """Robot/Equipment catalog."""

    __tablename__ = "robots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    manufacturer = Column(String(255), nullable=False, index=True)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    use_case = Column(Enum(Industry), nullable=False, index=True)

    # Specifications
    payload = Column(String(50), nullable=True)
    autonomy_level = Column(String(20), nullable=True)
    specifications = Column(JSON, nullable=True)

    # Pricing
    lease_from = Column(String(50), nullable=False)
    lease_price_monthly = Column(Float, nullable=True)

    # Media
    image_url = Column(String(500), nullable=True)

    # Metadata
    is_active = Column(Boolean, default=True, nullable=False)
    robot_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Dealer(Base):
    """Authorized dealer network."""

    __tablename__ = "dealers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    coverage = Column(Text, nullable=False)
    address = Column(Text, nullable=False)
    phone = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    website = Column(String(500), nullable=True)

    # Service Information
    specialties = Column(JSON, nullable=False)  # Array of specialty strings
    zip_codes = Column(JSON, nullable=False)  # Array of covered ZIP codes

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Metadata
    extra_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Thread(Base):
    """Conversation thread for agent interactions."""

    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    title = Column(String(255), nullable=True)
    context = Column(JSON, nullable=True)  # Page context, user state, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="threads")
    messages = relationship("ThreadMessage", back_populates="thread", cascade="all, delete-orphan")


class ThreadMessage(Base):
    """Message within a conversation thread."""

    __tablename__ = "thread_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    agent_id = Column(String(100), nullable=True)  # Which agent generated this
    message_metadata = Column(JSON, nullable=True)  # Tool calls, thought process, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    thread = relationship("Thread", back_populates="messages")


class AgentVersion(Base):
    """Agent contract version tracking."""

    __tablename__ = "agent_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, index=True)
    version = Column(String(20), nullable=False)
    contract_schema = Column(JSON, nullable=False)  # Full agent contract JSON
    is_active = Column(Boolean, default=True, nullable=False)
    performance_metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
