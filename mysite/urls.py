"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect, HttpResponse
from .sqlhelper import Manage_Info
import json


def add_student(request):
    """添加学生信息"""
    if request.method == "GET":
        return render(request, "add_student.html")
    else:
        # 获取学生信息
        student_info = request.POST
        # 判断该学生是否已被录入
        manage = Manage_Info()
        if manage.student_exists(student_info.get('student_id')):
            return HttpResponse("该学生已存在")
        # 判断班级是否存在
        if not manage.class_exists(student_info.get('class_name')):
            return HttpResponse("不存在 %s 班级" %student_info.get('class_name'))
        # 将学生录入系统
        try:
            manage.add_student_info(student_info)
        except Exception as ret:
            return HttpResponse(ret)
        return redirect("/student/")



def del_student(request):
    """删除学生信息"""
    _id =  request.GET.get('nid')
    manage = Manage_Info()
    try:
        manage.del_student_info(_id)
    except Exception as ret:
        return HttpResponse(ret)
    else:
        return redirect("/student/")


def edit_student(request):
    """编辑学生信息"""
    # 1、收到编辑信息的请求
    manage = Manage_Info()
    if request.method == "GET":
        _id = request.GET.get('nid')
        student_info = manage.get_student_info(id=_id)
        return render(request, "edit_student.html", {"content":student_info})
    else:
        # 对编辑后的信息进行提交
        _id = request.GET.get('nid')
        # 判断得到的信息是否合法
        # 判断班级是否指定
        if request.POST.get('class_name'):
            # 判断班级是否在数据库中记录
            if not manage.class_exists(request.POST.get('class_name')):
                return HttpResponse("班级不存在")
        new_info = dict(
            student_id=request.POST.get('student_id'),
            name=request.POST.get('name'),
            class_name=request.POST.get('class_name')
        )
        manage.update_student_info(_id, new_info)
        return redirect("/student/")


def student_info(request):
    """学生信息"""
    manage = Manage_Info()
    student_infos = manage.get_student_info()
    class_infos = manage.get_class_info()
    return render(request,"student_info.html",
                  {"content":student_infos, "classes":class_infos}
                  )

def add_teacher(request):
    """添加教师信息"""
    manage = Manage_Info()
    ret = {"status": True, "message": None}
    if request.method == "GET":
        return render(request, "add_teacher.html")
    else:
        # 判断该教师职工号是否存在于数据库中
        if manage.teacher_exists_by_id(request.POST.get('job_id')):
            ret = {"status": False, "message": "职工号重复，请重新输入"}
            return HttpResponse(json.dumps(ret))
        # 获取前端发送过来的新教师的信息
        teacher_info = dict(
            job_id=request.POST.get('job_id'),
            name=request.POST.get('name'),
            class_list=request.POST.get('class_list')
        )
        manage.add_teacher_info(teacher_info)
        return HttpResponse()

def del_teacher(request):
    """删除教师信息"""
    # 获取所要删除的教师序号
    _id = request.GET.get('nid')
    manage = Manage_Info()
    try:
        manage.del_teacher_info(_id)
    except Exception as ret:
        return HttpResponse(str(ret))
    else:
        return redirect("/teacher/")

def edit_teacher(request):
    """编辑教师信息"""
    manage = Manage_Info()
    if request.method == 'GET':
        _id = request.GET.get('nid')
        teacher_info = manage.get_teacher_info(id=_id)
        return render(request, 'edit_teacher.html', {'content':teacher_info})
    else:
        # 获取所编辑教师的序号
        _id = request.GET.get('nid')
        # 获取编辑后的信息
        new_info = dict(
            name=request.POST.get('name'),
            job_id=request.POST.get('job_id')
        )
        # 更新教师信息
        manage.update_teacher_info(_id, new_info)
        return redirect("/teacher/")

def teacher_info(request):
    """展示所有教师信息"""
    manage = Manage_Info()
    all_teacher_info = manage.get_teacher_info()
    all_class = manage.get_class_info()
    return render(request,
                  "teacher_info.html",
                  {"content":all_teacher_info, "classes": all_class}
                  )

