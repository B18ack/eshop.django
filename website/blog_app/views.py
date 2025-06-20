from django.shortcuts import render, redirect, get_object_or_404
from . import models
from .forms import LoginForm, RegistrationForm, CommentForm, ItemForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.generic import UpdateView, DeleteView
from slugify import slugify
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from cart.forms import CartAddItemForm


def render_home_page(request):
    categories = models.Category.objects.all()
    questions = models.FAQ.objects.all()  # select * from blog_app_faq
    items = models.Item.objects.all().order_by('id')
    
    paginator = Paginator(items, 8)  
    page = request.GET.get('page')
    items = paginator.get_page(page)
    cart_item_form = CartAddItemForm()
    
    context = {
        'categories': categories,
        'questions': questions,
        'items': items,
        'cart_item_form': cart_item_form,
    }
    return render(request, 'blog_app/index.html', context)
    


def render_items_page(request):
    query_params = request.GET.get('category')
    page = request.GET.get('page')
    print(query_params)
    
    items = models.Item.objects.all()
    
    if query_params:
        # category = models.Category.objects.get(slug=query_params)
        # select * from categories where slug = '';
        items = items.filter(category__slug=query_params)

    paginator = Paginator(items, 3)  
    
    items = paginator.get_page(page)
    
    categories = models.Category.objects.all()
    context = {
        'items': items,
        'categories': categories,
        'slug': query_params
    }
    return render(request, 'blog_app/item.html', context)
        

def render_faq_page(request):
    questions = models.FAQ.objects.all()
    context = {
        'questions': questions
    }
    return render(request, 'blog_app/faq.html', context)
    

def render_registration_page(request):
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST)
        if form.is_valid():
            form.save()  # сохранение данных в форму
            messages.success(request, 'Регистрация прошла успешно')
            return redirect('login')
        else:
            for i in form:
                for e in i.errors:
                    print(e)
                # print(dir(i.errors), i.errors.data)
    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'blog_app/registration.html', context)
    

# GET, POST, PUT, DELETE
def render_login_page(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()  # AuthenticationForm. User | None
            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно вошли в аккаунт')
                return redirect('home')
            else:
                messages.error(request, 'Пользователь не найден')
        else:

            messages.error(request, 'Неправильный логин или пароль')  # отображаем сообщение ошибки
    else:
        form = LoginForm()
    
    context = {
        'form': form
    }
    return render(request, 'blog_app/login.html', context)
    

def render_item_detail_page(request, slug):
    item = models.Item.objects.get(slug=slug)
    comments = models.Comment.objects.filter(item=item)
    cart_item_form = CartAddItemForm()

    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.item = item
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий успешно добавлен')
            return redirect('item_detail', slug=item.slug)
    else:
        form = CommentForm()

    try:
        item.likes
    except Exception:
        models.Like.objects.create(item=item)

    try:
        item.dislikes
    except Exception:
        models.Dislike.objects.create(item=item)

    total_likes = item.likes.user.all().count()
    total_dislikes = item.dislikes.user.all().count()

    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = models.Favorite.objects.filter(user=request.user, item=item).exists()

    context = {
        'item': item,
        'comments': comments,
        'form': form,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'total_comments': comments.count(),
        'cart_item_form': cart_item_form,
        'is_favorite': is_favorite 
    }
    return render(request, 'blog_app/item_detail.html', context)
    

def user_logout(request):
    logout(request)
    return redirect('home')


def create_item_page(request):
    if request.method == 'POST':
        form = ItemForm(data=request.POST, files=request.FILES)
        
        if form.is_valid():
            item = form.save(commit=False)
            item.slug = slugify(item.title)
            item.author = request.user
            item.save()
            
            for photo in request.FILES.getlist('gallery'):
                models.ItemImage.objects.create(
                    item=item,
                    photo=photo
                )
            
            messages.success(request, 'Товар успешно добавлен')
            return redirect('item_detail', item.slug)
        else:
            messages.error(request, 'Что-то пошло не так')
    else:
        form = ItemForm()
    
    context = {
        'form': form
    }
    return render(request, 'blog_app/item_form.html', context)



class UpdateItem(UpdateView):
    model = models.Item
    form_class = ItemForm
    template_name='blog_app/item_form.html'

    def form_valid(self, form):
        item = form.save(commit=False)
        item.slug = slugify(item.title)
        # Если нужно, можно обновить автора или другие поля
        item.save()

        # Обновляем preview, если он был загружен
        if 'preview' in self.request.FILES:
            item.preview = self.request.FILES['preview']
            item.save()

        # Добавляем новые фото в галерею, если они есть
        for photo in self.request.FILES.getlist('gallery'):
            models.ItemImage.objects.create(
                item=item,
                photo=photo
            )
        
        messages.success(self.request, 'Товар успешно обновлён')
        return redirect('item_detail', item.slug)
    

class DeleteItem(DeleteView):
    model = models.Item
    success_url = '/items/'
    template_name = 'blog_app/item_confirm_delete.html'
    


def add_vote(request, item_id, action):
    item = models.Item.objects.get(pk=item_id)

    user = request.user
    if action == 'add_like':
        if user in item.likes.user.all():
            # если лайк уже добавлен от пользователя
            # то удаляем его лайк
            item.likes.user.remove(user.pk)  
        else:
            # если лайк не добавлен
            # добавляем лайк, удаляем дизлайк
            item.likes.user.add(user.pk)
            item.dislikes.user.remove(user.pk)
    elif action == 'add_dislike':
        if user in item.dislikes.user.all():
            # если лайк уже добавлен от пользователя
            # то удаляем его лайк
            item.dislikes.user.remove(user.pk)  
        else:
            # если лайк не добавлен
            # добавляем лайк, удаляем дизлайк
            item.dislikes.user.add(user.pk)
            item.likes.user.remove(user.pk)
    
    return redirect('item_detail', slug=item.slug)
    

def search(request):
    query = request.GET.get('q')
    # регулярные выражения
    items = models.Item.objects.filter(title__iregex=query)
    context = {
        'items': items,
        'total_items': items.count(),
        'query': query
    }
    return render(request, 'blog_app/search.html', context)

# на детальной странице статьи сделать подсчет комментариев и отобразить на странице


@login_required(login_url='login')
def profile_page(request):
    items = models.Item.objects.filter(author=request.user)
    total_comments = sum([item.comment_set.all().count() for item in items])
    total_likes = sum([item.likes.user.all().count() for item in items])
    total_dislikes = sum([item.dislikes.user.all().count() for item in items])
    context = {
        'total_items': items.count(),
        'total_comments': total_comments,
        'total_likes': total_likes,
        'total_dislikes': total_dislikes,
        'items': items
    }
    return render(request, 'blog_app/profile.html', context)


@login_required
def add_to_favorites(request, item_id):
    item = get_object_or_404(models.Item, id=item_id)
    models.Favorite.objects.get_or_create(user=request.user, item=item)
    return redirect('item_detail', slug=item.slug)

@login_required
def remove_from_favorites(request, item_id):
    item = get_object_or_404(models.Item, id=item_id)
    models.Favorite.objects.filter(user=request.user, item=item).delete()
    return redirect('favorite_list')

@login_required
def favorite_list(request):
    favorites = models.Favorite.objects.filter(user=request.user).select_related('item')
    return render(request, 'blog_app/favorites.html', {'favorites': favorites})