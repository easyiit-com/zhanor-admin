from marshmallow import Schema, fields, post_load, pre_load

from app.plugins.demo.models.demo import Demo

class DemoSchema(Schema):
    id = fields.Integer(dump_only=True) 
    user_id = fields.Integer() 
    admin_id = fields.Integer() 
    category_id = fields.Integer() 
    category_ids = fields.String(description="The greeting msg")
    tags = fields.String()
    week = fields.String(enum=['monday', 'tuesday', 'wednesday'])
    flag = fields.String(enum=['hot', 'index', 'recommend'])
    genderdata = fields.String(enum=['male', 'female'])
    hobbydata = fields.String(enum=['male', 'female'])
    title = fields.String()
    content = fields.String() 
    image = fields.String()
    images = fields.String()
    attachfile = fields.String()
    keywords = fields.String()
    description = fields.String()
    city = fields.String()
    json = fields.String()
    multiplejson = fields.String()
    price = fields.Decimal(default = '0' ) 
    views = fields.Integer(default = '0' ) 
    workrange = fields.String()
    startdate = fields.Date() 
    activitytime = fields.DateTime() 
    year = fields.DateTime() 
    times = fields.Time() 
    refreshtime = fields.DateTime() 
    createtime = fields.DateTime() 
    updatetime = fields.DateTime() 
    deletetime = fields.DateTime() 
    weigh = fields.Integer(default = '0' ) 
    switch = fields.Integer(default = '0' ) 
    status = fields.String(enum=['normal', 'hidden'])
    state = fields.Integer(default = '0' ) 


 
    @post_load
    def make_demo(self, data, **kwargs):
        # 如果有需要，可以在加载数据后执行一些操作
        return Demo(**data)