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

# Create your views here.
def home(request):
    from datetime import date
    today = date.today()
    
    # Fetch low quantity products
    low_quantity_products = Products.objects.filter(quantity__lte=models.F('low_quantity_threshold'))

    # Fetch most sold products
    most_sold_products = SalesItems.objects.values('product_id__name').annotate(total_sold=Sum('qty')).order_by('-total_sold')[:5]

    context = {
        'categories': Products.objects.count(),
        'products': Products.objects.count(),
        'transaction': Sales.objects.filter(date_added__date=today).count(),
        'total_sales': Sales.objects.filter(date_added__date=today).aggregate(total=Sum('grand_total'))['total'],
        'low_quantity_products': low_quantity_products,
        'most_sold_products': most_sold_products,
    }
    return render(request, 'posApp/home.html', context)
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
@login_required
def manage_products(request):
    product = {}
    categories = Category.objects.filter(status = 1).all()
    if request.method == 'GET':
        data =  request.GET
        id = ''
        if 'id' in data:
            id= data['id']
        if id.isnumeric() and int(id) > 0:
            product = Products.objects.filter(id=id).first()
    
    context = {
        'product' : product,
        'categories' : categories
    }
    return render(request, 'posApp/manage_product.html',context)
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

@login_required
def save_product(request):
    data = request.POST
    resp = {'status': 'failed'}
    id = data.get('id', '')
    code = data.get('code', '')

    if id.isnumeric() and int(id) > 0:
        check = Products.objects.exclude(id=id).filter(code=code).exists()
    else:
        check = Products.objects.filter(code=code).exists()

    if check:
        resp['msg'] = "Product Code Already Exists in the database"
    else:
        try:
            category = Category.objects.get(id=data['category_id'])
            if id.isnumeric() and int(id) > 0:
                product = Products.objects.get(id=id)
                product.code = code
                product.category = category
                product.name = data['name']
                product.description = data['description']
                product.price = float(data['price'])
                product.status = data['status']
                product.quantity = int(data['quantity'])
                product.low_quantity_threshold = int(data['low_quantity_threshold'])
                product.save()
            else:
                Products.objects.create(
                    code=code,
                    category=category,
                    name=data['name'],
                    description=data['description'],
                    price=float(data['price']),
                    status=data['status'],
                    quantity=int(data['quantity']),
                    low_quantity_threshold=int(data['low_quantity_threshold'])
                )
            resp['status'] = 'success'
            messages.success(request, 'Product Successfully saved.')
        except Category.DoesNotExist:
            resp['msg'] = "Category does not exist"
        except Exception as e:
            resp['msg'] = f"An error occurred: {str(e)}"
    return HttpResponse(json.dumps(resp), content_type="application/json")

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


@login_required
# 


def salesList(request):
    # Get all sales
    sales = Sales.objects.all()

    sale_data = []
    for sale in sales:
        data = {}
        # Collect basic sale information
        for field in sale._meta.get_fields(include_parents=False):
            if field.related_model is None:
                data[field.name] = getattr(sale, field.name)
        
        # Collect related items for each sale
        items = SalesItems.objects.filter(sale_id=sale).all()
        data['items'] = items
        data['item_count'] = items.count()  # Count of items in the sale

        # Format tax_amount if it exists
        if 'tax_amount' in data:
            data['tax_amount'] = format(float(data['tax_amount']), '.2f')
        
        sale_data.append(data)

    context = {
        'page_title': 'Sales Transactions',
        'sale_data': sale_data,
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