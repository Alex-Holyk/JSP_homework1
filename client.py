import socketio

sio = socketio.Client()


@sio.event
def connect():
    print('connection established')


@sio.event
def disconnect():
    print('disconnected from server')


@sio.event
def connect_error():
    print('the connection failed')


def show_menu(drinks):
    menu_string = 'Select a drink:'

    for index, value in enumerate(drinks):
        menu_string += f'\n{index + 1}. {value["title"]}'
    print(menu_string)


@sio.event
def show_drinks(response):
    show_menu(response['data'])


@sio.event
def show_ingredients(response):
    ingredients = response['data']
    response_string = '\nThere are '
    for item in ingredients:
        response_string += f'{item} x{ingredients[item]} '
    response_string += 'are left.'
    print(response_string)


@sio.event
def print_response(response):
    if 'data' in response.keys():
        print(response['data'])
        return

    print(response)


def get_ingredients():
    with_sugar = input('Sugar? (y/N)').lower()
    with_milk = input('Milk? (y/N)').lower()

    ingredients = []
    if (with_sugar == 'y'):
        ingredients.append('sugar')
    if (with_milk == 'y'):
        ingredients.append('milk')

    return ingredients


def main_loop():
    ingredients = []
    while True:
        print('q - disconnect, h - history')
        sio.emit('get_ingredients')
        sio.emit('get_drinks')
        user_input = input().lower()
        if user_input == 'q':
            sio.disconnect()
            print('disconnected')
            return
        elif user_input == 'h':
            sio.emit('get_history')
        else:
            ingredients = get_ingredients()
            sio.emit('make_coffee', {
                'drink': user_input, 'options': ingredients})


sio.connect('http://localhost:5000')
main_loop()
sio.wait()
