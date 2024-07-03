from django.contrib import admin

from flights.models import (
    Ticket,
    Flight,
    Order,
    Crew,
    AirplaneType,
    Airport,
    Airplane
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(Flight)
admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Ticket)
