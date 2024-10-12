from flask import Flask, jsonify
from datetime import datetime

class Response:
    """
    通用响应类，提供静态方法返回标准化的成功或错误响应。
    """

    @staticmethod
    def success(data=None, msg="Success", code=200):
        """
        返回成功响应。
        :param data: 返回的数据，默认为空字典。
        :param msg: 成功消息，默认为 "Success"。
        :param code: 状态码，默认为 200。
        :return: Flask jsonify 格式的响应对象和 HTTP 状态码。
        """
        timestamp = datetime.utcnow().timestamp()  # 获取当前 UTC 时间戳
        response = {
            "code": code,     # 状态码
            "msg": msg,       # 成功信息
            "time": timestamp, # 时间戳
            "data": data or {} # 返回的数据，默认为空字典
        }
        return jsonify(response), code

    @staticmethod
    def error(data=None, msg="Error", code=400):
        """
        返回错误响应。
        :param data: 返回的数据，默认为空字典。
        :param msg: 错误消息，默认为 "Error"。
        :param code: 状态码，默认为 400。
        :return: Flask jsonify 格式的响应对象和 HTTP 状态码。
        """
        timestamp = datetime.utcnow().timestamp()  # 获取当前 UTC 时间戳
        response = {
            "code": code,     # 状态码
            "msg": msg,       # 错误信息
            "time": timestamp, # 时间戳
            "data": data or {} # 返回的数据，默认为空字典
        }
        return jsonify(response), code
