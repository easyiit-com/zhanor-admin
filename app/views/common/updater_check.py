# import json
# from pyramid.response import Response
# from pyramid.view import notfound_view_config,view_config
# from pyramid.httpexceptions import HTTPNotFound

# @view_config(route_name='updater.check', request_method='POST', renderer='json')
# def post_notfound_view(exc, request):
#     data = {
#         'version':'1.0.2',
#         'md5':"fdaejk8jjdfliyuumadedsanmxudeskseffd",
#         'download':'http://admin.zhanor.com/last_version.zip',
#         'update_time':'2024-01-01 15:36:21'
#     }
#     return Response(
#                 json.dumps({'status': 0, 'msg': 'HTTPNotFound', 'data': {}}),
#                 content_type="application/json",
#                 charset="utf-8",
#                 status = 404
#             )