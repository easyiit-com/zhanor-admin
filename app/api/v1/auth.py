import json
import requests
from app.core.csrf import csrf
from app.models.user import User
from app.core.utils.defs import ip, now
from app.core.utils.logger import logger
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from flasgger import swag_from
from flask_restful import Resource, reqparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
from app.core.db import get_db 

class ApiRegister(Resource):
   
    @swag_from(
        {
            "tags": ["Authentication"],
            "operationId": "registerUser",
            "summary": "Register a new user",
            "description": "Endpoint to register a new user with email, password, mobile, and name.",
            "parameters": [
                {
                    "in": "body",
                    "name": "user_details",
                    "description": "User details to register",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "email": {
                                "type": "string",
                                "description": "The email of the user",
                                "required": True,
                            },
                            "password": {
                                "type": "string",
                                "description": "The password of the user",
                                "required": True,
                            },
                            "mobile": {
                                "type": "string",
                                "description": "The mobile number of the user",
                                "required": True,
                            },
                            "name": {
                                "type": "string",
                                "description": "The username of the user",
                                "required": True,
                            },
                        },
                    },
                },
            ],
            "responses": {
                "201": {"description": "User registered successfully"},
                "400": {"description": "Bad Request - Invalid input"},
                "409": {"description": "Conflict - User already exists"},
            },
        }
    )
    @csrf.exempt
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True, help="Email is required.")
        parser.add_argument("password", type=str, required=True, help="Password is required.")
        parser.add_argument("mobile", type=str, required=True, help="Mobile is required.")
        parser.add_argument("name", type=str, required=True, help="Username is required.")
        data = parser.parse_args()

        # 检查用户是否已存在
        existing_user = User.query.filter(
            (User.email == data["email"]) |
            (User.mobile == data["mobile"]) |
            (User.name == data["name"])
        ).first()

        if existing_user:
            return {"msg": "User already exists"}, 409
        # 创建新用户
        new_user = User(
            user_group_id=1,
            email=data["email"],
            mobile=data["mobile"],
            name=data["name"],
            nickname=f"user_{data['name']}",  # 默认值
            password="",  # 默认值，密码将被设置
            avatar="/static/assets/img/avatar.png	",  # 默认值
            level=1,  # 默认值
            gender='male',  # 默认值
            birthday=None,  # 默认值
            bio="",  # 默认值
            balance=0,  # 默认值
            score=0,  # 默认值
            successions=0,  # 默认值
            maxsuccessions=0,  # 默认值
            prevtime=now(),  # 默认值
            logintime=now(),  # 默认值
            loginip=ip(),  # 默认值
            loginfailure=0,  # 默认值
            joinip=ip(),  # 默认值
            createtime=now(),  # 当前时间
            updatetime=now(),  # 当前时间
            verification="",  # 默认值
            token="",  # 默认值
            status='normal',  # 默认值
        )
        new_user.set_password(data["password"])
        db_session = get_db()
        db_session.add(new_user)
        db_session.commit()

        return {
            "msg": "User created successfully",
            "data": {"email": data["email"], "mobile": data["mobile"], "name": data["name"]},
        }, 201



class ApiLogin(Resource):
    @csrf.exempt
    @swag_from(
        {
            "tags": ["Authentication"],
            "operationId": "loginUser",
            "summary": "Login a user",
            "description": "Endpoint to login a user with email, mobile, or username.",
            "parameters": [
                {
                    "in": "body",
                    "name": "login_details",
                    "description": "User details to login",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "identifier": {
                                "type": "string",
                                "description": "Email, mobile number, or username",
                                "required": True,
                            },
                            "password": {
                                "type": "string",
                                "description": "The password of the user",
                                "required": True,
                            },
                        },
                    },
                },
            ],
            "responses": {
                "200": {"description": "User logged in successfully"},
                "400": {"description": "Bad Request - Invalid input"},
                "401": {"description": "Unauthorized - Invalid credentials"},
            },
        }
    )
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("identifier", type=str, required=True, help="Email, mobile, or username is required.")
        parser.add_argument("password", type=str, required=True, help="Password is required.")
        data = parser.parse_args()

        identifier = data.get("identifier")
        password = data.get("password")

        # 查找用户
        user = User.query.filter(
            (User.email == identifier) |
            (User.mobile == identifier) |
            (User.name == identifier)
        ).first()

        if not user or not user.check_password(password):
            return {"msg": "Invalid credentials"}, 401

        # 登录成功，生成访问令牌
        access_token = create_access_token(identity=user.id)
        return {"msg": "Login successful", "data": {"token": access_token}}, 200

