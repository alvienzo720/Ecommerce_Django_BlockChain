from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from web3 import Web3



# Create your views here.
def store(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items

	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
		cartItems = order['get_cart_items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items

	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


def checkout(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		items = []
		order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}
	context = {'items':items, 'order':order,'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id




	ganache_url = "http://127.0.0.1:7545"

		# connect to the blockchain 
	web3 = Web3(Web3.HTTPProvider(ganache_url))

		# check if we are connected
	print("Are are connected ", web3.isConnected())

		#print the block number 
	print("Block Number" ,web3.eth.blockNumber)



	account_1 = "0xA5cD10D1B035eF8F4c30D43646ce3431F7F54Cd5"

	account_2 = "0x37897B989790c8D3a4A5e5261C296506cdbfD00A"


	private_key = "c70273dfe25ae8ead357943d47c1d0bc42e5901765b8f70319615f871484b601"

	nonce = web3.eth.getTransactionCount(account_1)
		#build a trasnaction 
	if total >=25000:
		
		tx = {
			'nonce': nonce,
			'to': account_2,
			'value': web3.toWei(0.5, 'ether'),
			'gas': 2000000,
			'gasPrice':web3.toWei('50','gwei')

		}

		#sign the transaction

		sign_tx = web3.eth.account.signTransaction(tx, private_key)


		#send transaction
		txt_hash = web3.eth.sendRawTransaction(sign_tx.rawTransaction)


		#get transaction hash

		balance1 = web3.eth.get_balance(account_1)
		balance2 = web3.eth.get_balance(account_2)

		print("Blanace is for the sender: ", balance1)
		print("Blanace is for the reciver: ", balance2)


		print(web3.toHex(txt_hash))

	if total < 30000:
		print("No reward")


	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		region=data['shipping']['region'],
		village=data['shipping']['village'],
		)

	return JsonResponse('Payment submitted..', safe=False)