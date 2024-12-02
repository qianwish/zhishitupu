import os
import re
import xml.dom.minidom
from pyquery import PyQuery as pq
doc = xml.dom.minidom.Document()
def init_xml():
    global doc # 定义全局变量doc
    root = doc.createElement("root") # 创建"root"根节点
    doc.appendChild(root) # appendChild方法在doc节点的子节点列表末添加新的子节点"root"，一般需要createElement和appendChild搭配使用

    # 课程名字对应的标签
    courses_name_xml = doc.createElement("courses")# 创建"courses"节点
    root.appendChild(courses_name_xml) # 在"root"节点的子节点列表末添加新的子节点"courses"

    # 先修课程对应的标签
    adv_courses_xml = doc.createElement("adv-course")# 创建"adv-course"节点
    root.appendChild(adv_courses_xml) # 在"root"节点的子节点列表末添加新的子节点"adv-course"
    return courses_name_xml, adv_courses_xml # 课程详细信息的xml对象和先修课程的xml对象

def convert_adv_course(courses_info, course_name_to_index):
    adv_courses_dict = {} # 创建存放先修课程的字典
    for i, course_info in enumerate(courses_info): # 遍历某课程的全部信息
        course_adv = course_info['advance'] # 获取当前课程的先修课程
        if course_adv == "无": # 如果没有先修课程，则跳出本次循环
            continue
        for course_name in course_name_to_index.keys(): # 遍历所有课程的名称
            if course_name not in course_adv: # 如果课程名称不在先修课程中，则跳出循环
                continue
            if i not in adv_courses_dict.keys(): # 如果i代表的先修课程下标不在adv_courses_dict.keys中 ，eg. adv_courses_dict={1: [6, 9]}
                adv_courses_dict[i] = [course_name_to_index[course_name]] # 优先进行替换，构建成{课程:[先修课1，先修课2]}的字典
            else:
                adv_courses_dict[i].append(course_name_to_index[course_name])# 否则就直接添加入字典内构建成{课程:[先修课1，先修课2]}的字典
    print(adv_courses_dict)
    return adv_courses_dict # 返回先修课程字典(用一门课的下标指代该门课程)

def save_course_adv_to_xml(courses_info, course_name_to_index, courses_adv_xml):
    adv_course_dict = convert_adv_course(courses_info=courses_info, course_name_to_index=course_name_to_index) # 将先修课程信息转化成索引表示的字典
    for pre_course, adv_courses in adv_course_dict.items(): # pre_course某课程课程下标，adv_courses是先修课程下标
        for adv_course in adv_courses: # 遍历某课程的所有先修课程
            node = doc.createElement("item") # 创建名称为“item”的结点
            courses_adv_xml.appendChild(node) # 将“item”的结点添加到父节点下
            create_node(node_parent=node, node_name="adv", node_content=pre_course)# 创建当前课程的结点
            create_node(node_parent=node, node_name="pre", node_content=adv_course) # 创建先修课程的结点
    print("成功为先修课程创建为xml节点")

def create_node(node_parent, node_name, node_content=None):
    global doc # global全局定义变量doc
    node_adv = doc.createElement(node_name) # 创建名称为node_name的节点
    if node_content is not None:# 如果节点的内容不为空
        node_adv.appendChild(doc.createTextNode(str(node_content)))# 给叶子节点node_name设置一个文本节点，用于显示文本内容
    node_parent.appendChild(node_adv) # 将node_name节点添加到父节点中
    return node_adv
def save_xml_to_file():
    global doc # global全局定义变量doc
    path = os.path.join('../', 'spider/data.xml') # 写入文件的路径
    fp = open(path, 'w')# 创建文件data.xml，并准备写入
    doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="UTF-8")# 把xml内存对象写到文件
    print('成功将xml节点存入'+path+'中')
def parse_html(html_name):
    pyquery_html = pq(filename=html_name,encoding='utf-8')# 将html文件初始化
    li = pyquery_html('body > div.WordSection2 > table,p') # 提取课程的信息
    print(li.text())
    # 使用正则法提取以下数据，放入courses_temp变量中
    courses_temp = re.findall("课程名称\n(.*?)"  
                              "\n课程编号\n(.*?)"  
                              "\n(.*?)"  # 英文名称 
                              "\n学分/学时\n(.*?)/(.*?)"
                              "\n(.*?)"  # 选修还是必修
                              "\n开课学期\n(.*?)\n.*?"
                              "\n先修课程\n(.*?)课程名称.*?二、课程教学目标(.*?)三、课程与支撑的毕业要求.*?执笔人:(.*?)审核人", li.text(),# 课程详情
                              #flags是正则的标识符号，re.DOTALL代表匹配所有
                              flags=re.DOTALL)
    courses_info = [] # 定义一个空列表，用于存储所有课程的信息
    # 对课程信息进行数据清洗，并将数据保存为字典格式
    for item in courses_temp:
        courses_info.append({
            # 课程名称
            "name": "".join(item[0].strip('中文：').split()).replace('-','',-1).replace('/','',-1),
            # 课程编号
            "id": "".join(item[1].strip("").split()),
            # 英文名称
            "english_name": item[2].strip("英文：").replace(u'\xa0', u' '),
            # 学分
            "credit": "".join(item[3].strip("").split()),
            # 学时
            "credit_hour": "".join(item[4].strip("").split()),
            # # 选修/必修
            "optional": 'y' if '必修（）' in "".join(item[5].strip("").split())
                .replace(u'\u2a57', u'').replace(u'\uf0fc', u'') else 'n',
            # 开课学期
            "semester": "".join(item[6].strip("").split()),
            # 先修课程
            "advance": "".join(item[7].strip("").split()),
            # 课程详细信息
            "details": "".join(item[8].strip("").split()),
            # 课程老师
            "teacher": "".join(item[9].strip("").split())
        })
    print("成功解析html中的课程信息,课程总数为:", len(courses_info))
    return courses_info
def save_courses_info_to_xml(courses_info):
    courses_info_xml, adv_courses_xml = init_xml()# 初始化xml文件对象
    course_name_to_index = {}
    for i, course_info in enumerate(courses_info):# 遍历所有的课程信息
        course_node_xml = create_node(node_parent=courses_info_xml, node_name="course") # 创建名称为“course”的节点，用于存放所有课程的信息
        for key, value in course_info.items(): # 遍历某门课程的信息
            if key == 'advance': # 如果是先修课程信息，则跳出本次循环
                continue
            create_node(node_parent=course_node_xml, node_name=str(key), node_content=str(value)) # 创建节点
        course_name_to_index[course_info['name']] = i # 将课程名称和对应的下标存储成一个dict
    print("成功为课程的信息(除先修课程)创建为xml节点")
    save_course_adv_to_xml(courses_info, course_name_to_index, adv_courses_xml)# 为先修课程创建节点
    save_xml_to_file()# 将xml对象写入文件
def main():
    courses_info = parse_html("hello.html")# 解析xml
    save_courses_info_to_xml(courses_info)# 将解析出的课程信息存入xml中

if __name__ == '__main__':
    main()