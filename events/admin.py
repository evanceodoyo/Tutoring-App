from django.contrib import admin

from .models import Event, EventObjective, EventTag, EventTicket, Objective, Sponsor


class EventAdmin(admin.ModelAdmin):
    list_display = ["title", "organiser", "start_date", "end_date", "created"]
    search_fields = ["title"]
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Event, EventAdmin)
admin.site.register(EventObjective)
admin.site.register(Objective)
admin.site.register(EventTag)
admin.site.register(Sponsor)
admin.site.register(EventTicket)
