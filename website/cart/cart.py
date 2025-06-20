from decimal import Decimal
from django.conf import settings
from blog_app.models import Item

class Cart(object):
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            self.session[settings.CART_SESSION_ID] = {}
            cart = self.session[settings.CART_SESSION_ID]
        self.cart = cart 
    
    def __iter__(self):
        # перебираем товары в корзине из базы данных 
        item_ids = self.cart.keys()
        items = Item.objects.filter(id__in=item_ids)

        cart = self.cart.copy()
        for item in items:
            cart[str(item.id)]['items'] = item

        for itam in cart.values():
            itam['price'] = Decimal(itam['price'])
            itam['total_price'] = itam['price'] * itam['quantity']
            yield itam

    
    def __len__(self):
        # считает ск товаров в корзине
        return sum(itam['quantity'] for itam in self.cart.values())
    

    def add(self, item, quantity=1, update_quantity=False):
        # добавление товара в корзину или обновление кол-ва
        item_id = str(item.id)
        if item_id not in self.cart:
            self.cart[item_id] = {'quantity': 0,
                                  'price': str(item.price)}
        if  update_quantity:
            self.cart[item_id]['quantity'] = quantity
        else:
            self.cart[item_id]['quantity'] += quantity
        self.save()      


    def save(self):
        # сохраняем товар
        self.session.modified = True
    
    
    def remove(self, item):
        # удаляем товар
        item_id = str(item.id)
        if item_id in self.cart:
            del self.cart[item_id]
            self.save()
    

    def get_total_price(self):
        # получаем общ стоимость
        return sum(Decimal(itam['price']) * itam['quantity'] for itam in self.cart.values())
    

    def clear(self):
        # очистка корзины
        del self.session[settings.CART_SESSION_ID]
        self.save()