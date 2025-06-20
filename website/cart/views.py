from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from blog_app.models import Item
from .cart import Cart
from .forms import CartAddItemForm


@require_POST
def cart_add(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    form = CartAddItemForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(item = item,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    return redirect('cart:cart_detail')


def cart_remove(request, item_id):
    cart = Cart(request)
    item = get_object_or_404(Item, id=item_id)
    cart.remove(item)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for itam in cart:
        print(itam)
        itam['update_quantity_form'] = CartAddItemForm(initial={'quantity': itam['quantity'],
                                                                'update': True})
       
    return render(request, 'cart/cart_detail.html', {'cart':cart}) 


def cart_order(request):
    return render(request, 'cart/order.html')