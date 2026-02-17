from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from app.db.base import Base

class CompanyAdminModel(Base):
    __tablename__ = "company_admin"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("company.id"), nullable=False)
    is_primary_admin = Column(Boolean, default=False, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "company_id", name="uq_user_company"),
    )
