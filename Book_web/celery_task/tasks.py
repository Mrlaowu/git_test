#使用celery
from django.conf import settings
from django.core.mail import send_mail
from celery import Celery
import time
from django.template import loader,RequestContext

#在任务处理者一端加上这几句:django项目初始化
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","Book_web.settings")
django.setup()

from apps.books.models import Books

#创建一个Celery类的实例对象  broker:中间人
app=Celery("celery_task.tasks",broker='redis://192.168.229.130:6379/8')

#定义任务函数
@app.task
def send_register_active_email(to_email,username,token):
    """发送激活邮件"""
    #组织邮件信息
    subject = "三维书店欢迎信息"
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s,欢迎您成为三维书店注册会员</h1>请点击下面链接激活您的账户<br><a href="http://127.0.0.1/user/active/%s">http://127.0.0.1/user/active/%s</a>' % (
    username, token, token)
    #发送邮件
    send_mail(subject, message, sender, receiver, html_message=html_message)
    time.sleep(4)

@app.task
def generate_static_index_html():
    """generate staitc page"""
    books=Books.objects.all()

    context={
        'books':books
    }
    #使用模板
    #1.加载模板文件，返回模板对象
    temp=loader.get_template("static_index.html")

    #2.渲染模板
    static_index_html=temp.render(context)

    #3.生成对应的静态文件
    save_path=os.path.join(settings.BASE_DIR,'static/index.html')
    with open(save_path,'w') as fp:
        fp.write(static_index_html)