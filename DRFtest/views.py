from django.http import JsonResponse
from rest_framework import status as status_
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.utils import json
from django.core.exceptions import ValidationError
from .models import InquiryDetails, InquiryHistory, Payment, \
    PaymentInquiry, ContractorPrice
from .validators import validate_okpd, format_okpd
from django.contrib.auth.models import User
from .serializers import PaymentInquirySerializer, ContractorSerializer, PaymentSerializer


def get_contractor_list(request):
    u = User.objects.all()
    u = u.filter(is_staff=False)
    serializer = ContractorSerializer(u, many=True)
    return JsonResponse(serializer.data, safe=False)


def get_inquiry_list(request):
    p = PaymentInquiry.objects.all()
    status_exact = request.GET.get('current_status_exact')
    status = request.GET.get('current_status')
    serializer = PaymentInquirySerializer(p, many=True)

    if status_exact:
        p = p.filter(current_status__status=status_exact)
        serializer = PaymentInquirySerializer(p, many=True)
        return JsonResponse(serializer.data, safe=False)

    if status:
        status = status.split("-")
        q = PaymentInquiry.objects.filter(current_status__status__in=status)
        serializer = PaymentInquirySerializer(q, many=True)
        return JsonResponse(serializer.data, safe=False)

    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_inquiry_by_id(request, id):
    try:
        p = PaymentInquiry.objects.get(pk=id)
    except PaymentInquiry.DoesNotExist:
        return Response(status=status_.HTTP_404_NOT_FOUND)

    serializer = PaymentInquirySerializer(p)
    return JsonResponse(serializer.data)


@api_view(['GET'])
def get_inquiry_details(request, id):
    try:
        p = PaymentInquiry.objects.get(pk=id)
    except PaymentInquiry.DoesNotExist:
        return Response(status=status_.HTTP_404_NOT_FOUND)

    d = InquiryDetails.objects.filter(inquiry=p)
    serializer = PaymentInquirySerializer(d, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_inquiry_payments(request):
    p = Payment.objects.all()
    serializer = PaymentSerializer(p, many=True)
    return JsonResponse(serializer.data, safe=False)


def add_details(data, new_payment):
    if data.get('product') and data.get('amount') and \
            data.get('okei') and data.get('okpd'):
        details_name = data['product']
        amount = data['amount']
        okei = data['okei']
        okpd = data['okpd']
        try:
            validate_okpd(okpd)
        except ValidationError:
            return Response(status=status_.HTTP_400_BAD_REQUEST)
        try:
            amount = int(amount)
            okpd = format_okpd(okpd)
            i = InquiryDetails.objects.create(name=details_name, amount=amount,
                                              OKEI=okei, OKPD2=okpd, inquiry=new_payment)
            print(i)
        except ValueError:
            return Response(status=status_.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
def create_inquiry(request):
    data = json.dumps(request.data)
    data = json.loads(data)
    name = data.get('name')
    status = data.get('status')
    if not name or not status:
        return Response(status=status_.HTTP_400_BAD_REQUEST)

    st = InquiryHistory.objects.create(status=status)
    new_payment = PaymentInquiry.objects.create(name=name, current_status=st)

    # InquiryDetails
    add_details(data, new_payment)

    contractor_id = data.get('contractor_id')
    resolution = data.get('resolution')
    deadline = data.get('deadline')
    payment = data.get('payment_id')

    if contractor_id:
        try:
            contractor = User.objects.get(pk=contractor_id)
            st.contractor = contractor
        except User.DoesNotExist:
            return Response(status=status_.HTTP_404_NOT_FOUND)

    if resolution:
        st.resolution = resolution

    if deadline:
        if deadline != '':
            new_payment.deadline_date = deadline
            new_payment.save()
    if payment:
        try:
            payment = int(payment)
        except ValueError:
            Response(status=status_.HTTP_400_BAD_REQUEST)
        try:
            p = Payment.objects.get(pk=payment)
            new_payment.payment_m = p
            new_payment.save()
        except Payment.DoesNotExist:
            return Response(status=status_.HTTP_404_NOT_FOUND)

    st.save()
    serializer = PaymentInquirySerializer(new_payment)
    return JsonResponse(serializer.data, safe=False, status=201)


@csrf_exempt
@api_view(['POST'])
def create_payment(request):
    data = json.loads(request.data)
    payment_id = data.get('id')
    inquiry = data.get('inquiry_id')
    nmc = data.get('nmc_id')
    p = Payment.objects.create()
    if payment_id:
        p.payment_id = payment_id
        p.save()
    if inquiry:
        try:
            i = PaymentInquiry.objects.get(pk=inquiry)
            p.inquiry = i
            p.save()
        except PaymentInquiry.DoesNotExist:
            return Response(status=status_.HTTP_404_NOT_FOUND)
    if nmc:
        try:
            nmc = ContractorPrice.objects.get(pk=nmc)
            p.NMC = nmc
            p.save()
        except ContractorPrice.DoesNotExist:
            return Response(status=status_.HTTP_404_NOT_FOUND)
    serializer = PaymentSerializer(p)
    return JsonResponse(serializer.data, safe=False, status=201)
