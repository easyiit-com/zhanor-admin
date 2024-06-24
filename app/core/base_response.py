from flask import Flask, jsonify
from datetime import datetime

class Response:
    @staticmethod
    def success(data=None, msg="Success", code=200):
        timestamp = datetime.utcnow().timestamp()
        response = {
            "code": code,
            "msg": msg,
            "time": timestamp,
            "data": data or {}
        }
        return jsonify(response), code

    @staticmethod
    def error(data=None, msg="Error", code=400):
        timestamp = datetime.utcnow().timestamp()
        response = {
            "code": code,
            "msg": msg,
            "time": timestamp,
            "data": data or {}
        }
        return jsonify(response), code