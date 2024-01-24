from fastapi import APIRouter, Body, Depends, Header, Request
from fastapi.responses import RedirectResponse
import stripe
from firebase_admin import auth
import uuid
from database.firebase import db
from routers.router_auth import get_current_user
router = APIRouter(
      tags=["Stripe"],
      prefix='/stripe'
)
  
# This is your test secret API key.
from dotenv import dotenv_values
config = dotenv_values(".env")
stripe.api_key = ""
YOUR_DOMAIN = 'http://localhost'

@router.get('/checkout')
async def stripe_checkout(request: Request):
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': '',
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
    except Exception as e:
        return str(e)

    response = RedirectResponse(url=checkout_session['url'])
    return response


@router.post('/webhook')
async def webhook_received(request: Request, stripe_signature: str = Header(None)):
    webhook_secret = "whsec_fd5d2abeb005c0790a0199927deac46d7c45fb662a350f79578af5b155f1a89a"
    data = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=data,
            sig_header=stripe_signature,
            secret=webhook_secret
        )
        event_data = event['data']
    except Exception as e:
        return {"error": str(e)}
    print(event_data)
    event_type = event['type']
    if event_type == 'checkout.session.completed':
        print('checkout session completed')
    elif event_type == 'invoice.paid':
        print('invoice paid')
        cust_email = event_data['object']['customer_email'] # email de notre customer
        fireBase_user = auth.get_user_by_email(cust_email) # Identifiant firebase correspondant (uid)
        cust_id =event_data['object']['customer'] # Stripe ref du customer
        item_id= event_data['object']['lines']['data'][0]['subscription_item']
        db.child("users").child(fireBase_user.uid).child("stripe").set({"item_id":item_id, "cust_id":cust_id}) # écriture dans la DB firebase      

    elif event_type == 'invoice.payment_failed':
        print('invoice payment failed')
    # else:
        # print(f'unhandled event: {event_type}')

    return {"status": "success"}

 