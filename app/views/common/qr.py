# from datetime import datetime
# from io import BytesIO
# import mimetypes
# import os
# import uuid
# import urllib.parse
# import qrcode
# from zhanor_admin.common.defs import now
# from pyramid.view import view_config
# from pyramid.response import Response

# from zhanor_admin.common.defs import get_image_info, is_image
# from ..models.attachment_file import AttachmentFile
# from ..models.attachment_image import AttachmentImage
# import transaction

# from app.utils.logger import logger
# logger = logger.getLogger(__name__)

# @view_config(route_name='qr',permission="user", request_method='GET')
# def qr_view(request):
#     data = request.matchdict.get('data')
#     data = urllib.parse.unquote(data).replace(":/","://")
#     qr = qrcode.QRCode(
#         version=1,
#         error_correction=qrcode.constants.ERROR_CORRECT_L,
#         box_size=10,
#         border=4,
#     )
#     qr.add_data(data)
#     qr.make(fit=True)

#     img_io = BytesIO()  # 使用BytesIO创建内存中的临时文件
#     img = qr.make_image(fill='black', back_color='white')
#     img.save(img_io, format='PNG')  # 将二维码图片保存到内存中

#     img_io.seek(0)  # 回到起始位置以便读取数据
#     response = Response(body=img_io.getvalue(), content_type='image/png')

#     return response