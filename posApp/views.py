from pickle import FALSE
from django.shortcuts import redirect, render
from django.http import HttpResponse
from flask import jsonify
from posApp.models import Category, Products, Sales, SalesItems
from django.db.models import Count, Sum, F
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
import json, sys
from datetime import date, datetime
from django.db import models

# for pie filter
# from django.shortcuts import render
# from django.http import JsonResponse
# from .models import SalesItems
# from django.db.models import Sum
# from django.utils.dateparse import parse_date

# Login
def login_user(request):
    logout(request)
    resp = {"status":'failed','msg':''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status']='success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp),content_type='application/json')

#Logout
def logoutuser(request):
    logout(request)
    return redirect('/')



# def home(request):
#     from datetime import date
#     today = date.today()
    
#     # Fetch low quantity products
#     low_quantity_products = Products.objects.filter(quantity__lte=models.F('low_quantity_threshold'))

#     # Fetch most sold products
#     most_sold_products = SalesItems.objects.values('product_id__name').annotate(total_sold=Sum('qty')).order_by('-total_sold')[:5]

#     context = {
#         'categories': Products.objects.count(),
#         'products': Products.objects.count(),
#         'transaction': Sales.objects.filter(date_added__date=today).count(),
#         'total_sales': Sales.objects.filter(date_added__date=today).aggregate(total=Sum('grand_total'))['total'],
#         'low_quantity_products': low_quantity_products,
#         'most_sold_products': most_sold_products,
#     }
#     return render(request, 'posApp/home.html', context)
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import Sales  # Make sure to import your Sale model

from django.shortcuts import render
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from .models import Products, Sales, SalesItems

def home(request):
    today = timezone.now().date()
    seven_days_ago = today - timedelta(days=7)
    six_months_ago = today - relativedelta(months=6)
    one_month_ago = today - relativedelta(months=1)

    # Fetch low quantity products
    low_quantity_products = Products.objects.filter(quantity__lte=models.F('low_quantity_threshold'))

    # Fetch most sold products
    most_sold_products = SalesItems.objects.values('product_id__name').annotate(total_sold=Sum('qty')).order_by('-total_sold')[:5]
    
    # Fetch sales data for the last 7 days
    sales_last_7_days = Sales.objects.filter(date_added__date__range=[seven_days_ago, today])
    
    # Prepare data for the 7 days chart
    sales_data_7_days = {}
    for sale in sales_last_7_days:
        date = sale.date_added.date()
        sales_data_7_days[date] = sales_data_7_days.get(date, 0) + sale.grand_total
    
    # Fill missing days with 0 sales
    all_dates_7_days = [seven_days_ago + timedelta(days=i) for i in range(7)]
    sales_for_chart_7_days = [{'date': date.strftime('%Y-%m-%d'), 'total_sales': sales_data_7_days.get(date, 0)} for date in all_dates_7_days]
    
    # Fetch sales data for the last 6 months
    sales_last_6_months = Sales.objects.filter(date_added__date__range=[six_months_ago, today])
    
    # Prepare data for the 6 months chart
    sales_data_6_months = {}
    for sale in sales_last_6_months:
        month = sale.date_added.date().strftime('%Y-%m')
        sales_data_6_months[month] = sales_data_6_months.get(month, 0) + sale.grand_total
    
    # Fill missing months with 0 sales
    all_months = [(six_months_ago + relativedelta(months=i)).strftime('%Y-%m') for i in range(7)]
    sales_for_chart_6_months = [{'month': month, 'total_sales': sales_data_6_months.get(month, 0)} for month in all_months]
    
    # Fetch most sold products for the past month
    sales_last_1_month = SalesItems.objects.filter(sale_id__date_added__date__range=[one_month_ago, today])
    
    # Prepare data for the most sold products in the past month chart
    most_sold_products_month = SalesItems.objects.filter(sale_id__date_added__date__range=[one_month_ago, today]).values('product_id__name').annotate(total_sold=Sum('qty')).order_by('-total_sold')
    
    context = {
        'categories': Products.objects.count(),
        'products': Products.objects.count(),
        'transaction': Sales.objects.filter(date_added__date=today).count(),
        'total_sales': Sales.objects.filter(date_added__date=today).aggregate(total=Sum('grand_total'))['total'],
        'low_quantity_products': low_quantity_products,
        'most_sold_products': most_sold_products,
        'sales_last_7_days': sales_for_chart_7_days,
        'sales_last_6_months': sales_for_chart_6_months,
        'most_sold_products_month': most_sold_products_month,
    }
    return render(request, 'posApp/home.html', context)



