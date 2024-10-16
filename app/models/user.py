# user.py
from datetime import datetime, date, time
from decimal import Decimal
import bcrypt
from sqlalchemy.sql.expression import ClauseElement
from app.core.base import Base
from app.core.db import db, get_db
from app.core.user.login.mixins import UserMixin

class User(UserMixin,Base):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, nullable=False,comment='ID') 
    user_group_id = db.Column(db.Integer, nullable=False,comment='Group ID') 
    name = db.Column(db.String(32), nullable=False,unique=True,comment='Username') 
    nickname = db.Column(db.String(50), nullable=False,comment='Nickname') 
    password = db.Column(db.String(120), nullable=False,comment='Password') 
    email = db.Column(db.String(100), nullable=False,unique=True,comment='Email')  
    mobile = db.Column(db.String(16), nullable=False,unique=True,comment='Mobile Phone Number') 
    avatar = db.Column(db.String(255),comment='Avatar') 
    level = db.Column(db.SmallInteger, nullable=False,server_default='0',comment='Level') 
    gender = db.Column(db.Enum('female', 'male'), server_default='male',nullable=False,comment='Gender') 
    birthday = db.Column(db.Date,comment='Date of Birth') 
    bio = db.Column(db.String(100),comment='Motto') 
    balance = db.Column(db.Numeric,comment='Balance') 
    score = db.Column(db.Integer, nullable=False,comment='Points') 
    successions = db.Column(db.Integer, server_default='0',comment='Consecutive Login Days') 
    maxsuccessions = db.Column(db.Integer, server_default='0',comment='Maximum Consecutive Login Days') 
    prevtime = db.Column(db.DateTime,comment='Previous Login Time') 
    logintime = db.Column(db.DateTime,comment='Login Time') 
    loginip = db.Column(db.String(50),comment='Login IP Address') 
    loginfailure = db.Column(db.SmallInteger,comment='Failed Login Attempts') 
    joinip = db.Column(db.String(50),comment='Joining IP Address') 
    created_at = db.Column(db.DateTime,comment='Creation Time') 
    updated_at = db.Column(db.DateTime,comment='Update Time') 
    verification = db.Column(db.String(255),comment='Verification') 
    token = db.Column(db.String(50),comment='Token') 
    status = db.Column(db.Enum('normal', 'hidden'),server_default='normal',comment='Status') 
    
    def set_password(self, pw):
        db_session = get_db()
        pwhash = bcrypt.hashpw(pw.encode("utf8"), bcrypt.gensalt())
        self.password = pwhash.decode("utf8")
        db_session.commit()

    def check_password(self, pw):
        if not pw:
            return False
        if self.password is not None:
            try:
                expected_hash = self.password.encode("utf8")
                return bcrypt.checkpw(pw.encode("utf8"), expected_hash)
            except ValueError:
                return False
        else:
            return False



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