def class_info(request):
    """展示所有班级信息"""
    manage = Manage_Info()
    all_class_info= manage.get_class_info()
    all_teacher_info = manage.get_teacher_info()
    return render(request, "class_info.html" ,{'content':all_class_info,
                                               'tech_content':all_teacher_info})

def get_classesinfo(request):
    manage = Manage_Info()
    ret = {"status": True, "message": None}
    try:
        classes_info = manage.get_class_info()
    except Exception:
        ret["status"] = False
        ret["message"] = "出现异常，获取信息失败"
        return HttpResponse(json.dumps(ret))
    else:
        ret["message"] = classes_info
        return HttpResponse(json.dumps(ret))

def add_class(request):
    """添加班级信息"""
    if request.method == 'GET':
        return render(request, "add_class.html")
    else:
        manage = Manage_Info()
        class_info = dict(
            name=request.POST.get('name'),
        )
        manage.add_class_info(class_info)
        return redirect('/class/')

def del_class(request):
    """删除班级信息"""
    manage = Manage_Info()
    _id = request.GET.get('nid')
    manage.del_class_info(_id)
    return redirect("/class/")

def edit_class(request):
    """编辑班级信息"""
    manage = Manage_Info()
    if request.method == 'GET':
        # 获取班级信息
        _id = request.GET.get('nid')
        class_info = manage.get_class_info(_id)
        return render(request, "edit_class.html", {"content":class_info})
    else:
        _id = request.GET.get('nid')
        # 判断该教师是否存在于数据库
        if not manage.teacher_exists_by_name(request.POST.get('teacher_name')):
            return HttpResponse("该教师不存在！")
        new_info = dict(
            name=request.POST.get('name'),
            teacher_name=request.POST.get('teacher_name')
        )
        manage.update_class_info(_id, new_info)
        return redirect("/class/")

def model_add_student(request):
    # 获取学生信息
    manage = Manage_Info()
    student_info = request.POST
    if len(student_info.get("name")) > 0 and \
            len(student_info.get("student_id")) > 0:
        # 判断学生是否被录入
        if manage.student_exists(student_info.get("student_id")):
            return HttpResponse("该学生已被录入，请问重复录入!")
        try:
            manage.add_student_info(student_info)
        except Exception as ret:
            return HttpResponse("录入失败!")
        else:
            return  HttpResponse("OK")
    else:
        if len(student_info.get("name")) == 0:
            return HttpResponse("学生姓名不能为空!")
        else:
            return HttpResponse("学生ID不能为空!")

def model_del_student(request):
    ret = {"status": True, "message": None}
    manage = Manage_Info()
    _id = request.GET.get("nid")
    try:
        manage.del_student_info(_id)
    except Exception as ret:
        ret["message"] = "出现异常，删除失败"
        return HttpResponse(json.dumps(ret))
    else:
        return HttpResponse(json.dumps(ret))

def model_edit_student(request):
    ret = {"status": True, "message": None}
    manage = Manage_Info()
    # 判断名字是否为空
    _id = request.POST.get('nid')
    if len(request.POST.get("name")) > 0:
        new_info = dict(
            student_id=request.POST.get("student_id"),
            name=request.POST.get("name"),
            class_id=request.POST.get("class_id")
        )
        try:
            manage.update_student_info(_id, new_info)
        except Exception:
            print(new_info)
            ret["status"] = False
            ret["message"] = "出现异常，编辑失败"
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse(json.dumps(ret))
    else:
        ret["status"] = False
        ret["message"] = "学生姓名不能为空"
        return HttpResponse(json.dump(ret))

