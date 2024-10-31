from flask import request
from flask_restful import Resource 
from flask_jwt_extended import jwt_required  
from flasgger import swag_from
from flask_restful import Resource, reqparse
from app.core.db import get_db
from app.models.%%model_name%% import %%model_class_name%%
 
class Api%%model_class_name%%List(Resource):
    @swag_from(
        {
            "tags": ["%%model_class_name%%s"],
            "operationId": "get%%model_class_name%%List",
            "summary": "Retrieve a list of all %%model_name%%s",
            "description": "Get a list containing all registered %%model_name%%s.",
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT or Bearer Token",
                    "required": True,
                    "type": "string",
                    "format": "Bearer <token>",
                    "example": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
                },
            ],
            "responses": {
                "200": {
                    "description": "List of %%model_name%%s retrieved successfully",
                    "schema": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/%%model_class_name%%"},
                    },
                },
                "401": {"description": "Unauthorized"},
            },
        }
    )
    @jwt_required()
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "%%model_name%%_id", type=int, location="args", help="Filter by %%model_name%%_id"
        )
        parser.add_argument(
            "title",
            type=str,
            action="append",
            location="args",
            help="Filter by title (支持多个)",
        )
        args = parser.parse_args()

        query = %%model_class_name%%.query
        if args.%%model_name%%_id:
            query = query.filter_by(%%model_name%%_id=args.%%model_name%%_id)
        if args.title:
            query = query.filter(%%model_class_name%%.title.in_(args.title))

        %%model_name%%s = %%model_class_name%%.query.order_by(%%model_class_name%%.id.desc()).all()
        %%model_name%%_dicts = [%%model_name%%.to_dict() for %%model_name%% in %%model_name%%s]
        return {"code": 1,"msg": "Get Successfully", "data": %%model_name%%_dicts}, 200

class Api%%model_class_name%%Create(Resource):
    @jwt_required()
    @swag_from(
        {
            "tags": ["%%model_class_name%%s"],
            "operationId": "create %%model_class_name%%",
            "summary": "Create a %%model_name%%",
            "description": "Create a new %%model_name%%",
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT or Bearer Token",
                    "required": True,
                    "type": "string",
                    "format": "Bearer <token>",
                    "example": "Bearer <token>",
                },
                {
                    "in": "body",
                    "name": "%%model_name%%_create",
                    "description": "%%model_class_name%% data",
                    "schema": {
                        "type": "object",
                        "properties": {
                            %%api_schema%%
                        },
                    },
                },
            ],
            "responses": {
                "200": {"description": "%%model_class_name%% created/updated successfully"},
                "400": {"description": "Bad Request - Invalid input or missing required fields"},
                "401": {"description": "Unauthorized - Invalid token provided"},
                "404": {"description": "Not Found - %%model_class_name%% not found"},
            },
        }
    )
    def put(self):
        db_session = get_db()
        data = request.get_json()
        new_%%model_name%% = %%model_class_name%%(**data)
        db_session.add(new_%%model_name%%)
        db_session.commit()
        return {"code": 1,"msg": "Created successfully", "data": new_%%model_name%%.to_dict()}, 200
     
class Api%%model_class_name%%(Resource):

    @jwt_required()
    @swag_from(
        {
            "tags": ["%%model_class_name%%s"],
            "operationId": "get%%model_class_name%%",
            "summary": "Get a single %%model_name%% by ID",
            "description": "Retrieve detailed information about a specific %%model_name%% by their ID.",
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT or Bearer Token",
                    "required": True,
                    "type": "string",
                    "format": "Bearer <token>",
                    "example": "Bearer <token>",
                },
                {
                    "name": "%%model_name%%_id",
                    "in": "path",
                    "description": "The ID of the %%model_name%% to retrieve",
                    "required": True,
                    "type": "integer",
                },
            ],
            "responses": {
                "200": {
                    "description": "%%model_class_name%% details retrieved successfully",
                    "schema": {"$ref": "#/definitions/%%model_class_name%%"},
                },
                "404": {"description": "%%model_class_name%% not found"},
            },
        }
    )
    def get(self, %%model_name%%_id):
        %%model_name%% = %%model_class_name%%.query.get_or_404(%%model_name%%_id)
        return {"code": 1,"msg": "Get Successfully", "data": %%model_name%%.to_dict()}, 200

    @jwt_required()
    @swag_from(
        {
            "tags": ["%%model_class_name%%s"],
            "operationId": "update%%model_class_name%%",
            "summary": "Update a %%model_name%%",
            "description": "Update an existing %%model_name%% by providing the %%model_name%% ID.",
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT or Bearer Token",
                    "required": True,
                    "type": "string",
                    "format": "Bearer <token>",
                    "example": "Bearer <token>",
                },
                {
                    "name": "%%model_name%%_id",
                    "in": "path",
                    "description": "The ID of the %%model_name%% to update",
                    "required": True,
                    "type": "integer",
                },
                {
                    "in": "body",
                    "name": "%%model_name%%_create",
                    "description": "%%model_class_name%% data",
                    "schema": {
                        "type": "object",
                        "properties": {
                            %%api_schema%%
                        },
                    },
                },
            ],
            "responses": {
                "200": {"description": "%%model_class_name%% created/updated successfully"},
                "400": {"description": "Bad Request - Invalid input or missing required fields"},
                "401": {"description": "Unauthorized - Invalid token provided"},
                "404": {"description": "Not Found - %%model_class_name%% not found"},
            },
        }
    )
    def put(self, %%model_name%%_id=None):
        db_session = get_db()
        data = request.get_json()
        if %%model_name%%_id:
            %%model_name%% = %%model_class_name%%.query.get_or_404(%%model_name%%_id)
            for key, value in data.items():
                if hasattr(%%model_name%%, key):
                    setattr(%%model_name%%, key, value)
            db_session.commit()
            return {"code": 1,"msg": "Updated successfully"}, 200

    @jwt_required()
    @swag_from(
        {
            "tags": ["%%model_class_name%%s"],
            "operationId": "delete%%model_class_name%%",
            "summary": "Delete a %%model_name%% by ID",
            "description": "Deletes a %%model_name%% from the system based on the provided %%model_name%% ID.",
            "parameters": [
                {
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT or Bearer Token",
                    "required": True,
                    "type": "string",
                    "format": "Bearer <token>",
                    "example": "Bearer <token>",
                },
                {
                    "name": "%%model_name%%_id",
                    "in": "path",
                    "description": "The ID of the %%model_name%% to delete",
                    "required": True,
                    "type": "integer",
                },
            ],
            "responses": {
                "204": {"description": "%%model_class_name%% deleted successfully"},
                "404": {"description": "Not Found - %%model_class_name%% not found"},
            },
        }
    )
    def delete(self, %%model_name%%_id):
        db_session = get_db()
        %%model_name%% = %%model_class_name%%.query.get_or_404(%%model_name%%_id)
        db_session.delete(%%model_name%%)
        db_session.commit()
        return {"code": 1,"msg": "Deleted successfully"}, 204