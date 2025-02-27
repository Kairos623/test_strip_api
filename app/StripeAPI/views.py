import stripe
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .models import Item, Order, Discount, OrderItem

STRIPE_PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
STRIPE_API_KEY_EUR = settings.STRIPE_API_KEY_EUR
STRIPE_API_KEY_USD = settings.STRIPE_API_KEY_USD


def success(request):
    """
    Отмечает заказ как оплаченный (если он существует) и отображает шаблон успешной оплаты.
    """
    order_id = request.session.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, paid=False)
            order.paid = True
            order.save()
        except Order.DoesNotExist:
            pass
        request.session.pop('order_id', None)
    return render(request, 'StripeAPI/success.html')


def cancel(request):
    """
    Отображает шаблон отмены оплаты.
    """
    return render(request, 'StripeAPI/cancel.html')


def item_list(request):
    """
    Отображает список всех товаров.
    """
    items = Item.objects.all()
    context = {'items': items}
    return render(request, 'StripeAPI/main.html', context)


def item_detail(request, id):
    """
    Отображает подробную информацию о товаре.
    """
    item = get_object_or_404(Item, pk=id)
    context = {
        'item': item,
        'stripe_public_key': STRIPE_PUBLIC_KEY,
    }
    return render(request, 'StripeAPI/item_detail.html', context)


def get_stripe_api_key(currency):
    """
    Возвращает API-ключ Stripe для заданной валюты.
    """
    currency_keys = {
        code.upper(): getattr(settings, f"STRIPE_API_KEY_{code.upper()}", None)
        for code, _ in Item.CURRENCY_CHOICES
    }
    return currency_keys.get(currency.strip().upper())


def parse_quantity(request, method='GET'):
    """
    Извлекает количество товара из запроса. Если значение некорректно или меньше 1, возвращается значение по умолчанию (1).
    """
    default_quantity = 1
    try:
        if method.upper() == 'GET':
            quantity = int(request.GET.get('quantity', default_quantity))
        else:
            quantity = int(request.POST.get('quantity', default_quantity))
        if quantity < 1:
            quantity = default_quantity
    except (ValueError, TypeError):
        quantity = default_quantity
    return quantity


def get_or_create_order(request):
    """
    Извлекает текущий незаконченный заказ из сессии или создаёт новый.
    """
    order_id = request.session.get('order_id')
    order = Order.objects.filter(id=order_id, paid=False).first() if order_id else None
    if not order:
        order = Order.objects.create()
        request.session['order_id'] = order.id
    return order


def buy_item(request, id):
    """
    Создаёт сессию оплаты Stripe для покупки одного товара.
    """
    item = get_object_or_404(Item, pk=id)
    quantity = parse_quantity(request, method='GET')

    stripe.api_key = get_stripe_api_key(item.currency)
    if not stripe.api_key:
        return JsonResponse({'error': 'API-ключ для валюты не найден'}, status=400)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': item.currency,
                'product_data': {
                    'name': item.name,
                    'description': item.description,
                },
                'unit_amount': int(item.price * 100),
            },
            'quantity': quantity,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('success')),
        cancel_url=request.build_absolute_uri(reverse('cancel')),
    )
    return JsonResponse({'sessionId': session.id})


def add_to_order(request, id):
    """
    Добавляет товар в заказ с проверкой на единообразие валюты.
    """
    item = get_object_or_404(Item, pk=id)
    quantity = parse_quantity(request, method='POST')
    order = get_or_create_order(request)

    order_items = order.order_items.all()
    if order_items.exists():
        existing_currency = order_items.first().item.currency.upper()
        if existing_currency != item.currency.upper():
            message = "Нельзя добавлять товары с разной валютой в один заказ."
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': message})
            else:
                return redirect('item_detail', id=item.id)

    order_item, created = OrderItem.objects.get_or_create(
        order=order, item=item, defaults={'quantity': quantity}
    )
    if not created:
        order_item.quantity += quantity
        order_item.save()

    message = f'Товар "{item.name}" добавлен в заказ (количество: {quantity}).'
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': message})
    else:
        return redirect('item_detail', id=item.id)


def order_detail(request):
    """
    Отображает детали текущего заказа.
    """
    order = None
    order_id = request.session.get('order_id')
    if order_id:
        order = get_object_or_404(Order, pk=order_id, paid=False)
    context = {
        'order': order,
        'stripe_public_key': STRIPE_PUBLIC_KEY,
    }
    return render(request, 'StripeAPI/order_detail.html', context)


def update_order_item(request, order_item_id):
    """
    Обновляет количество для позиции в заказе.
    """
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__paid=False)
    if request.method == 'POST':
        new_quantity = parse_quantity(request, method='POST')
        order_item.quantity = new_quantity
        order_item.save()
    return redirect('order_detail')


