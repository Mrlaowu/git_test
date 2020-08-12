from django.db import models
from db.basemodel import BaseModel
from tinymce.models import HTMLField

class BooksType(BaseModel):
    name=models.CharField(max_length=20,verbose_name="种类名称")

    def __str__(self):
        return self.name

    class Meta:
        db_table="df_books_type"
        verbose_name="书籍种类"
        verbose_name_plural=verbose_name


class Books(BaseModel):
    type=models.ForeignKey("BooksType",verbose_name="书籍种类")
    title=models.CharField(max_length=20,verbose_name="书籍标题")
    price=models.DecimalField(max_digits=10,decimal_places=2,verbose_name="商品价格")
    image=models.ImageField(upload_to="books",verbose_name="书籍图片")
    count=models.IntegerField(default=1,verbose_name="书籍数量")
    detail=HTMLField(blank=True,verbose_name="书籍详情")
    author=models.CharField(max_length=20,verbose_name="作者")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name="图书"
        verbose_name_plural=verbose_name