# from datetime import date, timedelta
# from django.db.models import Sum
# from .models import Products, Sales, SalesItems

# from datetime import date, timedelta
# from django.db.models import Sum, F
# from django.shortcuts import render
# from .models import Products, Sales, SalesItems

# def home(request):
#     today = date.today()
#     thirty_days_ago = today - timedelta(days=30)

#     # Fetch low quantity products
#     low_quantity_products = Products.objects.filter(quantity__lte=F('low_quantity_threshold'))

#     # Fetch most sold products
#     most_sold_products = SalesItems.objects.values('product_id__name').annotate(total_sold=Sum('qty')).order_by('-total_sold')[:5]

#     # Fetch sales data for the last 30 days
#     sales_last_30_days = Sales.objects.filter(date_added__date__gte=thirty_days_ago, date_added__date__lte=today)
#     daily_sales = sales_last_30_days.extra({'date_added': "date(date_added)"}).values('date_added').annotate(total=Sum('grand_total')).order_by('date_added')

#     # Format daily_sales for JSON output
#     daily_sales_formatted = [{'date_added': sale['date_added'].strftime('%Y-%m-%d') if isinstance(sale['date_added'], datetime) else sale['date_added'], 'total': sale['total']} for sale in daily_sales]

#     context = {
#         'categories': Products.objects.count(),
#         'products': Products.objects.count(),
#         'transaction': Sales.objects.filter(date_added__date=today).count(),
#         'total_sales': Sales.objects.filter(date_added__date=today).aggregate(total=Sum('grand_total'))['total'],
#         'low_quantity_products': low_quantity_products,
#         'most_sold_products': most_sold_products,
#         'daily_sales': daily_sales_formatted,  # Pass formatted data
#     }
#     return render(request, 'posApp/home.html', context)



# def home(request):
#     categories_count = Category.objects.count()
#     products_count = Products.objects.count()
#     today = datetime.now().date()
#     today_transactions = Sales.objects.filter(date_added__date=today).count()
#     today_sales = Sales.objects.filter(date_added__date=today).aggregate(total_sales=Sum('grand_total'))['total_sales'] or 0

#     low_quantity_products = Products.objects.filter(quantity__lte=models.F('low_quantity_threshold'), status=1)

#     context = {
#         'categories': categories_count,
#         'products': products_count,
#         'transaction': today_transactions,
#         'total_sales': today_sales,
#         'low_quantity_products': low_quantity_products,
#     }
#     return render(request, 'posApp/home.html', context)
def about(request):
    context = {
        'page_title':'About',
    }
    return render(request, 'posApp/about.html',context)

#Categories
@login_required
def category(request):
    category_list = Category.objects.all()
    # category_list = {}
    context = {
        'page_title':'Category List',
        'category':category_list,
    }
    return render(request, 'posApp/category.html',context)
@login_required
def manage_category(request):
    category = {}
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            category = Category.objects.filter(id=id).first()
    
    context = {
        'category' : category
    }
    return render(request, 'posApp/manage_category.html',context)

@login_required
def save_category(request):
    data =  request.POST
    resp = {'status':'failed'}
    try:
        if (data['id']).isnumeric() and int(data['id']) > 0 :
            save_category = Category.objects.filter(id = data['id']).update(name=data['name'], description = data['description'],status = data['status'])
        else:
            save_category = Category(name=data['name'], description = data['description'],status = data['status'])
            save_category.save()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully saved.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

