from django.contrib import admin
from .models import Person, PersonName, Place, PlaceName

# Register your models here.
class PlaceNameInline(admin.TabularInline):
    model = PlaceName

class PersonNameInline(admin.TabularInline):
    model = PersonName

class PlaceAdmin(admin.ModelAdmin):
    inlines = [PlaceNameInline]

class PersonAdmin(admin.ModelAdmin):
    inlines = [PersonNameInline]

admin.site.register(Person, PersonAdmin)
admin.site.register(Place, PlaceAdmin)
