# addon_order.py
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy.sql.expression import ClauseElement
from sqlalchemy.orm import relationship
from app.core.base import Base
from app.core.db import db

 
class AddonOrder(Base):
    __tablename__ = 'addon_order'
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment='Order ID')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='User ID')
    addon_id = db.Column(db.Integer, db.ForeignKey('addon.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, comment='Addon ID')
    order_number = db.Column(db.String(64), nullable=False, unique=True, comment='Order Number')
    transaction_id = db.Column(db.String(64), comment='Transaction ID')
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='Order Amount')
    pay_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00, comment='Paid Amount')
    status = db.Column(db.Enum('pending', 'paid', 'cancelled', 'failed'), nullable=False, default='pending', comment='Payment Status')
    payment_method = db.Column(db.String(32), comment='Payment Method')
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), comment='Creation Time')
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), comment='Update Time')

    # 定义与 User 和 Addon 模型的关系
    # user = relationship('User', backref='addon_orders', passive_deletes=True)
    # addon = relationship('Addon', backref='addon_orders', passive_deletes=True)

    # __table_args__ = (
    #     # 唯一约束
    #     db.UniqueConstraint('order_number', name='uk_order_number'),
    #     # 索引
    #     db.Index('idx_user_id', 'user_id'),
    #     db.Index('idx_addon_id', 'addon_id'),
    # )



    @classmethod
    def from_dict(cls, data):
        """
        Creates an instance of GeneralConfig from a dictionary.
        This method explicitly filters out keys that do not correspond to the model's columns.
        """
        
        # List all column names of the model
        valid_keys = {column.name for column in cls.__table__.columns}
        # Filter the dictionary to include only keys that correspond to column names
        filtered_data = {key: value for key, value in data.items() if key in valid_keys}
        return cls(**filtered_data)
    def to_dict(self, fields=None):
        """
        Convert this User instance into a dictionary.

        Args:
        - fields: Optional list of fields to include in the dictionary. If None, includes all fields.

        Returns:
        - A dictionary representation of this User instance.
        """
        # If no specific fields are requested, include all fields.
        if fields is None:
            fields = [column.name for column in self.__table__.columns]
        
        result_dict = {}
        for field in fields:
            value = getattr(self, field, None)
            
            # Convert datetime and date objects to string for JSON compatibility.
            if isinstance(value, (datetime, date, time)):
                value = value.isoformat()
            # Convert Decimal to string to prevent precision loss during serialization.
            elif isinstance(value, Decimal):
                value = str(value)
            
            result_dict[field] = value
        
        return result_dict
    
    def initialize_special_fields(self):
        for field_name, field in self.__mapper__.columns.items():
            if isinstance(field.type, (db.Enum)):
                options_method = getattr(self, f"{field_name}_property".upper(), None)
                if options_method and hasattr(options_method(), 'members'):
                    setattr(self, field_name, field.type.members)
                elif isinstance(field.type, db.Enum):
                    if isinstance(field.default, ClauseElement):
                        pass
                    else:
                        if field.default is not None and hasattr(field.default, 'arg'):
                            setattr(self, field_name, field.default.arg if field.default.arg != 'None' else '')

            elif field.default is not None: 
                if isinstance(field.default, ClauseElement):
                    pass
                else:
                    if field.default is not None and hasattr(field.default, 'arg'):
                            setattr(self, field_name, field.default.arg if field.default.arg != 'None' else '')
            else:
                setattr(self, field_name,'')