@login_required
def delete_category(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Category.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Category Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")

# Products
def products(request):
    product_list = Products.objects.all()
    context = {
        'page_title':'Product List',
        'products':product_list,
    }
    return render(request, 'posApp/products.html',context)
# @login_required
# def manage_products(request):
#     product = {}
#     categories = Category.objects.filter(status = 1).all()
#     if request.method == 'GET':
#         data =  request.GET
#         id = ''
#         if 'id' in data:
#             id= data['id']
#         if id.isnumeric() and int(id) > 0:
#             product = Products.objects.filter(id=id).first()
    
#     context = {
#         'product' : product,
#         'categories' : categories
#     }
#     return render(request, 'posApp/manage_product.html',context)

def manage_product(request):
    product_id = request.GET.get('id')
    product = get_object_or_404(Products, id=product_id) if product_id else None
    categories = Category.objects.all()
    context = {
        'product': product,
        'categories': categories
    }
    return render(request, 'posApp/manage_product.html', context)
def test(request):
    categories = Category.objects.all()
    context = {
        'categories' : categories
    }
    return render(request, 'posApp/test.html',context)
# @login_required
# def save_product(request):
#     data = request.POST
#     resp = {'status': 'failed'}
#     id = ''
#     if 'id' in data:
#         id = data['id']
#     if id.isnumeric() and int(id) > 0:
#         check = Products.objects.exclude(id=id).filter(code=data['code']).all()
#     else:
#         check = Products.objects.filter(code=data['code']).all()
#     if len(check) > 0:
#         resp['msg'] = "Product Code Already Exists in the database"
#     else:
#         category = Category.objects.filter(id=data['category_id']).first()
#         try:
#             if id.isnumeric() and int(id) > 0:
#                 save_product = Products.objects.filter(id=id).update(
#                     code=data['code'],
#                     category_id=category,
#                     name=data['name'],
#                     description=data['description'],
#                     price=float(data['price']),
#                     status=data['status'],
#                     quantity=int(data['quantity']),
#                     low_quantity_threshold=int(data['low_quantity_threshold'])  # Update threshold
#                 )
#             else:
#                 save_product = Products(
#                     code=data['code'],
#                     category_id=category,
#                     name=data['name'],
#                     description=data['description'],
#                     price=float(data['price']),
#                     status=data['status'],
#                     quantity=int(data['quantity']),
#                     low_quantity_threshold=int(data['low_quantity_threshold'])  # Set threshold
#                 )
#                 save_product.save()
#             resp['status'] = 'success'
#             messages.success(request, 'Product Successfully saved.')
#         except:
#             resp['status'] = 'failed'
#     return HttpResponse(json.dumps(resp), content_type="application/json")

# @login_required
# def save_product(request):
#     data = request.POST
#     resp = {'status': 'failed'}
#     id = data.get('id', '')
#     code = data.get('code', '')

#     if id.isnumeric() and int(id) > 0:
#         check = Products.objects.exclude(id=id).filter(code=code).exists()
#     else:
#         check = Products.objects.filter(code=code).exists()

#     if check:
#         resp['msg'] = "Product Code Already Exists in the database"
#     else:
#         try:
#             category = Category.objects.get(id=data['category_id'])
#             if id.isnumeric() and int(id) > 0:
#                 product = Products.objects.get(id=id)
#                 product.code = code
#                 product.category = category
#                 product.name = data['name']
#                 product.description = data['description']
#                 product.price = float(data['price'])
#                 product.status = data['status']
#                 product.quantity = int(data['quantity'])
#                 product.low_quantity_threshold = int(data['low_quantity_threshold'])
#                 product.save()
#             else:
#                 Products.objects.create(
#                     code=code,
#                     category=category,
#                     name=data['name'],
#                     description=data['description'],
#                     price=float(data['price']),
#                     status=data['status'],
#                     quantity=int(data['quantity']),
#                     low_quantity_threshold=int(data['low_quantity_threshold'])
#                 )
#             resp['status'] = 'success'
#             messages.success(request, 'Product Successfully saved.')
#         except Category.DoesNotExist:
#             resp['msg'] = "Category does not exist"
#         except Exception as e:
#             resp['msg'] = f"An error occurred: {str(e)}"
#     return HttpResponse(json.dumps(resp), content_type="application/json")
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Products, Category
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def save_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('id')
        if product_id:
            product = get_object_or_404(Products, id=product_id)
        else:
            product = Products()

        product.code = request.POST.get('code')
        product.low_quantity_threshold = request.POST.get('low_quantity_threshold')
        product.category_id = request.POST.get('category_id')
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.quantity = request.POST.get('quantity')
        product.status = request.POST.get('status')

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        try:
            product.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'msg': str(e)})

    return JsonResponse({'status': 'failed', 'msg': 'Invalid request'})
