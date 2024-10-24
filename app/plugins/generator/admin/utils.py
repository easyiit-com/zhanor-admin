import os
import re
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import String
from app.core.db import db
class Generator:
    def __init__(self, engine, table_name):
        self.engine = engine
        self.table_name = table_name
        self.mysql_to_sqlalchemy_types = {
            "TINYINT": db.SmallInteger,
            "SMALLINT": db.SmallInteger,
            "MEDIUMINT": db.Integer,
            "INTEGER": db.Integer,
            "BIGINT": db.BigInteger,
            "INT": db.Integer,
            "FLOAT": db.Float,
            "DOUBLE": db.Float,
            "DECIMAL": db.Numeric,
            "NUMERIC": db.Numeric,
            "CHAR": db.String,
            "VARCHAR": db.String,
            "TINYTEXT": db.Text,
            "TEXT": db.Text,
            "JSON": db.Text,
            "MEDIUMTEXT": db.Text,
            "LONGTEXT": db.Text,
            "VARBINARY": db.LargeBinary,
            "BLOB": db.LargeBinary,
            "MEDIUMBLOB": db.LargeBinary,
            "LONGBLOB": db.LargeBinary,
            "BOOLEAN": db.Boolean,
            "DATE": db.Date,
            "DATETIME": db.DateTime,
            "TIMESTAMP": db.DateTime,
            "TIME": db.Time,
            "ENUM": db.Enum,
            "SET": db.Enum,
        }
        
        self.base_dir = os.path.join(os.path.dirname(__file__), os.pardir, "admin")

        self.model_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "model.tpl")
        )
        self.template_index_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "index.tpl")
        )
        self.template_add_edit_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "add_and_edit.tpl")
        )
        self.js_tpl_path = os.path.abspath(os.path.join(self.base_dir, "tpl", "js.tpl"))
        self.views_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "views.tpl")
        )
        self.api_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "api.tpl")
        )
        
        self.schema_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "schema.tpl")
        )
        
        self.route_tpl_path = os.path.abspath(
            os.path.join(self.base_dir, "tpl", "route.tpl")
        )

    def map_column_to_openapi_type(self,column_type):
        column_type_map = {
            'INTEGER': 'integer',
            'BIGINT': 'integer',
            'SMALLINT': 'integer',
            'VARCHAR': 'varchar',
            'TEXT': 'string',
            'DECIMAL': 'decimal',
            'UNICODE': 'string',
            'BOOLEAN': 'boolean',
            'FLOAT': 'number',
            'NUMERIC': 'number',
            'DATE': 'date',
            'DATETIME': 'datetime',
            'ENUM': 'enum', 
            'JSON': 'object',
            'BINARY': 'string', 
            'BLOB': 'string',
            'CHAR': 'string',
            'TIMESTAMP': 'string',
        }
        mapped_type = column_type_map.get(str(column_type), "string").lower() 
        if isinstance(mapped_type, dict):
            return mapped_type
        else:
            return mapped_type
    
    def code(self, fields, controllers):
        try:
            model_name = self.table_name
            model_class_name = self.table_name.title().replace("_", "")
            route_str = self.table_name.replace("_", "/", 1)

            engine = self.engine
            inspector = Inspector.from_engine(engine)

            pk_constraint = inspector.get_pk_constraint(self.table_name)
            pk_columns = pk_constraint.get("constrained_columns", [])
            columns = inspector.get_columns(self.table_name)
            model_code = ""
            model_code += f"class {model_class_name}(Base):\n"
            model_code += "    __tablename__ = '" + self.table_name + "'\n"

            with open(self.model_tpl_path, "r") as source_file:
                model_tpl_content = source_file.read()
            
            with open(self.schema_tpl_path, "r") as source_file:
                schema_tpl_content = source_file.read()    
                
            template_index_tpl_content = ""
            # schema
            schema_code = ""
            schema_code += f"class {model_class_name}Schema(Schema):\n"

            replace_template_index_tpl_table_ths = f""
            replace_template_index_tpl_table_tds = f""
            replace_template_index_tpl_table_details = f""
            with open(self.template_index_tpl_path, "r") as source_file:
                template_index_tpl_content = source_file.read()
            template_add_tpl_content = ""
            template_edit_tpl_content = ""

            replace_template_add_tpl_form_body = ""
            replace_template_edit_tpl_form_body = ""
            with open(self.template_add_edit_tpl_path, "r") as source_file:
                template_add_and_edit_tpl_content = source_file.read()

            with open(self.js_tpl_path, "r") as source_file:
                js_tpl_content = source_file.read()

            with open(self.views_tpl_path, "r") as source_file:
                views_tpl_content = source_file.read()

            with open(self.api_tpl_path, "r") as source_file:
                api_tpl_content = source_file.read()

            with open(self.route_tpl_path, "r") as source_file:
                route_tpl_content = source_file.read()

            js_code = ""
            add_js_code = ""
            api_schema = ""

            table_fields = []
            for column in columns:
                column_name = column.get("name", None)
                column_type = column["type"].__class__.__name__
                length = getattr(column["type"], "length", 0)
                default = column.get("default", None)
                unique = column.get("unique", None)
                nullable = column["nullable"]
                enums_argument = getattr(column["type"], "enums", [])
                column_comment = column.get("comment", column_name)
                required = "required" if nullable == False else ""
                maxlength = f"maxlength = '{length}'" if length else ""
                sets_argument = getattr(column["type"], "values", "")
                sets_argument = sets_argument or ()
                column_comment_safe = column_comment or column_name.title()
                split_result = column_comment_safe.split("(")
                button_text = (
                    split_result[0]
                    if len(split_result) > 0 and "(" in column_comment_safe
                    else column_comment_safe
                )
                split_result = column_comment_safe.split(":")
                button_text = (
                    split_result[0]
                    if len(split_result) > 0 and ":" in column_comment_safe
                    else column_comment_safe
                )

                model_type_class = self.mysql_to_sqlalchemy_types.get(column_type, None)

                if model_type_class is String and length != 0:
                    model_type = model_type_class.__name__ + f"({length})"
                    schema_type = model_type_class.__name__ + f"()"
                elif model_type_class is String:
                    model_type = model_type_class
                    schema_type = model_type_class
                elif model_type_class is not None:
                    model_type = model_type_class.__name__
                    schema_type = model_type_class.__name__
                primary_key = column["name"] in pk_columns
                primary_key_str = ", primary_key=True" if primary_key else ""
                schema_key_str = "dump_only=True" if primary_key else ""
                nullable_str = ", nullable=False" if nullable == False else ""
                default_str = (
                                    f', default=func.now() '  # 处理 created_at
                                    if column_name == "created_at"
                                    else (
                                        f', default=func.now(), onupdate=func.now() '  # 处理 updated_at
                                        if column_name == "updated_at"
                                        else (
                                            f', default={column["default"]} '  # 其他字段的默认值处理
                                            if column.get("default") is not None
                                            and column_type != "DATETIME"
                                            and column_name != "id"
                                            else ""
                                        )
                                    )
                                )

                enums_argument_str = ""
                if model_type == "Enum" and len(enums_argument) > 0:
                    enums_argument_str = "('" + "', '".join(enums_argument) + "')"
                    model_type = f"{model_type}{enums_argument_str}"
                    schema_type = f"String(enum={enums_argument})"

                sets_argument_str = ""
                if (model_type == "SET") and sets_argument and len(sets_argument) > 0:
                    sets_argument_str = str(tuple(sets_argument))
                    model_type = f"{model_type}{sets_argument_str}"
                    schema_type = f"{model_type}{sets_argument_str}"

                model_code += f"    {column['name']} = db.Column(db.{model_type}{'' if nullable else ''}{primary_key_str}{'' if nullable==False else ''}{nullable_str}{'' if default is not None else ''}{default_str},comment='{column_comment_safe}') \n"
              
                schema_code += f"    {column['name']} = fields.{schema_type}({schema_key_str}{'' if default is not None else ''}{default_str}) \n"
                
                openapi_type = self.map_column_to_openapi_type(column_type)
                column.get('type') 
                openapi_format = ""
                emun = ''
                if openapi_type == "datetime":
                    openapi_type = "string"
                    openapi_format = '"format": "date-time","example": "2023-04-01 10:00:00",'
                elif openapi_type == "date":
                    openapi_type = "string"
                    openapi_format = '"format": "date","example": "2023-04-01",'
                elif openapi_type == "enum":
                    openapi_type = "string"
                    emun = f'"enum":{enums_argument},'
                elif openapi_type == "decimal":
                    openapi_type = "string"
                    openapi_format = '"example": "12.99",'
                elif openapi_type == "varchar":
                    openapi_type = "string"
                    openapi_format = f'"maxlength": {length},' if length else "" 
                    
   
                    
                if column_name != "id":
                    api_schema += f'    "{column['name']}": {{"type": "{openapi_type}",{emun}{openapi_format}"description": "{column_comment_safe}","required": {'False' if nullable or column_name == "id" else 'True'}}},\n'
                
                input_type = "text"
                if (
                    column_type
                    in [
                        "TINYINT",
                        "SMALLINT",
                        "MEDIUMINT",
                        "INTEGER",
                        "BIGINT",
                        "INT",
                        "FLOAT",
                        "DOUBLE",
                        "DECIMAL",
                        "NUMERIC",
                        "YEAR",
                    ]
                    and "switch" not in column_name
                    and "state" not in column_name
                    and "id" != column_name
                    and "_id" not in column_name
                    and "pid" != column_name 
                    and "parent_id" != column_name
                ):
                    input_type = "number"
                    step = 0.01 if column_type == "DECIMAL" else 1
                    
                    input_field = f'<input type="{input_type}" class="form-control" step="{step}" id="{column_name}" name="{column_name}" value="{{{{value.{column_name}}}}}" {maxlength} placeholder="{{{{_(\'{column_comment}\')}}}}"  {required}/>\n'
                    
                elif (column_type == "DATETIME" or column_type == "TIMESTAMP"):
                    if (column_name != "created_at" and column_name != "updated_at"):
                        input_type = "datetime"
                        input_field = f'<input type="{input_type}" class="form-control" id="{column_name}" name="{column_name}" value="{{{{value.{column_name}}}}}" placeholder="{{{{_(\'{column_comment}\')}}}}"  {required}/>\n'
                        
                        add_js_code += f"""
                        <script>   
                            document.addEventListener("DOMContentLoaded", function () {{
                                const input = document.getElementById("{column_name}");
                                let initialDate;
                                const existingValue = input.value.trim();
                                if (existingValue !== "") {{
                                    initialDate = flatpickr.parseDate(existingValue, "Y-m-d H:i:s");
                                }} else {{
                                    initialDate = new Date();
                                }}
                                flatpickr("#{column_name}", {{
                                    enableTime: true,
                                    dateFormat: "Y-m-d H:i:s",
                                    defaultDate: initialDate
                                }});
                            }}); 
                        </script>
                        """
                elif column_type == "DATE":
                    input_type = "date"
                    input_field = f'<input type="{input_type}"  class="form-control"id="{column_name}" name="{column_name}" value="{{{{value.{column_name}}}}}" placeholder="{{{{_(\'{column_comment}\')}}}}"  {required}/>\n'

                    add_js_code += f"""
                    <script>   
                        document.addEventListener("DOMContentLoaded", function () {{
                            const input = document.getElementById("{column_name}");
                            let initialDate;
                            const existingValue = input.value.trim();
                            if (existingValue !== "") {{
                                initialDate = flatpickr.parseDate(existingValue, "Y-m-d");
                            }} else {{
                                initialDate = new Date();
                            }}
                            flatpickr("#{column_name}", {{
                                disableMobile : true,
                                dateFormat: "Y-m-d",
                                defaultDate: initialDate
                            }});
                        }}); 
                    </script>
                    """
                elif column_type == "TEXT":
                    input_field = f'<textarea class="form-control" name="{column_name}" id="{column_name}" cols="30" rows="10" {required}>{{{{value.{column_name}}}}}</textarea>\n'
                    add_js_code += f"""
                    <script>   
                        document.addEventListener("DOMContentLoaded", function () {{
                        let textarea = document.getElementById('{column_name}');
                        let options = {{
                            selector: '#{column_name}',
                            height: 300,
                            menubar: false,
                            statusbar: false,
                            plugins: [],
                            toolbar: 'undo redo | formatselect | ' +
                            'bold italic backcolor | alignleft aligncenter ' +
                            'alignright alignjustify | bullist numlist outdent indent | ' +
                            'removeformat',
                            content_style: 'body {{ font-family: -apple-system, BlinkMacSystemFont, San Francisco, Segoe UI, Roboto, Helvetica Neue, sans-serif; font-size: 14px; -webkit-font-smoothing: antialiased; }}',
                            setup: function(editor) {{
                                editor.on('change', function(e) {{
                                    textarea.value = editor.getContent();
                                }});
                            }}
                        }}
                        if (localStorage.getItem("tablerTheme") === 'dark') {{
                            options.skin = 'oxide-dark';
                            options.content_css = 'dark';
                        }}
                        tinyMCE.init(options);
                        }}) 
                    </script>
                    """
                elif column_type == "ENUM":
                    option_str = "<option value>{{_('Pealse Select')}}</option>\n"
                    if len(enums_argument) > 0:
                        option_str += f" {{% if value.{column_name} %}}\n"
                        for emun in enums_argument:
                            option_str += f"  <option value=\"{emun}\" {{% if value.{column_name}=='{emun}' %}} selected {{% endif %}}>{{{{_('{emun.title()}')}}}}</option>\n"
                        option_str += f" {{% else %}}\n"
                        for emun in enums_argument:
                            option_str += f"  <option value=\"{emun}\" {{% if {default}=='{emun}' %}} selected {{% endif %}}>{{{{_('{emun.title()}')}}}}</option>\n"
                        option_str += f" {{% endif %}}\n"
                    input_field = (
                        f'<select id="{column_name}" type="text" class="form-select" name="{column_name}">\n'
                        f"  {option_str}\n"
                        f"</select>"
                    )
                elif column_type == "SET":
                    check_str = ""
                    if len(sets_argument) > 0:
                        for set_val in sets_argument:
                            check_str += f"""  <label class=\"form-check form-check-inline\">
                                    <input class=\"form-check-input\" type=\"checkbox\" name="{column_name}[]" value=\"{set_val}\" {{% if value.{column_name} != None and value.{column_name} != '' and '{set_val}' in value.{column_name} %}}checked{{% endif %}}>
                                    <span class=\"form-check-label\">{{{{_('{set_val.title()}')}}}}</span>
                                </label>"""
                    input_field = f"<div>\n" f"  {check_str}" f"</div>\n"
                elif re.search(r"(?:^|_)image$", column_name.lower()) or re.search(
                    r"(?:^|_)images$", column_name.lower()
                ):
                    allowed_extensions = ".jpg,.jpeg,.png,.gif"
                    input_field = f'<input class="form-control upload" type="file" {"" if not "image" in column_name else "multiple"} data-allowed-extensions="{allowed_extensions}" data-upload-type="image" /><div class="images-container row g-2"></div><input type="hidden" id="{column_name}" name="{column_name}" value="{{{{value.{column_name}}}}}" />'
                elif column_name.endswith("_file") or column_name.endswith("_file"):
                    allowed_extensions = ".docx,.html,.doc"
                    input_field = f'<input class="form-control upload" type="file" {"" if not "file" in column_name else "multiple"} data-allowed-extensions="{allowed_extensions}"  data-upload-type="file"/><div class="images-container row g-2"></div><input type="hidden" id="{column_name}" name="{column_name}" value="{{{{value.{column_name}}}}}" />'
                elif "range" in column_name:
                    input_type = "text"
                    input_field = f'<input type="{input_type}" class="form-control" id="{column_name}" name="{column_name}" value="{{{{value.{column_name}}}}}" placeholder="{{{{_(\'{column_comment}\')}}}}"  {required}/>\n'
                    add_js_code += f"""
                    <script>   
                        document.addEventListener("DOMContentLoaded", function () {{
                            flatpickr("#{column_name}", {{
                                mode: "range",
                                disableMobile : true,
                                dateFormat: "Y-m-d H:i:s",
                                conjunction: " - "
                            }});
                        }}); 
                    </script>
                    """
                elif "switch" in column_name:
                    input_type = "checkbox"
                    input_field = f'<label class="form-check form-switch"><input type="hidden" id="{column_name}Hidden" name="{column_name}" value="0"/><input type="{input_type}"  class="form-check-input " id="{column_name}" name="{column_name}" value="1" {{% if 1 == value.{column_name} %}}checked{{% endif %}} {required}/></label>\n'
                elif "state" in column_name:
                    input_type = "radio"
                    pairs = column_comment[column_comment.find(": ") + 2 :].split(", ")
                    state_dict_list = [
                        {
                            "value": int(pair.split("=")[0]),
                            "description": pair.split("=")[1].strip(),
                        }
                        for pair in pairs
                    ]
                    html_content = ""
                    for state in state_dict_list:
                        checked_attr = "checked" if state["value"] == 1 else ""
                        html_content += f'<label for="option-{state["value"]}" class="form-check form-check-inline"><input type="{input_type}" class="form-check-input" id="option-{column_name}-{state["value"]}" name="{column_name}" value="{state["value"]}" {checked_attr}><span class="mx-1">{state["description"]}</span></label>'
                    input_field = html_content
                elif "id" == column_name:
                    input_field = f'<input class="form-control" type="hidden" id="{column_name}" name="{column_name}"  value="{{{{value.{column_name}}}}}" placeholder="{{{{_(\'{column_comment}\')}}}}"  {required}/>{{{{value.{column_name}}}}}\n'
                elif "password" in column_name:
                    input_field = f'<input class="form-control" type="text" id="{column_name}" name="{column_name}"  value="" placeholder="{{{{_(\'{column_comment}\')}}}}" {required}/>\n'
                
                elif ("pid" == column_name or "parent_id" == column_name): 
                    option_str = "<option value='0' selected>{{_('Pealse Select')}}</option>\n"
                    
                    input_field = (
                        f'<select id="{column_name}" class="form-select ajax" data-model="{model_name}" data-title="name" data-value="{{{{value.{column_name}}}}}" name="{column_name}">\n'
                        f"  {option_str}\n"
                        f"</select>"
                    )
                
                elif column_name.endswith("_id"):
                    model = column_name.replace("_id", "")
                    option_str = "<option value>{{_('Pealse Select')}}</option>\n"
                    input_field = (
                        f'<select id="{column_name}" class="form-select ajax" data-model="{model}" data-title="name" data-value="{{{{value.{column_name}}}}}" name="{column_name}">\n'
                        f"  {option_str}\n"
                        f"</select>"
                    )
                elif column_name.endswith("_ids"):
                    model = column_name.replace("_ids", "")
                    option_str = "<option value>{{_('Pealse Select')}}</option>\n"
                    input_field = (
                        f'<select id="{column_name}" class="form-select ajax" data-model="{model}" data-title="name" data-value="{{{{value.{column_name}}}}}" name="{column_name}[]" multiple>\n'
                        f"  {option_str}\n"
                        f"</select>"
                    )
                else:
                    input_field = f'<input class="form-control" type="{input_type}" id="{column_name}" name="{column_name}"  value="{{{{value.{column_name}}}}}" placeholder="{{{{_(\'{column_comment}\')}}}}"  {maxlength} {required}/>\n'
                if (
                    column_name != "id"
                    and column_name != "created_at"
                    and column_name != "updated_at"
                ):
                    replace_template_add_tpl_form_body += f'<div class="mb-[20px]">\n    <label class="form-label" for="{column_name}" {required}>{{{{_(\'{button_text}\')}}}}</label>\n   {input_field}  </div>\n'

                if column_name == "id":
                    replace_template_edit_tpl_form_body += f'<div class="mb-[20px]">\n    <label class="form-label" for="{column_name}" {required}>{{{{_(\'ID\')}}}}</label>\n   {input_field}  </div>\n'
                else:
                    if column_name != "created_at" and column_name != "updated_at":
                        replace_template_edit_tpl_form_body += f'<div class="mb-[20px]">\n    <label class="form-label" for="{column_name}" {required}>{{{{_(\'{button_text}\')}}}}</label>\n   {input_field}  </div>\n'
                if column_name == "id":
                    replace_template_index_tpl_table_ths += f'<th><input class="form-check-input m-0 align-middle select-all" type="checkbox" aria-label="Select invoice"></th><th><button class="table-sort" data-sort="sort-name">{{{{_(\'{button_text}\')}}}}</button></th>\n'

                    replace_template_index_tpl_table_tds += f'<td><input class="form-check-input m-0 align-middle id-checkbox" type="checkbox" aria-label="Select invoice" value="{{{{value.{column_name}}}}}"></td><td class="sort-name">{{{{ value.{column_name} }}}}</td>\n'

                    replace_template_index_tpl_table_details += f'<div class="row mb-3 align-items-end"><div class="col-auto fw-bold"> {{{{_("{button_text}")}}}}</div><div class="col">{{{{ value.{column_name} }}}} </div></div>'

                    js_code += f'if ($("#id").val() != undefined && $("#id").val() != 0 && $("#id").val() != "") {{\n'
                    js_code += f"    formData.append( '{column_name}', $( \"#{column_name}\" ).val() );\n"
                    js_code += "}\n"
                else:
                    if fields == "*" or fields == None:
                        replace_template_index_tpl_table_ths += (
                            f"<th>{{{{_('{button_text}')}}}}</th>\n"
                        )

                        replace_template_index_tpl_table_tds += f'<td class="sort-name">{{{{ value.{column_name} }}}}</td>\n'

                    elif column_name in fields.split(","):
                        replace_template_index_tpl_table_ths += (
                            f"<th>{{{{_('{button_text}')}}}}</th>\n"
                        )
                        replace_template_index_tpl_table_tds += f'<td class="sort-name">{{{{ value.{column_name} }}}}</td>\n'
                    replace_template_index_tpl_table_details += f'<div class="row mb-3 align-items-end"><div class="col-auto fw-bold"> {{{{_("{button_text}")}}}}</div><div class="col">{{{{ value.{column_name} }}}} </div></div>'
                    if column_type == "SET":
                        js_code += f"var {column_name}SelectedValues = [];\n"
                        js_code += f'$(\'input[type="checkbox"][name="{column_name}"]:checked\').each(function() {{\n'
                        js_code += (
                            f"    {column_name}SelectedValues.push(this.value);\n"
                        )
                        js_code += f"}});\n"
                        js_code += f"var {column_name}SeparatedValues = {column_name}SelectedValues.join(',');\n"
                        js_code += f"formData.append('{column_name}', {column_name}SeparatedValues);\n"
                    elif "switch" in column_name:
                        js_code += f'formData.append( \'{column_name}\', $( "#{column_name}" ).is(":checked") ? 1 : 0 );\n'
                    else:
                        if column_name != "created_at" and column_name != "updated_at":
                            js_code += f"formData.append( '{column_name}', $( \"#{column_name}\" ).val() );\n"
                table_fields.append(column_name)
            data = {}
            
            model_tpl_content = model_tpl_content.replace(
                "%%model_class%%", model_code
            ).replace("%%model_name%%", model_name)
           
            schema_tpl_content = schema_tpl_content.replace(
                "%%schema_class%%", schema_code
            ).replace("%%model_name%%", model_name) 

            template_index_tpl_content = (
                template_index_tpl_content.replace(
                    "%%table_ths%%", replace_template_index_tpl_table_ths
                )
                .replace("%%model_name%%", model_name)
                .replace("%%model_class_name%%", model_class_name)
                .replace("%%route%%", route_str)
                .replace("%%table_tds%%", replace_template_index_tpl_table_tds)
                .replace("%%table_details%%", replace_template_index_tpl_table_details)
                .replace("%%js_file_name%%", self.table_name)
            )
            data["template_index_code"] = template_index_tpl_content

            template_add_tpl_content = (
                template_add_and_edit_tpl_content.replace(
                    "%%form_body%%", replace_template_add_tpl_form_body
                )
                .replace("%%model_class_name%%", model_class_name)
                .replace("%%model_name%%", model_name)
                .replace("%%js_file_name%%", self.table_name)
                .replace("%%add_js%%", add_js_code)
                .replace("%%route%%", route_str)
            )

            template_edit_tpl_content = (
                template_add_and_edit_tpl_content.replace(
                    "%%form_body%%", replace_template_edit_tpl_form_body
                )
                .replace("%%model_class_name%%", model_class_name)
                .replace("%%model_name%%", model_name)
                .replace("%%js_file_name%%", self.table_name)
                .replace("%%add_js%%", add_js_code)
                .replace("%%route%%", route_str)
            )

            js_tpl_content = (
                js_tpl_content.replace("%%form_body%%", js_code)
                .replace("%%route%%", route_str)
                .replace("%%model_name%%", model_name)
                .replace("%%model_class_name%%", model_class_name)
            )

            views_tpl_content = (
                views_tpl_content.replace("%%route%%", route_str)
                .replace("%%model_name%%", model_name)
                .replace("%%model_class_name%%", model_class_name)
                .replace("%%file_name%%", model_name)
                .replace("%%route_name%%", model_name.replace("_", "/"))
            )

            api_tpl_content = (
                api_tpl_content.replace("%%route%%", route_str)
                .replace("%%model_name%%", model_name)
                .replace("%%model_class_name%%", model_class_name)
                .replace("%%api_schema%%", api_schema)
            )
            route_tpl_content = (
                route_tpl_content.replace("%%route%%", route_str)
                .replace("%%model_name%%", model_name)
                .replace("%%model_class_name%%", model_class_name)
            )
            data["table_fields"] = table_fields
            data["template_add_code"] = template_add_tpl_content
            data["template_edit_code"] = template_edit_tpl_content
            data["views_code"] = views_tpl_content
            data["api_code"] = api_tpl_content
            data["js_code"] = js_tpl_content
            data["model_code"] = model_tpl_content
            data["schema_code"] = schema_tpl_content
            data["route_code"] = route_tpl_content
        except ValueError:
            return {}
        return data
