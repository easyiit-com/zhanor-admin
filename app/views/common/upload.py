from datetime import datetime
import mimetypes
import os
import uuid
from flask import Blueprint, current_app, request
from app.core.base_response import Response
from app.core.db import get_db
from app.models.attachment_file import AttachmentFile
from app.utils.defs import get_image_info, is_image, now 
 
import logging
logger = logging.getLogger(__name__)

bp = Blueprint("upload", __name__)

@bp.route('/upload',methods=["POST"])
def upload_view():
    user_id = 0
    admin_id = 0
    
    domain  = current_app.config.get('DOMAIN','') 
    upload_directory = current_app.config.get('UPLOAD_DIRECTORY') 
    allowed_image_extensions = current_app.config.get('UPLOAD_IMAGE_EXTENSIONS', ['jpg','jpeg','png','gif'])
    allowed_file_extensions = current_app.config.get('UPLOAD_FILE_EXTENSIONS', ['pdf','zip'])
    allowed_extensions = allowed_image_extensions + allowed_file_extensions
    max_size = int(current_app.config.get('UPLOAD_MAX_SIZE', 5242880))
    max_count = int(current_app.config.get('UPLOAD_MAX_COUNT', 3)) 
    
    if 'files[]' not in request.files:
       return Response.error(msg='No file part')
 
    upload_files = request.files.getlist('files[]')
    
    logger.error(f"Uploading:{upload_files}")
    save = request.form.get('save', 'true')

    if isinstance(upload_files, (list, tuple)): 
        if len(upload_files) > max_count:
            return Response.error(msg="Exceeded max file count")
        
    if len(upload_files)==0: 
        return Response.error(msg="No files were not selected",data = request)
    
    urls = []
    db_session = get_db()
    for upload_file in upload_files:
        filename = upload_file.filename
        logger.error(f"filename=========>{filename}")
        ext = os.path.splitext(filename)[1].lower().replace('.', '')
        if ext not in allowed_extensions:
            return Response.error(msg="File type not allowed")

        if upload_file.content_length > max_size:
            return Response.error(msg="File size is too large")
            
        base_path = os.path.join(upload_directory, datetime.now().strftime('%Y%m%d'))
        os.makedirs(base_path, exist_ok=True)  
        
        unique_filename = str(uuid.uuid4()) + '.' +ext
        file_path = os.path.join(base_path, unique_filename)
        
        with open(file_path, 'wb') as output_file:
            output_file.write(upload_file.read())
        relative_path = os.path.join('/static/uploads', datetime.now().strftime('%Y%m%d'), unique_filename)
        full_url = domain + relative_path
        if save=='true':
            user = getattr(request, 'user', None)
            if user:
                user_id = getattr(user, 'id', 0)
            admin = getattr(request, 'admin', None)
            if admin:
                admin_id = getattr(admin, 'id', 0)
            
            
            admin_id = getattr(admin, 'id', 0)
            attachment_file = AttachmentFile()
            attachment_file.category = 'upload'
            attachment_file.admin_id = admin_id
            attachment_file.user_id = user_id
            attachment_file.path_file = relative_path
            attachment_file.file_name = filename
            attachment_file.file_size = os.path.getsize(file_path)
            attachment_file.mimetype = ''
            attachment_file.createtime = now()
            attachment_file.updatetime = now()
            attachment_file.storage = ''
            db_session.add(attachment_file)
            db_session.commit()
        urls.append({'full_url': full_url, 'relative_url': relative_path})
    
    return Response.success(msg="Files uploaded successfully", data = urls)
 