from django.shortcuts import redirect, render
from market.context_processors import get_cart_amounts  
from market.models import Cart
from .forms import OrderForm
from .utils import generate_order_number
from .models import Order, OrderedFood, Payment
from accounts.utils import send_notification
import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import razorpay
from marketplace.settings import RZP_KEY_ID, RZP_KEY_SECRET



client = razorpay.Client(auth=(RZP_KEY_ID, RZP_KEY_SECRET))


# Create your views here.
@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count == 0:
        return redirect('marketplace')
    sub_total = get_cart_amounts(request)['subtotal']
    total_tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    tax_data = get_cart_amounts(request)['tax_dict']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(get_cart_amounts(request)['tax_dict'])
            order.total_tax = total_tax
            order.payment_method = request.POST['payment_method']
            order.save()
            order.order_number = generate_order_number(order.id)
            order.save()

            data = {
                'amount': float(order.total) * 100,
                'currency': 'INR',
                'receipt': 'receipt#'+order.order_number
            }
            rzp_order = client.order.create(data=data)
            rzp_order_id = rzp_order['id']
            context = {
                'cart_items': cart_items,
                'order': order,
                'rzp_order_id': rzp_order_id,
                'RZP_KEY_ID': RZP_KEY_ID,
                'rzp_amount': float(order.total) * 100
            }
            return render(request, 'orders/palce_order.html', context)

        else:
            print(form.errors)

    return render(request, 'orders/place_order.html')


@login_required(login_url='login')
def payment(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        payment_status = request.POST.get('payment_status')

        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=order.total,
            status=payment_status
        )
        payment.save()
        order.payment = payment
        order.is_ordered = True
        order.save()

        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            order_item = OrderedFood.objects.create(
                order=order,
                payment=payment,
                user=request.user,
                fooditem=item.fooditem,
                quantity=item.quantity,
                price=item.fooditem.price,
                amount=item.fooditem.price * item.quantity
            )
            order_item.save()

        mail_subject = 'Thank you for ordering with us!'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(mail_subject, mail_template, context)

        mail_subject = 'You have recieved a new order'
        mail_template = 'orders/new_order_received.html'
        to_emails = set()
        for i in cart_items:
            to_emails.add(i.fooditem.vendor.user.email)
        context = {
            'order': order,
            'to_emails': list(to_emails),
        }
        send_notification(mail_subject, mail_template, context)
        cart_items.delete()
        return JsonResponse({
            'status': 'success',
            'message': 'Payment processed successfully',
            'order_number': order_number,
            'transaction_id': transaction_id
        })



def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)
        subtotal = 0
        for item in ordered_food:
            subtotal += item.price * item.quantity
        tax_data = json.loads(order.tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')
