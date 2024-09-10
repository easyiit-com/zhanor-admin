# attachment_file.py
from datetime import datetime, date, time
from decimal import Decimal
from sqlalchemy.sql.expression import ClauseElement
from .meta import Base
from app.core.db import db

 
class AttachmentFile(Base):
    __tablename__ = 'attachment_file'
    id = db.Column(db.Integer, primary_key=True, nullable=False,comment='ID') 
    category = db.Column(db.String(50),comment='GeneralCategory') 
    admin_id = db.Column(db.Integer, nullable=False,comment='Administrator ID') 
    user_id = db.Column(db.Integer, nullable=False,comment='Member ID') 
    is_image = db.Column(db.Enum('0', '1'),server_default='0', comment='Whether the file is an image')
    thumbnail = db.Column(db.String(255), comment='Thumbnail Path')
    path_file = db.Column(db.String(255), nullable=False,comment='Physical Path') 
    file_name = db.Column(db.String(100),comment='File Name') 
    file_size = db.Column(db.Integer, nullable=False,comment='File Size') 
    mimetype = db.Column(db.String(100),comment='MIME Type') 
    extparam = db.Column(db.String(255),comment='Passthrough Data') 
    createtime = db.Column(db.DateTime, nullable=False,comment='Createtime') 
    updatetime = db.Column(db.DateTime, nullable=False,comment='Update Time') 
    storage = db.Column(db.String(100), nullable=False,comment='Storage Location') 
    sha1 = db.Column(db.String(40),comment='SHA1 Hash of the File') 
    general_attachmentcol = db.Column(db.String(45),comment='General Attachmentcol') 



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
