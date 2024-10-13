from marshmallow import Schema, fields, post_load, pre_load

%%schema_class%%

 
    @post_load
    def make_demo(self, data, **kwargs):
        # 如果有需要，可以在加载数据后执行一些操作
        return Demo(**data)