def model_add_teacher(request):
    """添加教师信息"""
    ret = {"status": True, "message": None}
    manage = Manage_Info()
    # 判断数据是否为空
    if len(request.POST.get('job_id')) > 0 and len(request.POST.get('name')) > 0:
        # 判断该教师职工号是否存在于数据库中
        if manage.teacher_exists_by_id(request.POST.get('job_id')):
            ret["status"] = False
            ret["message"] = "职工号重复，请重新输入"
            return HttpResponse(json.dumps(ret))
        # 获取前端发送过来的新教师的信息
        teacher_info = dict(
            job_id=request.POST.get('job_id'),
            name=request.POST.get('name'),
            class_list=request.POST.getlist("class_list")
        )
        try:
            manage.add_teacher_info(teacher_info)
        except Exception as ret:
            ret["status"] = False
            ret["message"] = "出现异常，添加失败!"
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse(json.dumps(ret))
    else:
        if len(request.POST.get('name')) == 0:
            ret["status"] = False
            ret["message"] = "教师姓名不能为空"
            return HttpResponse(json.dumps(ret))
        else:
            ret["status"] = False
            ret["message"] = "教师工号不能为空"
            return HttpResponse(json.dumps(ret))

def model_del_teacher(request):
    """删除教师信息"""
    # 获取所要删除的教师序号
    _id = request.GET.get('nid')
    manage = Manage_Info()
    try:
        manage.del_teacher_info(_id)
    except Exception:
        return HttpResponse("删除失败")
    else:
        return HttpResponse("OK")

def model_edit_teacher(request):
    """编辑教师信息"""
    ret = {"status":True, "message":None}
    manage = Manage_Info()
    # 获取所编辑教师的序号
    _id = request.POST.get('nid')
    print("id=",_id)
    # 获取编辑后的信息
    new_info = dict(
        name=request.POST.get('name'),
        job_id=request.POST.get('job_id'),
        tech_classes=request.POST.getlist('tech_classes')
    )
    try:
        # 更新教师信息和关系表信息
        manage.update_teacher_info(_id, new_info)
    except Exception as error:
        ret["status"] = False
        ret["message"] = str(error)
        return HttpResponse(json.dumps(ret))
    else:
        return HttpResponse(json.dumps(ret))

def model_add_class(request):
    manage = Manage_Info()
    ret = {"status": True, "message": None}
    if len(request.POST.get('class_name')) > 0:
        class_info = dict(
            name=request.POST.get('class_name'),
        )
        try:
            manage.add_class_info(class_info)
        except Exception:
            ret["message"] = "出现异常，添加失败"
            ret["status"] = False
        finally:
            return HttpResponse(json.dumps(ret))
    else:
        # 提示用户不能为空，并保留模态对话框
        ret["message"] = "输入不能为空!"
        ret["status"] = False
        return HttpResponse(json.dumps(ret))

def model_del_class(request):
    manage = Manage_Info()
    _id = request.GET.get("nid")
    try:
        manage.del_class_info(_id)
    except Exception as ret:
        return HttpResponse("删除失败！")
    else:
        return HttpResponse("OK")

def model_edit_class(request):
    """编辑班级信息"""
    ret = {"status":True, "message": None}
    manage = Manage_Info()
    _id = request.POST.get('nid')
    new_info = dict(
        name=request.POST.get('class_name'),
    )
    try:
        manage.update_class_info(_id, new_info)
    except Exception:
        ret["status"] = False
        ret["message"] = "出现异常，编辑失败！"
        return HttpResponse(json.dumps(ret))
    else:
        return HttpResponse(json.dumps(ret))

def navi(request):
    """主页-导航"""
    return render(request, "navi.html")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('navi/', navi),
    path('add-teacher/', add_teacher),
    path('model-add-teacher/', model_add_teacher),
    path('model-del-teacher/', model_del_teacher),
    path('model-edit-teacher/', model_edit_teacher),
    path('del-teacher/', del_teacher),
    path('edit-teacher/', edit_teacher),
    path('teacher/', teacher_info),
    path('add-class/', add_class),
    path('model-add-class/', model_add_class),
    path('model-del-class/', model_del_class),
    path('model-edit-class/', model_edit_class),
    path('edit-class/', edit_class),
    path('del-class/', del_class),
    path('class/', class_info),
    path('get-classesinfo/', get_classesinfo),
    path('add-student/', add_student),
    path('model-add-student/', model_add_student),
    path('model-del-student/', model_del_student),
    path('model-edit-student/', model_edit_student),
    path('del-student/', del_student),
    path('edit-student/', edit_student),
    path('student/', student_info)
]
