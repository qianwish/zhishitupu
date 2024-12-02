#cd Online_Learning
#python manage.py runserver 0.0.0.0:8000
# -*- coding: utf-8 -*-
from flask import Flask, request
from ModelProcess import *
from Service import *
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*' # 通过设置Access-Control-Allow-Origin实现跨域，“*”表示允许所有的域名都可以访问
    response.headers['Access-Control-Allow-Methods'] = 'PUT,GET,POST,DELETE' # 设置允许的请求类型
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'  # 设置允许的请求头字段，'Content-Type,Authorization'表示参数的定义将被忽略
    return response


def main():
    app = Flask(__name__)  # 初始化Flask实例
    app.after_request(after_request)  # 更改responese的请求头信息
    query_process = ModelProcess()  # 实例化ModelProcess类
    service = Service()  # 实例化Service类
    neo4j = Neo4j()  # 实例化Neo4j类

    @app.route('/')  # 定义路由，当地址是根路径时，则执行以下函数
    def index():
        return "index"

    # 定义路由规则，获取一门课程的所有先修课程
    @app.route('/course/adv', methods={"GET"})
    def get_adv_courses():
        course_name = request.form.get('course_name')  # 获取课程名称
        if not course_name:  # 如果没有获取到课程名称
            return ResponseData(ExceptionMsg.REQUIRE_COURSE_NAME).encode()  # 返回响应信息
        return service.get_adv_courses(course_name)  # 请求Service.py中的get_course_info函数来获取查询结果

    # 定义路由，获取课程的详细信息
    @app.route('/course/info', methods={"GET"})
    def get_course_info():
        course_name = request.form.get('course_name')  # 获取课程名称
        if not course_name:  # 如果没有获取到课程名称
            return ResponseData(ExceptionMsg.REQUIRE_COURSE_NAME).encode()  # 返回响应信息
        return service.get_course_info(course_name)  # 请求Service.py中的get_course_info函数来获取查询结果

    # 定义路由，获取某课程的授课教师
    @app.route('/course/teacher', methods={"GET"})
    def get_course_teacher():
        course_name = request.form.get('course_name')
        if not course_name:
            return ResponseData(ExceptionMsg.REQUIRE_COURSE_NAME).encode()
        return service.get_course_teacher(course_name)  # 请求Service.py中的get_course_info函数来获取查询结果

    # 定义路由，根据用户输入的问题进行搜索
    @app.route('/query')
    def query():

        # 获取question参数
        question = request.args.get('question')  # 获取用户输入的问题
        question = question.upper()  # 将小写字母替换为大写字母
        if not question:  # 如果没有获取到问题
            return ResponseData(
                ExceptionMsg.REQUIRE_QUESTION).encode()  # 返回信息，如：{"code": "0006", "message": "需要问题参数(question)"}
        question_index, pattern = query_process.analysis_query(question)  # 将用户问题转化成系统能够识别的表示

        data = {'type': question_index}  # 问题的类别
        if question_index == 1:  # 如果用户想查询某课程的先修课
            course_name = pattern[0]  # 课程名称
            course = neo4j.get_course_node(course_name)  # 在Neo4j图数据库中查询课程节点
            if not course:
                return ResponseData(ExceptionMsg.NONEXISTENT_COURSE).encode()
            data['result'] = neo4j.get_course_adv(course_name)  # 查询该课程的先修课程
        # question_index == 8，代表想问老师姓名类的问题
        elif question_index == 8:  # 如果用户想查询某门课程的授课教师
            course_name = pattern[0]  # 课程名称
            course = neo4j.get_course_node(course_name)
            if not course:
                return ResponseData(ExceptionMsg.NONEXISTENT_COURSE).encode()
            teacher = neo4j.get_course_teacher(course_name)  # 查询授课教师
            if not teacher:
                return ResponseData(ExceptionMsg.NO_INFO_ABOUT_THIS_COURSE).encode()
            data['result'] = teacher['name']
        else:
            course_name = pattern[0]  # 课程名称
            course_info = neo4j.get_course_node(course_name)
            if question_index == 0:  # 课程介绍
                data['result'] = course_info['details']
            elif question_index == 2:  # 开课学期
                data['result'] = course_info['semester']
            elif question_index == 3:  # 选修/必修
                data['result'] = course_info['optional']
            elif question_index == 4:  # 学分
                data['result'] = course_info['credit']
            elif question_index == 5:  # 学时
                data['result'] = course_info['credit_hour']
            elif question_index == 6:  # 课程编号
                data['result'] = course_info['id']
            elif question_index == 7:  # 英文名称
                data['result'] = course_info['english_name']
            else:
                return ResponseData(
                    ExceptionMsg.QUESTION_IDENTIFICATION_WRONG).encode()  # question_index的值不在模板中，返回异常信息为"0007", "识别问题出错"
        return ResponseData(data=data).encode()

    app.run(debug=True)  # 启动flask


if __name__ == '__main__':
    main()
#http://localhost:8000/