def delete_order_item(request, order_item_id):
    """
    Удаляет позицию из заказа. Если после удаления в заказе не остается товаров, удаляет и сам заказ.
    """
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__paid=False)
    order = order_item.order
    if request.method == 'POST':
        order_item.delete()
        if not order.order_items.exists():
            order.delete()
            request.session.pop('order_id', None)
            return redirect('item_list')
    return redirect('order_detail')


def delete_order(request, order_id):
    """
    Удаляет весь заказ.
    """
    order = get_object_or_404(Order, id=order_id, paid=False)
    if request.method == 'POST':
        order.delete()
        request.session.pop('order_id', None)
    return redirect('item_list')


def buy_order(request, id):
    """
    Создаёт сессию оплаты Stripe для покупки всего заказа.
    """
    order = get_object_or_404(Order, id=id)

    currencies = {oi.item.currency for oi in order.order_items.all()}
    if len(currencies) > 1:
        return JsonResponse({'error': 'Все товары в заказе должны быть в одной валюте.'}, status=400)

    currency = currencies.pop() if currencies else 'usd'
    stripe.api_key = get_stripe_api_key(currency)
    if not stripe.api_key:
        return JsonResponse({'error': 'API-ключ для валюты не найден'}, status=400)

    line_items = []
    for order_item in order.order_items.all():
        item_data = {
            'price_data': {
                'currency': currency,
                'unit_amount': int(order_item.item.price * 100),
                'product_data': {
                    'name': order_item.item.name,
                    'description': order_item.item.description,
                },
            },
            'quantity': order_item.quantity,
        }
        if order.tax:
            item_data['tax_rates'] = [order.tax.stripe_tax_rate_id]
        line_items.append(item_data)

    payment_method_types = ['card']
    mode = 'payment'
    success_url = request.build_absolute_uri(reverse('success'))
    cancel_url = request.build_absolute_uri(reverse('cancel'))

    if order.discount:
        discounts = [{'coupon': order.discount.stripe_coupon_id}]
        session = stripe.checkout.Session.create(
            payment_method_types=payment_method_types,
            line_items=line_items,
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
            discounts=discounts,
        )
    else:
        session = stripe.checkout.Session.create(
            payment_method_types=payment_method_types,
            line_items=line_items,
            mode=mode,
            success_url=success_url,
            cancel_url=cancel_url,
        )

    return JsonResponse({'sessionId': session.id})


def apply_coupon(request, order_id):
    """
    Применяет промокод к заказу.
    """
    order = get_object_or_404(Order, pk=order_id)
    coupon_code = request.POST.get('coupon_code', '').strip()
    if coupon_code:
        try:
            discount = Discount.objects.get(name__iexact=coupon_code)
            order.discount = discount
            order.save()
            return redirect('order_detail')
        except Discount.DoesNotExist:
            url = f"{reverse('order_detail')}?coupon_error=1"
            return redirect(url)
    return redirect('order_detail')


def buy_item_intent(request, id):
    """
    Создаёт PaymentIntent Stripe для покупки одного товара.
    """
    item = get_object_or_404(Item, pk=id)
    stripe.api_key = get_stripe_api_key(item.currency)

    intent = stripe.PaymentIntent.create(
        amount=int(item.price * 100),
        currency=item.currency,
        payment_method_types=["card"],
    )
    context = {
        'client_secret': intent.client_secret,
        'stripe_public_key': STRIPE_PUBLIC_KEY,
        'item': item,
    }
    return render(request, 'StripeAPI/payment_intent.html', context)


def buy_order_intent(request, id):
    """
    Создаёт PaymentIntent Stripe для покупки всего заказа.
    """
    order = get_object_or_404(Order, id=id)
    currencies = {oi.item.currency for oi in order.order_items.all()}
    if len(currencies) > 1:
        return JsonResponse({'error': 'Все товары в заказе должны быть в одной валюте.'}, status=400)
    currency = currencies.pop()
    stripe.api_key = get_stripe_api_key(currency)

    total_amount = int(order.total_amount * 100)
    metadata = {}
    if order.discount:
        metadata['discount_coupon'] = order.discount.stripe_coupon_id
        metadata['discount_percentage'] = str(order.discount.percentage)
    if order.tax:
        metadata['tax_rate'] = order.tax.stripe_tax_rate_id
        metadata['tax_percentage'] = str(order.tax.percentage)

    intent = stripe.PaymentIntent.create(
        amount=total_amount,
        currency=currency,
        payment_method_types=["card"],
        metadata=metadata,
    )
    context = {
        'client_secret': intent.client_secret,
        'stripe_public_key': STRIPE_PUBLIC_KEY,
        'order': order,
    }
    return render(request, 'StripeAPI/payment_intent.html', context)
