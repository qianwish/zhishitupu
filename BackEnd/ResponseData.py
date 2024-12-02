import json
from ExceptionMsg import ExceptionMsg

class ResponseData:
    def __init__(self, exceptionMsg=ExceptionMsg.SUCCESS, data=None):
        self.code = exceptionMsg.get_code() # 获取响应码
        self.message = exceptionMsg.get_message() # 获取响应信息
        self.data = data # 查询结果

    def encode(self): # 将数据转化为json格式
        return json.dumps(self, cls=ResponseDataEncoder, ensure_ascii=False)

class ResponseDataEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, ResponseData): # 判断obj是不是ResponseData类型的变量，即是不是ResponseData类的返回值
            result = {
                "code": obj.code, # 响应码
                "message": obj.message, # 响应信息
                "data": obj.data} # 查询结果
            #查看返回结果是否为空
            if result['data'] is None: # 如果查询结果为空
                result.pop('data') # 则删除‘data’参数
            return result
        return json.JSONEncoder.default(self, obj) # 返回json格式的数据，如：{"code": "0005", "message": "该教师不存在"}

if __name__ == '__main__':
    responseData = ResponseData(
    )
    print(responseData.encode())