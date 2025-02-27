from django.urls import path

from .views import item_list, item_detail, buy_item, success, cancel, add_to_order, order_detail, buy_order, \
    apply_coupon, update_order_item, delete_order_item, delete_order, buy_item_intent, buy_order_intent

urlpatterns = [
    path('', item_list, name='item_list'),
    path('item/<int:id>/', item_detail, name='item_detail'),
    path('buy/<int:id>/', buy_item, name='buy_item'),
    path('success/', success, name='success'),
    path('cancel/', cancel, name='cancel'),
    path('item/<int:id>/add/', add_to_order, name='add_to_order'),
    path('order/', order_detail, name='order_detail'),
    path('order/buy/<int:id>/', buy_order, name='buy_order'),
    path('order/<int:order_id>/apply_coupon/', apply_coupon, name='apply_coupon'),
    path('order/update/<int:order_item_id>/', update_order_item, name='update_order_item'),
    path('order/delete_item/<int:order_item_id>/', delete_order_item, name='delete_order_item'),
    path('order/delete/<int:order_id>/', delete_order, name='delete_order'),
    path('buy-item-intent/<int:id>/', buy_item_intent, name='buy_item_intent'),
    path('buy-order-intent/<int:id>/', buy_order_intent, name='buy_order_intent'),
]
