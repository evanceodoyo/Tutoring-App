from django.contrib import admin

from .models import CustomerInquiry


class CustomerInquiryAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "subject", "message", "created"]
    search_fields = ["name", "email", "subject", "message"]


admin.site.register(CustomerInquiry, CustomerInquiryAdmin)
