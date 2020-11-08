from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework.utils import json

from .models import InquiryDetails, InquiryHistory, Payment, PaymentInquiry, ContractorPrice
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
    status_many = request.GET.get('current_status')
    serializer = PaymentInquirySerializer(p, many=True)

    if status_exact:
        print("tur")
        print(status_exact)
        p = p.filter(current_status__status=status_exact)
        serializer = PaymentInquirySerializer(p, many=True)
        return JsonResponse(serializer.data, safe=False)

    if status_many:
        pass

    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_inquiry_by_id(request, id):
    try:
        p = PaymentInquiry.objects.get(pk=id)
    except PaymentInquiry.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = PaymentInquirySerializer(p)
    return JsonResponse(serializer.data)


@api_view(['GET'])
def get_inquiry_details(request, id):
    try:
        p = PaymentInquiry.objects.get(pk=id)
    except PaymentInquiry.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    d = InquiryDetails.objects.filter(inquiry=p)
    serializer = PaymentInquirySerializer(d, many=True)
    return JsonResponse(serializer.data, safe=False)


@api_view(['GET'])
def get_inquiry_payments(request):
    p = Payment.objects.all()
    serializer = PaymentSerializer(p, many=True)
    return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@api_view(['POST'])
def create_inquiry(request):
    data = json.dumps(request.data)
    data = json.loads(data)
    name = data['name']
    status = data['status']
    deadline = data['deadline']
    payment = data['payment_id']
    resolution = data['resolution']
    contractor_id = data['contractor_id']

    st = InquiryHistory.objects.create(status=status)
    new_payment = PaymentInquiry.objects.create(name=name, current_status=st)
    if contractor_id:
        contractor = User.objects.get(pk=contractor_id)
        st.contractor = contractor
        st.save()
    if resolution:
        st.resolution = resolution
        st.save()
    if deadline:
        new_payment.deadline_date = deadline
        new_payment.save()
    if payment and payment != "":
        payment = int(payment)
        p = Payment.objects.get(pk=payment)
        new_payment.payment_m = p
        new_payment.save()

    serializer = PaymentInquirySerializer(new_payment)
    return JsonResponse(serializer.data, safe=False, status=201)


@csrf_exempt
@api_view(['POST'])
def create_payment(request):
    data = json.loads(request.data)
    print(data)
    payment_id = data['id']
    inquiry = data['inquiry_id']
    nmc = data['nmc_id']
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
            return Response(status=status.HTTP_404_NOT_FOUND)
    if nmc:
        try:
            nmc = ContractorPrice.objects.get(pk=nmc)
            p.NMC = nmc
            p.save()
        except ContractorPrice.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = PaymentSerializer(p)
    return JsonResponse(serializer.data, safe=False, status=201)

# @csrf_exempt
# def products(request):
#     if request.method == "GET":
#         products = Product.objects.all()
#         serializer = ProductSerializer(products, many=True)
#         return JsonResponse(serializer.data, safe=False)
#
#     elif request.method == "POST":
#         data = JSONParser().parse(request)
#         serializer = ProductSerializer(data=data)
#
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data, status=201)
#         return JsonResponse(serializer.errors, status=400)
#
# @csrf_exempt
# def product_detail(request, id):
#     product = Product.objects.get(id=id)
#     if request.method == "GET":
#         serializer = ProductSerializer(product)
#         return JsonResponse(serializer.data)
#
#     elif request.method == "PUT":
#         data = JSONParser().parse(request)
#         serializer = ProductSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return JsonResponse(serializer.data)
#         return JsonResponse(serializer.errors, status=400)
#
#     elif request.method == "DELETE":
#         product.delete()
#         return HttpResponse(status=204)
