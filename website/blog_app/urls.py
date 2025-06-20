from django.urls import path, include

from . import views


urlpatterns = [
    path('cart/', include('cart.urls', namespace='cart')),
    path('', views.render_home_page, name='home'),
    path('faq/', views.render_faq_page, name='faq'),
    path('items/', views.render_items_page, name='items'),
    path('registration/', views.render_registration_page, name='registration'),
    path('login/', views.render_login_page, name='login'),
    path('items/create/', views.create_item_page, name='create_item'),
    path('item/<slug:slug>/', views.render_item_detail_page,name='item_detail'),
    path('item/<int:item_id>/<str:action>/', views.add_vote, name='add_vote'),
    path('item/<slug:slug>/update/', views.UpdateItem.as_view(), name='update'),
    path('item/<slug:slug>/delete/', views.DeleteItem.as_view(), name='delete'),
    path('logout/', views.user_logout, name='logout'),
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/add/<int:item_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:item_id>/', views.remove_from_favorites, name='remove_from_favorites'),

    path('search/', views.search, name='search'),
    path('profile/', views.profile_page, name='profile')
    
]