# user_recharge_order.py
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.sql.expression import ClauseElement
from .meta import Base
from app.core.db import db


class UserRechargeOrder(Base):
    __tablename__ = "user_recharge_order"
    id = db.Column(db.Integer, primary_key=True, nullable=False, comment="ID")
    trade_no = db.Column(db.String(100), unique=True, comment="Trade No")
    user_id = db.Column(db.Integer, comment="User ID")
    amount = db.Column(db.Numeric, comment="amount")
    pay_amount = db.Column(db.Integer, comment="Pay Amount")
    transaction_id = db.Column(db.String(120), comment="Transaction_Id")
    payment_method = db.Column(db.String(50), comment="Payment Method")
    pay_time = db.Column(db.DateTime, comment="Pay Time")
    ip = db.Column(db.String(50), comment="IP")
    useragent = db.Column(db.String(255), comment="UserAgent")
    memo = db.Column(db.String(255), comment="Memo")
    createtime = db.Column(db.DateTime, comment="Creation Time ")
    updatetime = db.Column(db.DateTime, comment="Update Time")
    status = db.Column(db.Enum("created", "paid", "expired"),server_default='created', comment="Status")

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
            if isinstance(value, (datetime, date)):
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
                if options_method and hasattr(options_method(), "members"):
                    setattr(self, field_name, field.type.members)
                elif isinstance(field.type, db.Enum):
                    if isinstance(field.default, ClauseElement):
                        pass
                    else:
                        if field.default is not None and hasattr(field.default, "arg"):
                            setattr(
                                self,
                                field_name,
                                (
                                    field.default.arg
                                    if field.default.arg != "None"
                                    else ""
                                ),
                            )

            elif field.default is not None:
                if isinstance(field.default, ClauseElement):
                    pass
                else:
                    if field.default is not None and hasattr(field.default, "arg"):
                        setattr(
                            self,
                            field_name,
                            field.default.arg if field.default.arg != "None" else "",
                        )
            else:
                setattr(self, field_name, "")
