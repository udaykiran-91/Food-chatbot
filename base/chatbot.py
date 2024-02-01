from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import db_helper
from . import utils

inprogress_orders = {}

@csrf_exempt
def handle_request(request):
    if request.method == 'POST':
        # Parse the request body JSON sent by Dialogflow
        request_data = json.loads(request.body.decode('utf-8')) 
        parameters = request_data['queryResult']['parameters']
        intent = request_data['queryResult']['intent']['displayName']
        output_contexts = request_data['queryResult']['outputContexts']

        session_id = utils.extract_session_id(output_contexts[0]['name'])

        intent_handler_dict  ={
            "track.order - context: ongoing-tracking": track_order,
            "order.add - context: ongoing-order" : add_to_order,
            "order.complete - context: ongoing-order": complete_order,
            "order.remove - context: ongoing-order" : remove_from_order,
            "new.order":new_order,
        }

        return intent_handler_dict[intent](parameters,session_id)


    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    # intent = payload['queryResult']

def new_order(parameters: dict,session_id: str):
    if session_id in inprogress_orders:
        inprogress_orders[session_id] = {}

def complete_order(parameters: dict,session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding order. Sorry! Can you place a new order please?"
    else:
        order = inprogress_orders[session_id]
        if order == {}:
            fulfillment_text ="Your order is empty. Please Order again"
        else:
            order_id = save_to_db(order)

            if order_id == -1:
                fulfillment_text = "Sorry, I couldn't process your order due to a backend error." \
                                    + "\nPlease try again later or contact our customer service for assistance."
            else:
                order_total = db_helper.get_total_order_price(order_id)

                fulfillment_text = f"Awesome. Your order is placed. " \
                                f"Your order total is ${order_total}.\nOrder ID: {order_id}.\nYou can use this number to track your order."

            del inprogress_orders[session_id]                       

    response = { "fulfillmentText": fulfillment_text}
    return JsonResponse(response)


def save_to_db(order: dict):
    
    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(food_item,quantity,next_order_id)

        if rcode == -1:
            return -1
    
    db_helper.insert_order_tracking(next_order_id, "in progress" )

    return next_order_id

def add_to_order(parameters: dict,session_id: str):
    food_item = parameters['food-item']
    quantities = parameters['number']

    if len(food_item) != len(quantities):
        fulfillment_text = "Sorry, I didn't understand. Can you please specify food items and quantities"
    else:
        new_food_dict = dict(zip(food_item,quantities))

        if session_id in inprogress_orders:
            old_food_dict = inprogress_orders[session_id]
            old_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = old_food_dict
             
        else:
            inprogress_orders[session_id] = new_food_dict


        order_str = utils.get_str_from_food_dict(inprogress_orders[session_id])
        fulfillment_text = f"So far, you have {order_str}. Do you need anything else? "
        response = { "fulfillmentText": fulfillment_text}

        return JsonResponse(response)


def track_order(parameters:dict, session_id: str):
    order_id = int(parameters['order_id'])
    order_status = db_helper.get_order_status(order_id)

    if order_status:
        fulfillment_text = f"The order status for {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order_id: {order_id}"


    response = {
                "fulfillmentText": fulfillment_text
            }
            
    return JsonResponse(response)


def remove_from_order(parameters:dict, session_id: str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I'm having trouble finding your order. Sorry! Can you place a new order?"
        response = {"fulfillmentText": fulfillment_text}
        return JsonResponse(response)
    
    current_order = inprogress_orders[session_id]
    food_items = parameters["food-item"]

    removed_items = []
    no_such_items = []

    for item in food_items:
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items)> 0:
        fulfillment_text = f'Removed {", ".join(removed_items)} from your order'

    if len(no_such_items)> 0:
        fulfillment_text = f' Your current order does not have {", ".join(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"

    else:
        order_str =utils.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}. Do you need anything else?"
    
    response = {"fulfillmentText": fulfillment_text}

    return JsonResponse(response)