# @login_required
# def save_product(request):
#     data = request.POST
#     resp = {'status':'failed'}
#     id = ''
#     if 'id' in data:
#         id = data['id']
#     if id.isnumeric() and int(id) > 0:
#         check = Products.objects.exclude(id=id).filter(code=data['code']).all()
#     else:
#         check = Products.objects.filter(code=data['code']).all()
#     if len(check) > 0:
#         resp['msg'] = "Product Code Already Exists in the database"
#     else:
#         category = Category.objects.filter(id=data['category_id']).first()
#         try:
#             if id.isnumeric() and int(id) > 0:
#                 save_product = Products.objects.filter(id=id).update(
#                     code=data['code'],
#                     category_id=category,
#                     name=data['name'],
#                     description=data['description'],
#                     price=float(data['price']),
#                     status=data['status'],
#                     quantity=int(data['quantity'])  # Update quantity
#                 )
#             else:
#                 save_product = Products(
#                     code=data['code'],
#                     category_id=category,
#                     name=data['name'],
#                     description=data['description'],
#                     price=float(data['price']),
#                     status=data['status'],
#                     quantity=int(data['quantity'])  # Set quantity
#                 )
#                 save_product.save()
#             resp['status'] = 'success'
#             messages.success(request, 'Product Successfully saved.')
#         except:
#             resp['status'] = 'failed'
#     return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def delete_product(request):
    data =  request.POST
    resp = {'status':''}
    try:
        Products.objects.filter(id = data['id']).delete()
        resp['status'] = 'success'
        messages.success(request, 'Product Successfully deleted.')
    except:
        resp['status'] = 'failed'
    return HttpResponse(json.dumps(resp), content_type="application/json")
@login_required
def pos(request):
    products = Products.objects.filter(status = 1)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html',context)

@login_required
def pos(request):
    products = Products.objects.filter(status = 1)
    product_json = []
    for product in products:
        product_json.append({'id':product.id, 'name':product.name, 'price':float(product.price)})
    context = {
        'page_title' : "Point of Sale",
        'products' : products,
        'product_json' : json.dumps(product_json)
    }
    # return HttpResponse('')
    return render(request, 'posApp/pos.html',context)

@login_required
def checkout_modal(request):
    grand_total = 0
    if 'grand_total' in request.GET:
        grand_total = request.GET['grand_total']
    context = {
        'grand_total' : grand_total,
    }
    return render(request, 'posApp/checkout.html',context)

@login_required
def save_pos(request):
    resp = {'status': 'failed', 'msg': ''}
    data = request.POST
    pref = datetime.now().year + datetime.now().year
    i = 1
    while True:
        code = '{:0>5}'.format(i)
        i += 1
        check = Sales.objects.filter(code=str(pref) + str(code)).all()
        if len(check) <= 0:
            break
    code = str(pref) + str(code)

    try:
        sales = Sales(
            code=code,
            sub_total=data['sub_total'],
            tax=data['tax'],
            tax_amount=data['tax_amount'],
            grand_total=data['grand_total'],
            tendered_amount=data['tendered_amount'],
            amount_change=data['amount_change']
        )
        sales.save()
        sale_id = sales.pk
        i = 0
        for prod in data.getlist('product_id[]'):
            product_id = prod
            product = Products.objects.filter(id=product_id).first()
            qty = int(data.getlist('qty[]')[i])
            price = float(data.getlist('price[]')[i])
            total = qty * price

            # Deduct the quantity
            if product.quantity >= qty:
                product.quantity -= qty
                product.save()
            else:
                resp['msg'] = f"Not enough stock for product {product.name}"
                return HttpResponse(json.dumps(resp), content_type="application/json")

            sales_item = SalesItems(
                sale_id=sales,
                product_id=product,
                qty=qty,
                price=price,
                total=total
            )
            sales_item.save()
            i += 1

        resp['status'] = 'success'
        resp['sale_id'] = sale_id
        messages.success(request, "Sale Record has been saved.")
    except Exception as e:
        resp['msg'] = f"An error occurred: {str(e)}"
    return HttpResponse(json.dumps(resp), content_type="application/json")


