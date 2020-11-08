from django.contrib import admin
from .models import PaymentInquiry, InquiryDetails, InquiryHistory, Payment, ContractorPrice


class PaymentInquiryAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


admin.site.register(PaymentInquiry, PaymentInquiryAdmin)
admin.site.register(InquiryDetails)
admin.site.register(InquiryHistory)
admin.site.register(Payment)
admin.site.register(ContractorPrice)
