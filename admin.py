from django.contrib import admin
from .models import GameLog, CardData, PredData, ExceptionData

admin.site.register(GameLog)
admin.site.register(CardData)
admin.site.register(PredData)
admin.site.register(ExceptionData)

class ExceptionInline(admin.TabularInline):
    model = ExceptionData

class CardDataAdmin(admin.ModelAdmin):
    inlines = [
        ExceptionInline,
    ]