# @login_required
# # 


# def salesList(request):
#     # Get all sales
#     sales = Sales.objects.all()

#     sale_data = []
#     for sale in sales:
#         data = {}
#         # Collect basic sale information
#         for field in sale._meta.get_fields(include_parents=False):
#             if field.related_model is None:
#                 data[field.name] = getattr(sale, field.name)
        
#         # Collect related items for each sale
#         items = SalesItems.objects.filter(sale_id=sale).all()
#         data['items'] = items
#         data['item_count'] = items.count()  # Count of items in the sale

#         # Format tax_amount if it exists
#         if 'tax_amount' in data:
#             data['tax_amount'] = format(float(data['tax_amount']), '.2f')
        
#         sale_data.append(data)

#     context = {
#         'page_title': 'Sales Transactions',
#         'sale_data': sale_data,
#     }
    
#     return render(request, 'posApp/sales.html', context)

from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render
from .models import Sales, SalesItems
import csv
# import xlwt
from django.http import JsonResponse

@login_required
# def salesList(request):
#     # Get the start and end dates from the request
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
    
#     # Filter sales based on date range
#     sales = Sales.objects.all()
#     if start_date:
#         sales = sales.filter(date_added__date__gte=start_date)
#     if end_date:
#         sales = sales.filter(date_added__date__lte=end_date)

#     sale_data = []
#     for sale in sales:
#         data = {}
#         for field in sale._meta.get_fields(include_parents=False):
#             if field.related_model is None:
#                 data[field.name] = getattr(sale, field.name)
        
#         items = SalesItems.objects.filter(sale_id=sale).all()
#         data['items'] = items
#         data['item_count'] = items.count()
#         if 'tax_amount' in data:
#             data['tax_amount'] = format(float(data['tax_amount']), '.2f')
#         sale_data.append(data)

#     context = {
#         'page_title': 'Sales Transactions',
#         'sale_data': sale_data,
#     }
    
#     return render(request, 'posApp/sales.html', context)
def salesList(request):
    # Get the start and end dates from the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Filter sales based on date range
    sales = Sales.objects.all()
    if start_date:
        sales = sales.filter(date_added__date__gte=start_date)
    if end_date:
        sales = sales.filter(date_added__date__lte=end_date)

    sale_data = []
    total_grand_total = 0
    total_tax_amount = 0
    total_item_count = 0

    for sale in sales:
        data = {}
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale, field.name)
        
        items = SalesItems.objects.filter(sale_id=sale).all()
        data['items'] = items
        data['item_count'] = items.count()
        
        if 'grand_total' in data:
            total_grand_total += float(data['grand_total'])
        
        if 'tax_amount' in data:
            total_tax_amount += float(data['tax_amount'])
            data['tax_amount'] = format(float(data['tax_amount']), '.2f')
        
        total_item_count += data['item_count']
        sale_data.append(data)

    context = {
        'page_title': 'Sales Transactions',
        'sale_data': sale_data,
        'total_grand_total': total_grand_total,
        'total_tax_amount': total_tax_amount,
        'total_item_count': total_item_count,
    }
    
    return render(request, 'posApp/sales.html', context)
@login_required
def receipt(request):
    id = request.GET.get('id')
    sales = Sales.objects.filter(id = id).first()
    transaction = {}
    for field in Sales._meta.get_fields():
        if field.related_model is None:
            transaction[field.name] = getattr(sales,field.name)
    if 'tax_amount' in transaction:
        transaction['tax_amount'] = format(float(transaction['tax_amount']))
    ItemList = SalesItems.objects.filter(sale_id = sales).all()
    context = {
        "transaction" : transaction,
        "salesItems" : ItemList
    }

    return render(request, 'posApp/receipt.html',context)
    # return HttpResponse('')

