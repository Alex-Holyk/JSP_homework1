import eventlet
import socketio
import datetime

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

MILK = 'milk'
SUGAR = 'sugar'


ingredients = {
    MILK: 12,
    SUGAR: 13
}

drinks = [
    {'title': 'Latte', 'ingredients': {}},
    {'title': 'Capuccino', 'ingredients': {}}
]

orders = []


@sio.event
def connect(sid, environ):
    print('connect ', sid)


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.event
def get_history(sid):
    sio.emit('print_response', {"OK": 200, "data": orders})


@sio.event
def make_coffee(sid, data):
    if "options" not in data:
        data['options'] = []

    response = validate(data)

    if "Error" in response.keys():
        sio.emit('print_response', response)

    chosen_drink = drinks[int(data['drink']) - 1]

    for option in data['options']:
        if option in ingredients and ingredients[option] > 0:
            ingredients[option] -= 1
            print(option)
            chosen_drink['ingredients'][option] = True

    print(chosen_drink)
    orders.append({'drink': chosen_drink,
                   'ordered-at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')})

    sio.emit('print_response', response)


def validate(data):
    chosen_index = int(data['drink']) - 1
    if not isinstance(chosen_index, int):
        return {"Error": 400, "Description": "Bad request"}
    if chosen_index > len(drinks):
        return {"Error": 404, "Description": "There is no drink under chosen number"}
    else:
        for item in data['options']:
            if item not in ingredients.keys():
                return {"Error": 404, "Description": f"'{item}' not found in ingredients"}
            elif ingredients[item] == 0:
                return {"Error": 403, "Description": f"'{item}' is out of stock"}

    return {"OK": 200, "Description": "Success", "data": f'Your {drinks[chosen_index]["title"]} is gonna be ready in a minute'}


@sio.event
def get_drinks(sid):
    sio.emit('show_drinks', {"data": drinks})


@sio.event
def get_ingredients(sid):
    sio.emit('show_ingredients', {'data': ingredients})


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
