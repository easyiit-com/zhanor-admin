from datetime import datetime
import mimetypes
import os
import uuid
from flask import Blueprint, current_app, request
from app.core.base_response import Response
from app.core.db import get_db
from app.models.attachment_file import AttachmentFile
from app.core.utils.defs import generate_thumbnail, get_image_info, is_image, now 
from PIL import Image
from app.core.utils.logger import logger
 
bp = Blueprint("upload", __name__)

@bp.route('/upload', methods=["POST"])
def upload_view():
    user_id = 0
    admin_id = 0
    
    domain = current_app.config.get('DOMAIN', '') 
    upload_directory = current_app.config.get('UPLOAD_DIRECTORY')   
    allowed_extensions = current_app.config.get('UPLOAD_FILE_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'docx', 'doc', 'ppt'])
    max_size = int(current_app.config.get('UPLOAD_MAX_SIZE', 5242880))
    max_count = int(current_app.config.get('UPLOAD_MAX_COUNT', 3)) 
    
    if 'files[]' not in request.files:
       return Response.error(msg='No file part')
 
    upload_files = request.files.getlist('files[]')
    
    logger.error(f"Uploading: {upload_files}")
    save = request.form.get('save', 'true')
    extparam = request.form.get('extparam', '')  # Capturing extparam from form data

    if isinstance(upload_files, (list, tuple)): 
        if len(upload_files) > max_count:
            return Response.error(msg="Exceeded max file count")
        
    if len(upload_files) == 0: 
        return Response.error(msg="No files were selected", data=request)
    
    # Default thumbnails for non-image files
    default_thumbnails = {
        'pdf': '/static/assets/images/file-type-pdf.png',
        'doc': '/static/assets/images/file-type-doc.png',
        'docx': '/static/assets/images/file-type-doc.png',
        'ppt': '/static/assets/images/file-type-ppt.png',
        # Add more default thumbnails if needed
        'default': '/static/assets/images/file-type-default.png'
    }

    urls = []
    db_session = get_db()
    for upload_file in upload_files:
        filename = upload_file.filename 
        ext = os.path.splitext(filename)[1].lower().replace('.', '')
        if ext not in allowed_extensions:
            return Response.error(msg="File type not allowed")

        if upload_file.content_length > max_size:
            return Response.error(msg="File size is too large")
        
        base_path = os.path.join(upload_directory, datetime.now().strftime('%Y%m%d'))
        os.makedirs(base_path, exist_ok=True)  
        
        unique_filename = str(uuid.uuid4()) + '.' + ext
        file_path = os.path.join(base_path, unique_filename)
        
        
        with open(file_path, 'wb') as output_file:
            output_file.write(upload_file.read())

        # Get the MIME type of the file
        mimetype, _ = mimetypes.guess_type(file_path)
        if not mimetype:
            mimetype = 'application/octet-stream'  # Default if MIME type cannot be determined

        relative_path = os.path.join('/static','uploads', datetime.now().strftime('%Y%m%d'))
        relative_file = os.path.join(relative_path, unique_filename)

        # Check if the file is an image and generate a thumbnail if it is
        is_image_file = "1" if is_image(file_path) else "0"   # Check if the file is an image
        thumbnail_path = None
        if is_image_file == "1":
            thumbnail_path = generate_thumbnail(file_path, base_path, relative_path)  # Generate a thumbnail for image files
        else:
            # Assign default thumbnail based on file extension
            thumbnail_path = default_thumbnails.get(ext, default_thumbnails['default'])
        
        
        full_url = domain + relative_file

        if save == 'true':
            user = getattr(request, 'user', None)
            if user:
                user_id = getattr(user, 'id', 0)
            admin = getattr(request, 'admin', None)
            if admin:
                admin_id = getattr(admin, 'id', 0)
            
            attachment_file = AttachmentFile()
            attachment_file.category = 'upload'
            attachment_file.admin_id = admin_id
            attachment_file.user_id = user_id
            attachment_file.path_file = relative_file
            attachment_file.file_name = filename
            attachment_file.file_size = os.path.getsize(file_path)
            attachment_file.mimetype = mimetype  # Set the MIME type
            attachment_file.extparam = extparam  # Set extparam from form data
            attachment_file.is_image = is_image_file  # Set whether the file is an image
            attachment_file.thumbnail = thumbnail_path  # Set the thumbnail path (image or default)
            attachment_file.created_at = now()
            attachment_file.updated_at = now()
            attachment_file.storage = ''
            db_session.add(attachment_file)
            db_session.commit()

        urls.append({'full_url': full_url, 'relative_url': relative_file, 'thumbnail': thumbnail_path})
    
    return Response.success(msg="Files uploaded successfully", data=urls)
 