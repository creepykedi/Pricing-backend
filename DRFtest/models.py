from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from .validators import validate_okpd


# Запросы на расчет
class PaymentInquiry(models.Model):
    name = models.CharField(max_length=128)
    date_created = models.DateTimeField(auto_now=True)
    deadline_date = models.DateField(blank=True, null=True)
    current_status = models.ForeignKey('InquiryHistory', on_delete=models.CASCADE)
    payment_m = models.ForeignKey('Payment', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.payment_m:
            return f"{self.name} #{self.id}. Статус: {self.current_status.status}. Создан: {self.date_created.date()}. Расчет №{self.payment_m.id}"
        return f"{self.name} #{self.id}. Статус: {self.current_status.status}. Создан: {self.date_created.date()}"

    class Meta:
        verbose_name_plural = "Запросы на расчет"


# Состав запроса для расчета
class InquiryDetails(models.Model):
    inquiry = models.ForeignKey(PaymentInquiry, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    OKPD2 = models.CharField(max_length=15, validators=[validate_okpd])
    OKEI = models.IntegerField(null=True, validators=[MaxValueValidator(999)])
    amount = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} {self.amount} шт., окпд2: {self.OKPD2} "

    class Meta:
        verbose_name_plural = "Состав запроса для расчета"


class InquiryHistory(models.Model):
    status_choices = [
        ('Created', 'Создан'),
        ('Received', 'Принят в работу исполнителем'),
        ('Payment formed', 'Сформирован расчет'),
        ('Returned', 'Возвращен исполнителю'),
        ('Taken down', 'Исполнитель с расчета снят'),
        ('Overdue', 'Просрочен')
    ]

    status = models.CharField(max_length=128, choices=status_choices)
    entry_date = models.DateTimeField(auto_now=True)
    contractor = models.ForeignKey(User, default="", null=True, blank=True, on_delete=models.CASCADE)
    resolution = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Исполнитель: {self.contractor}, статус: {self.status}, {self.entry_date}, Резолюция:{self.resolution} "

    class Meta:
        verbose_name_plural = "История изменений"


class ContractorPrice(models.Model):
    price = models.DecimalField(max_digits=11, decimal_places=2)
    position = models.ForeignKey(InquiryDetails, on_delete=models.CASCADE)
    contractor = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.position.name} {self.price}, Исполнитель: {self.contractor}"

    class Meta:
        verbose_name_plural = "Цена исполнителя"


class Payment(models.Model):
    payment_id = models.PositiveIntegerField(null=True, blank=True)
    inquiry = models.ForeignKey(PaymentInquiry, null=True, blank=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now=True)
    NMC = models.ForeignKey(ContractorPrice, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Расчет #{self.id}"

    class Meta:
        verbose_name_plural = "Расчеты"

