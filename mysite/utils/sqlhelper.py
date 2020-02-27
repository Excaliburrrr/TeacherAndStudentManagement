# _*_ coding: utf-8 _*_
# Author: Sebuntin
# Time: 18:58
# Name: utils.py

from sqlalchemy import Column, VARCHAR, Integer, create_engine, DATE, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time

Base = declarative_base()

class Student(Base):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, default=None)
    name = Column(VARCHAR(20), nullable=True)
    student_id = Column(VARCHAR(8), nullable=True)
    class_id = Column(VARCHAR(10), nullable=True, default=None)

class Class(Base):
    __tablename__ = 'class'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, default=None)
    name = Column(VARCHAR(20), nullable=True)

class Teacher(Base):
    __tablename__ = 'teacher'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, default=None)
    name = Column(VARCHAR(20), nullable=True)
    job_id = Column(VARCHAR(8), nullable=True)

class Relation(Base):
    """教师与班级关系表"""
    __tablename__ = 'relation'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False, default=None)
    teacher_id = Column(Integer, nullable=False, default=None)
    class_id= Column(Integer, nullable=False, default=None)


class Manage_Info:
    def __init__(self):
        engine = create_engine('mysql+pymysql://root:654232@localhost:3306/school', max_overflow=5)
        Base.metadata.create_all(engine)
        DBsession = sessionmaker(bind=engine)

        self.session = DBsession()

    def add_student_info(self, info_dict):
        class_info = self.session.query(Class).filter(Class.name==info_dict.get("class_name")).all()
        class_id = class_info[0].id
        new_student = Student(name=info_dict.get("name"), student_id=info_dict.get("student_id"), class_id=class_id)
        self.session.add(new_student)
        self.session.commit()

    def get_student_info(self, id=None):
        """当传入指定id时，返回对应id的学生信息，
            当不传值时，则返回所有学生的信息
        """
        if not id:
            student_infos = self.session.query(Student).all()
            info_list = []
            for student_info in student_infos:
                if student_info.class_id == "":
                    class_name = ""
                else:
                    class_info = self.session.query(Class).\
                        filter(student_info.class_id == Class.id).one()
                    class_name = class_info.name
                info_dict = dict(id=student_info.id,
                                 name=student_info.name,
                                 student_id=student_info.student_id,
                                 class_id = student_info.class_id,
                                 class_name=class_name)
                info_list.append(info_dict)

            return info_list
        else:
            student_info = self.session.query(Student).\
                filter(Student.id==id).one()
            # 得到班级名字
            if not student_info.class_id == "":
                class_info = self.session.query(Class).\
                    filter(Class.id==student_info.class_id).one()
                class_name = class_info.name
            else:
                class_name = ""
            return dict(
                id=student_info.id,
                name=student_info.name,
                student_id=student_info.student_id,
                class_name=class_name
            )

    def del_student_info(self, id):
        self.session.query(Student).filter(Student.id==id).delete()
        self.session.commit()

    def update_student_info(self, id, new_info):
        if new_info['class_id']:
            class_id = new_info['class_id']
        else:
            class_id = ""
        self.session.query(Student)\
            .filter(Student.id==id).update({
                        "student_id":new_info['student_id'],
                        "name":new_info['name'],
                        "class_id":class_id
            })
        self.session.commit()

    def get_teacher_info(self, id=None):
        if not id:
            teachers_info = self.session.query(Relation.id, Teacher.id, Teacher.name, Teacher.job_id, Class.name).\
                        outerjoin(Teacher, Teacher.id == Relation.teacher_id).\
                        join(Class, Class.id == Relation.class_id).all()
            result = dict()
            for teacher_info in teachers_info:
                tid = teacher_info[1]
                if tid in result.keys():
                    result[tid]['class_name'].append(teacher_info[4])
                else:
                    result[tid] = dict(
                        id=teacher_info[1],
                        name=teacher_info[2],
                        job_id=teacher_info[3],
                        class_name=[teacher_info[4]]
                    )
            return result.values()
        else:
            teacher = self.session.query(Teacher).\
                filter(Teacher.id==id).one()
            return dict(
                id=teacher.id,
                job_id=teacher.job_id,
                name=teacher.name
            )

    def add_teacher_info(self, teacher_info):
        new_teacher = Teacher(job_id=teacher_info['job_id'],
                              name=teacher_info['name'])
        self.session.add(new_teacher)
        last_rowid = self.session.query(func.max(Teacher.id)).one()[0]
        # 同时为关系表添加数据
        start_time = time.time()
        relation_list = []
        for class_id in teacher_info["class_list"]:
            new_relation = Relation(
                class_id=int(class_id),
                teacher_id=last_rowid,
            )
            relation_list.append(new_relation)
        self.session.add_all(relation_list)
        cost_time = time.time() - start_time
        self.session.commit()

    def update_teacher_info(self, id, teacher_info):
        # 更新教师信息
        self.session.query(Teacher).\
            filter(Teacher.id==id).update({
                'job_id':teacher_info['job_id'],
                'name':teacher_info['name'],
            })
        # 更新关系表信息
        self.session.query(Relation).filter(Relation.teacher_id==id).delete()
        for class_id in teacher_info['tech_classes']:
            new_relation = Relation(teacher_id=id, class_id=class_id)
            self.session.add(new_relation)
        self.session.commit()

    def del_teacher_info(self, id):
        # 当进行删除教师操作时，由于教师与班级是多对多的关系，
        # 所以需要同步删除关系表中关于该教师的所有关系
        self.session.query(Relation).filter(Relation.teacher_id==id).delete()
        self.session.query(Teacher).\
            filter(Teacher.id==id).delete()
        self.session.commit()

    def add_class_info(self, class_info):
        """添加班级"""
        # 从数据库中找教师编号
        new_class = Class(
            name=class_info["name"],
        )
        self.session.add(new_class)
        self.session.commit()

    def del_class_info(self, id):
        # 先更新学生班级信息
        self.session.query(Student).filter(Student.class_id==id).update({
            "class_id":""
        })
        self.session.query(Class).filter(Class.id==id).delete()
        # 更新关系表
        self.session.query(Relation).filter(id==Relation.class_id).delete()
        self.session.commit()

    def update_class_info(self, id, class_info):
        """当更新班级信息的时候，同时更新学生信息"""
        self.session.query(Class).filter(Class.id==id).update({
            "name":class_info['name'],
        })
        self.session.commit()


    def get_class_info(self, id=None):
        if not id:
            classes = self.session.query(Class).all()
            class_info_list = []
            for class_ in classes:
                class_info = dict(
                    id=class_.id,
                    name=class_.name,
                )
                class_info_list.append(class_info)
            return class_info_list
        else:
            class_ = self.session.query(Class).\
                filter(Class.id==id).one()
            return dict(
                id=id,
                name=class_.name,
            )


    def student_exists(self, student_id):
        """判断学生是否存在于数据库"""
        query = self.session.query(Student).\
            filter(Student.student_id==student_id).all()
        if query:
            return True
        else:
            return False

    def teacher_exists_by_id(self, job_id):
        """判断教师是否存在于数据库"""
        query = self.session.query(Teacher).\
            filter(Teacher.job_id==job_id).all()
        if query:
            return True
        else:
            return False

    def teacher_exists_by_name(self, name):
        query = self.session.query(Teacher). \
            filter(Teacher.name==name).all()
        if query:
            return True
        else:
            return False

    def class_exists(self, class_name):
        """判断班级是否存在"""
        query = self.session.query(Class).\
            filter(Class.name==class_name).all()
        if query:
            return True
        else:
            return False


if __name__ == "__main__":
    manage = Manage_Info()
    manage.get_teacher_info()
