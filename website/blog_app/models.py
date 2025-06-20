from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
from decimal import Decimal
# python manage.py makemigrations - данная команда, проверяет правильность нашей таблицы, и создает файл с историей того, что мы сделали с нашей базой данных
# python manage.py migrate - выполняет файл с историей изменений нашей базы данных, и создает таблицы внутри файла базы данных


# создание суперпользователя(администратора) для проекта
# python manage.py createsuperuser



class FAQ(models.Model):
    question = models.TextField(verbose_name='Вопрос')
    answer = models.TextField(verbose_name='Ответ')
    
    def __str__(self) -> str:
        return self.question
    
    class Meta:
        verbose_name = 'Вопрос ответ'
        verbose_name_plural = 'Вопросы ответы'



class Category(models.Model):
    name = models.CharField(max_length=40, unique=True, verbose_name='Название')
    slug = models.SlugField(verbose_name='Слаг', 
        help_text='Данное поле заполняется автоматически'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'



class Item(models.Model):
    title = models.CharField(max_length=150, verbose_name='Название')
    slug = models.SlugField(verbose_name='Слаг', null=True, blank=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    preview = models.ImageField(upload_to='items/previews/', null=True, blank=True, verbose_name='Превью')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items', verbose_name='Категория')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='items', verbose_name='Автор')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    credit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Кредит')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.credit:
            self.credit = self.price / Decimal('24')
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('item_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'        


class ItemImage(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    photo = models.ImageField(upload_to='items/gallery/', verbose_name='Фото')
    
    class Meta:
        verbose_name = 'Галлерея товара'
        verbose_name_plural = 'Галлерея товаров'
        

class Comment(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Товар')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Текст')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.author} - {self.item}'
        
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
    

class Like(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE,
    related_name='likes', verbose_name='Товар')
    user = models.ManyToManyField(User, related_name='likes')
    

class Dislike(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE,
    related_name='dislikes', verbose_name='Товар')
    user = models.ManyToManyField(User, related_name='dislikes')


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')

    def __str__(self):
        return f"{self.user.username} ❤ {self.item.title}"
