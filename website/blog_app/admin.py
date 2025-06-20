from django.contrib import admin
from . import models


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'slug', 'created_at']  # какие поля из таблицы отображать
    prepopulated_fields = {'slug': ('name',)}
    list_display_links = ['pk', 'name']  # какие поля из тех полей что были указаны в list_display сделать кликабельными
    list_filter = ['created_at']
    search_fields = ['name']

# if product.preview
# product.preview.url

class ItemImageInline(admin.TabularInline):
    model = models.ItemImage
    extra = 1

@admin.register(models.Item)
class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ItemImageInline]

admin.site.register(models.FAQ)
admin.site.register(models.Comment)

