from sqlalchemy import (
    Column, String, Integer, BigInteger, Boolean, Date, ForeignKey, Enum, DECIMAL,DateTime
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime,timezone
import enum

Base = declarative_base()

# --------------------------
# user types
# --------------------------
class UserTypeEnum(str, enum.Enum):
    USER = 'US'
    SUBUSER = 'SU'
    DISTRIBUTER = 'DI'
    DEALER = 'DE'
    SUBDEALER = 'SD'
    ADMIN = 'AD'

# --------------------------
# User Model
# --------------------------
class User(Base):
    __tablename__ = 'User'

    id = Column(BigInteger, primary_key=True, default=10)
    username = Column(String(150), unique=True, nullable=False)  # Simulating Django username
    first_name = Column(String(100), nullable=False)
    email = Column(String(254), nullable=False)

    phone = Column(String(10), nullable=False)  
    added_by = Column(String(50))
    company_details = Column(String(150), nullable=True)
    other_info = Column(String(255), nullable=True)

    user_type = Column(Enum(UserTypeEnum), default=UserTypeEnum.ADMIN, nullable=False)

    devices = relationship("DeviceTable", back_populates="owner")
    data = relationship("DeviceData", back_populates="device")

    def __repr__(self):
        return f"<User(username='{self.username}', user_type='{self.user_type}', phone='{self.phone}')>"

# --------------------------
# Device Model
# --------------------------
class DeviceTable(Base):
    __tablename__ = 'deviceTable'

    imei = Column(String(15), primary_key=True)
    device_company = Column(String(10), nullable=False)  
    device_model = Column(String(30), nullable=True)

    icc_id = Column(String(30), nullable=False, unique=True)
    unique_id = Column(String(1), default="N", nullable=True)

    primary_contact = Column(DECIMAL(13, 0), nullable=False, unique=True)
    secondary_contact = Column(DECIMAL(1, 0), default=0, nullable=True)

    version = Column(String(2), default="1", nullable=True)
    activation_status = Column(Boolean, nullable=False)
    activation_date = Column(Date, nullable=True)

    current_owner_username = Column(String(150), ForeignKey("User.username"), nullable=False)
    owner = relationship("User", back_populates="devices")

    added_date = Column(Date, default=datetime.now)
    other_info = Column(String(255), nullable=True)

    data = relationship("DeviceData", back_populates="device")

    def __repr__(self):
        return f"<DeviceTable(imei='{self.imei}', owner='{self.current_owner_username}')>"
    

class DeviceData(Base):
    __tablename__ = 'DeviceData'

    id = Column(Integer, primary_key=True)
    imei = Column(String(15), ForeignKey('deviceTable.imei'))
    message = Column(String)
    received_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    device = relationship("DeviceTable", back_populates="data")

    def __repr__(self):
        return f"<Devicedata(data='{self.message}'>"