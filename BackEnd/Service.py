from ExceptionMsg import ExceptionMsg
from ResponseData import ResponseData
from neo4j import Neo4j


class Service:
    def __init__(self):
        self.neo4j = Neo4j()  # 实例化Neo4j类

    # 定义查询先修课程的返回值
    def get_adv_courses(self, course_name):
        course = self.neo4j.get_course_node(course_name)  # 调用get_course_node()方法，根据课程名称查询课程节点
        if not course:  # 如果没有查询到课程节点
            return ResponseData(ExceptionMsg.NONEXISTENT_COURSE).encode()  # 返回信息，{"code": "0001", "message": "课程不存在"}
        data = self.neo4j.get_course_adv(course_name)  # 调用get_course_adv()方法，查询先修课程
        response_data = ResponseData(ExceptionMsg.SUCCESS, data=data).encode()  # 以json格式返回响应信息及查询到的先修课程结果
        return response_data

    # 定义查询课程详细信息的返回值
    def get_course_info(self, course_name):
        course = self.neo4j.get_course_node(course_name)  # 调用get_course_node()方法，根据课程名称查询课程节点
        if not course:  # 如果没有查询到课程节点
            return ResponseData(ExceptionMsg.NONEXISTENT_COURSE).encode()  # 返回信息，{"code": "0001", "message": "课程不存在"}
        return ResponseData(data=course).encode()  # 以json格式返回响应信息及查询到的课程的详细信息

    # 定义查询授课教师的返回值
    def get_course_teacher(self, course_name):
        course = self.neo4j.get_course_node(course_name)  # 调用get_course_node()方法，根据课程名称查询课程节点
        if not course:  # 如果没有查询到课程节点
            return ResponseData(ExceptionMsg.NONEXISTENT_COURSE).encode()  # 返回信息，{"code": "0001", "message": "课程不存在"}
        teacher = self.neo4j.get_course_teacher(course_name)  # 调用get_course_teacher()方法，查询某课程的授课教师
        if not teacher:  # 如果没有查询到
            return ResponseData(
                ExceptionMsg.NO_INFO_ABOUT_THIS_COURSE).encode()  # 返回信息，{"code": "0003", "message": "没有这门课程的教师信息"}
        return ResponseData(data=teacher).encode()

if __name__ == '__main__':
        service = Service()
        course_name = "算法分析与设计"
        print(service.get_adv_courses(course_name))
        print(service.get_course_info(course_name))
        print(service.get_course_teacher(course_name))