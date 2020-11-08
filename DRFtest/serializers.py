from rest_framework import serializers
from .models import InquiryDetails, InquiryHistory, Payment, PaymentInquiry, ContractorPrice
from django.contrib.auth.models import User


class ContractorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class InquiryDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InquiryDetails
        fields = '__all__'


class PaymentInquiryHistorySerializer(serializers.ModelSerializer):
    contractor = ContractorSerializer(read_only=True)

    class Meta:
        model = InquiryHistory
        fields = '__all__'


class PaymentInquirySerializer(serializers.ModelSerializer):
    current_status = PaymentInquiryHistorySerializer(read_only=True)

    class Meta:
        model = PaymentInquiry
        fields = '__all__'


class ContractorPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorPrice
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    inquiry = PaymentInquirySerializer(read_only=True)
    NMC = ContractorPriceSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'