import io
from django.http import HttpResponse
import csv
# import xlwt
# # from reportlab.lib.pagesizes import letter
# from reportlab.pdfgen import canvas
from .models import Sales, SalesItems

@login_required
def export_sales(request, file_format):
    # Get the start and end dates from the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filter sales based on date range
    sales = Sales.objects.all()
    if start_date:
        sales = sales.filter(date_added__date__gte=start_date)
    if end_date:
        sales = sales.filter(date_added__date__lte=end_date)

    if file_format == 'csv':
        return export_sales_csv(sales)
    elif file_format == 'excel':
        return export_sales_excel(sales)
    elif file_format == 'pdf':
        return export_sales_pdf(sales)
    else:
        return HttpResponse(status=400)

def export_sales_csv(sales):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'DateTime', 'Trans. Code', 'Total', 'Tax Inclusive', 'Items', 'Payment Mode'])

    for sale in sales:
        items = SalesItems.objects.filter(sale_id=sale).count()
        writer.writerow([
            sale.id, 
            sale.date_added, 
            sale.code, 
            sale.grand_total, 
            sale.tax_amount, 
            items,
            sale.payment_mode
        ])

    return response

def export_sales_excel(sales):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="sales.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Sales')

    row_num = 0
    columns = ['ID', 'DateTime', 'Trans. Code', 'Total', 'Tax Inclusive', 'Items', 'Payment Mode']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num])

    for sale in sales:
        row_num += 1
        items = SalesItems.objects.filter(sale_id=sale).count()
        row = [
            sale.id, 
            sale.date_added, 
            sale.code, 
            sale.grand_total, 
            sale.tax_amount, 
            items,
            sale.payment_mode
        ]
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num])

    wb.save(response)
    return response

def export_sales_pdf(sales):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales.pdf"'

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 40
    p.drawString(30, y, 'ID')
    p.drawString(80, y, 'DateTime')
    p.drawString(200, y, 'Trans. Code')
    p.drawString(300, y, 'Total')
    p.drawString(380, y, 'Tax Inclusive')
    p.drawString(480, y, 'Items')
    p.drawString(550, y, 'Payment Mode')

    for sale in sales:
        y -= 20
        items = SalesItems.objects.filter(sale_id=sale).count()
        p.drawString(30, y, str(sale.id))
        p.drawString(80, y, sale.date_added.strftime('%Y-%m-%d %H:%M'))
        p.drawString(200, y, sale.code)
        p.drawString(300, y, str(sale.grand_total))
        p.drawString(380, y, str(sale.tax_amount))
        p.drawString(480, y, str(items))
        p.drawString(550, y, sale.payment_mode)

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


@login_required
def delete_sale(request):
    resp = {'status':'failed', 'msg':''}
    id = request.POST.get('id')
    try:
        delete = Sales.objects.filter(id = id).delete()
        resp['status'] = 'success'
        messages.success(request, 'Sale Record has been deleted.')
    except:
        resp['msg'] = "An error occured"
        print("Unexpected error:", sys.exc_info()[0])
    return HttpResponse(json.dumps(resp), content_type='application/json')


@login_required
def low_quantity_products(request):
    low_quantity_products = Products.objects.filter(quantity__lte=F('low_quantity_threshold'), status=1)
    context = {
        'low_quantity_products': low_quantity_products,
    }
    return render(request, 'posApp/low_quantity_products.html', context)

# def filter_most_sold_products(request):
#     start_date = request.GET.get('start_date')
#     end_date = request.GET.get('end_date')
    
#     sales_items = SalesItems.objects.select_related('product_id', 'sale_id')

#     if start_date:
#         sales_items = sales_items.filter(sale_id__date_added__gte=parse_date(start_date))
#     if end_date:
#         sales_items = sales_items.filter(sale_id__date_added__lte=parse_date(end_date))

#     sales_data = sales_items.values('product_id__name').annotate(total_sold=Sum('qty')).order_by('-total_sold')[:5]
    
#     data = {
#         'labels': [sale['product_id__name'] for sale in sales_data],
#         'values': [sale['total_sold'] for sale in sales_data]
#     }
    
#     return JsonResponse(data)