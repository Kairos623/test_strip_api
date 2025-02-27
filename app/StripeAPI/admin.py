from django.contrib import admin

from .models import Item, Order, Discount, Tax, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'paid', 'discount', 'tax', 'total_amount']
    list_filter = ['paid', 'discount', 'tax']
    inlines = [OrderItemInline]
    readonly_fields = ['total_amount']
    fieldsets = (
        (None, {'fields': ('discount', 'tax', 'paid')}),
    )
    search_fields = ['id']


admin.site.register(Order, OrderAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'price', 'currency']
    fieldsets = (
        (None, {'fields': ('name', 'description', 'price', 'currency')}),
    )
    search_fields = ['name', 'description']


admin.site.register(Item, ItemAdmin)


class DiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'percentage', 'stripe_coupon_id']
    search_fields = ['name', 'stripe_coupon_id']


admin.site.register(Discount, DiscountAdmin)


class TaxAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'percentage', 'stripe_tax_rate_id']
    search_fields = ['name', 'stripe_tax_rate_id']


admin.site.register(Tax, TaxAdmin)
