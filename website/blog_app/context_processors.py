from .models import Category, Favorite

def categories_processor(request):
    categories = Category.objects.all()
    return {'categories': categories}


def favorite_count(request):
    if request.user.is_authenticated:
        count = Favorite.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'favorite_count': count}