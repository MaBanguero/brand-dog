from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import Order, DeliveryCompany, Task, Distributor, Fee
from .serializer import UserSerializer, OrderSerializer, DistributorSerializer, GetOrderSerializer, GetDistributorSerializer, DeliveryCompanySerializer, GetDeliveryCompanySerializer, FeeSerializer, GetFeeSerializer
from rest_framework.renderers import JSONRenderer
import json
import requests

ORDER_STATUS = ["delivered","assigned", "pending", "picked up"]

@require_POST
@csrf_exempt
def login(request):
    data = json.loads(request.body)
    user = get_object_or_404(User, username=data['username'])

    if not user.check_password(data['password']):
        return JsonResponse({"error":"invalid password"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer  = UserSerializer(instance=user)


    return JsonResponse({'message':'Ok', 
                         'token': token.key, 
                         'user': serializer.data
                        }, status= status.HTTP_200_OK)

@require_POST
@csrf_exempt
def register(request):
    serializer = UserSerializer(data=json.loads(request.body))

    if serializer.is_valid():
        serializer.save()

        user = User.objects.get(username=serializer.data['username'])
        user.set_password(serializer.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return JsonResponse({
            'token': token.key,
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@require_POST
@csrf_exempt
def logout(request):
    return JsonResponse({}, status=500)


# Create your views here.

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def newOrder(request):

    serializer = OrderSerializer(data=json.loads(request.body))
    if serializer.is_valid():
        json_data = json.loads(request.body)
        created_at = timezone.now()
        last_guide = Order.objects.all().order_by('id').last()
        
        if last_guide:
            guide = last_guide.guide + 1
        else:
            guide = 1000000
        city = json_data["city"]
        price = calculatePrice(city)
        serializer.status = 'pending'
        order = Order.objects.create(
            email= serializer["email"],
            customer_name = serializer["customer_name"],
            provider_name = serializer["provider_name"],
            city = serializer["city"],
            customer_address_2 = serializer["customer_address_2"],
            customer_address = serializer["customer_address"],
            provider_address_2 = serializer["provider_address_2"],
            provider_address = serializer["provider_address"],
            created_at = created_at,
            guide= guide,
            price= price, 
            status= serializer["status"],
            buyer_platform= 'DROPI',
            delivery_company= assignDeliveryCompany(city)
        )
        order.save()
        
        return JsonResponse({
                'message':'New Order Created',
                'data': {
                    'guide': order.guide,
                    'price': order.price
                }
        })
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getOrder(request, order_id=""):
    
    if order_id:
        order = Order.objects.get(pk=order_id)
        serializer = GetOrderSerializer(order)
        """data = {
            "email": order.email,
            "full_name": order.full_name,
            "city": order.city,
            "address_2": order.address_2,
            "address": order.address,
            "created_at": order.created_at, 
            "guide": order.guide,
            "price": order.price,
            "status": order.status,
            "buyer_platform": order.buyer_platform,
            "delivery_company": order.delivery_company.id 
        }"""
    else:
        order = Order.objects.all()
        serializer = GetOrderSerializer(order, many=True)
        #data =  Order.collection_to_json(collection)
        
    
    data = serializer.data

    return JsonResponse({
        'message':'Ok',
        'data': data
    })

@csrf_exempt
@require_http_methods('PATCH')
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def updateOrder(request):
    try: 
        data = json.loads(request.body)
        order = Order.objects.get(pk=data['id'])
        if order.status == 'picked up' or order.status == 'delivered':
            return JsonResponse({
            'message':'Order can not be updated',
            'data': {}
        })
        for key, value in data.items():
            if not key == 'guide' or key == 'status':  
                setattr(order, key, value)
        order.save()
        return JsonResponse({
            'message':'Order updated',
            'data': {
                'order_id': order.id,
                'order_guide': order.guide     
            }
        })
    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def assignDeliveryCompany(city):
    company =  DeliveryCompany.objects.filter(city=city)[0]
    return company

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def assignDistributor(request):
    json_data = json.loads(request.body)
    order = Order.objects.get(pk=json_data['orderId'])
    distributor = Distributor.objects.get(pk=json_data['distributorId'])
    task = Task.objects.create(distributor=distributor, order=order)
    task.save()
    order.status = 'assigned'
    order.save()
    sendMessage('Se te ha asignado una orden', distributor.telephone)
    return JsonResponse({
            'message':'Order Assigned',
            'data': {
                'distributor': {
                    'name':distributor.full_name,
                    'telephone': distributor.telephone
                }
            }
    })

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createDistributor(request):
    data = json.loads(request.body)
    serializer =  DistributorSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        deliveryCompany = DeliveryCompany.objects.get(pk=serializer.data['delivery_company'])
        data['deliveryCompany'] = deliveryCompany
        distributor =  Distributor.objects.create(delivery_company = deliveryCompany, full_name = data['full_name'])
        
        distributor.save()
        return JsonResponse({
            'message':'Distributor Created',
            'data': {
                'distributor_name': data['full_name'],
                'id': distributor.id
            }
    })
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createDeliveryCompany(request):
    data = json.loads(request.body)
    serializer =  DeliveryCompanySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        deliveryCompany = DeliveryCompany(**serializer.data)
        deliveryCompany.save()
        return JsonResponse({
            'message':'Delivery Company Created',
            'data': {
                'company_name': data['company_name'],
                'id': deliveryCompany.id
            }
    })
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getDeliveryCompany(request, delivery_company_id=""):
    
    if delivery_company_id:
        deliveryCompany = DeliveryCompany.objects.get(pk=delivery_company_id)
        serializer = GetDeliveryCompanySerializer(deliveryCompany)
    else:
        order = DeliveryCompany.objects.all()
        serializer = GetDeliveryCompanySerializer(order, many=True)
        
    data = serializer.data

    return JsonResponse({
        'message':'Ok',
        'data': data
    })


@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getDistributor(request, company_id):
    deliveryCompany = get_object_or_404(DeliveryCompany, id=company_id )
    distributor = Distributor.objects.filter(delivery_company = deliveryCompany)
    serializer = GetDistributorSerializer(distributor, many=True)
    return JsonResponse({
            'message':'OK',
            'data': {
                'distributor': serializer.data
            }
    })

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def createFee(request):
    data = json.loads(request.body)
    serializer =  FeeSerializer(data=data)
    if serializer.is_valid():
        fee = Fee(**serializer.data)
        fee.save()
        return JsonResponse({
            'message':'Fee Created',
            'data': {
                'company_name': data['city'],
                'id': fee.id
            }
    })
    else:
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getFee(request, city):
    if city:
        fee = Fee.objects.filter(city=city)
        serializer = FeeSerializer(fee)
    else:
        fee = Fee.objects.all()
        serializer = FeeSerializer(fee, many=True)
        
    data = serializer.data

    return JsonResponse({
        'message':'Ok',
        'data': data
    })

def calculatePrice(city):
    return Fee.objects.filter(city=city.lower())[0].price


def sendMessage(message, telephone):
    url = 'http://149.50.139.227:3002/sendmessage'
    data= {
        "message": message,
        "telephone": telephone
    }
    
    # Send GET request to the external API
    json_data = json.dumps(data)

    # Set headers to indicate JSON content
    headers = {'Content-Type': 'application/json'}

    # Send POST request to the external API
    response = requests.post(url, data=json_data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        #data = response.json()
        return JsonResponse({'data': 'OK'})
    else:
        # Handle errors
        return JsonResponse({'error': 'Failed to fetch data'}, status=500)