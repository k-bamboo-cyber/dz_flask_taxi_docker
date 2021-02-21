"""Приложение для заказа такси на Flask."""

from typing import Any

from flask import request, Flask, Response, json

from bd import Drivers, Clients, Orders

app = Flask(__name__)


def converter(ans: str) -> dict:
    """Конвертер строки response в словарь."""
    new_ans = ans.replace('[', "").replace(']', '').replace("'", '"')
    dict_ans = eval(new_ans)
    return dict_ans


@app.route('/drivers/<int:driver_id>')
def show_driver(driver_id: int) -> Any:
    """Поиск водителя."""
    try:
        driver = Drivers()
        ans = str(driver.select_driver(driver_id))
        if ans == '[]':
            return Response('Объект в базе не найден', status=404)
        return str(ans)
    except Exception:
        return Response('Неправильный запрос', status=400)


@app.route('/drivers', methods=['DELETE', 'POST'])
def del_or_add_driver() -> Response:
    """Удаление и добавление водителя в базу."""
    try:
        driver = Drivers()
        file = json.loads(request.data.decode('utf-8'))
    except Exception:
        return Response('Неправильный запрос', status=400)
    if request.method == 'POST':
        try:
            driver.insert_driver(file['name'], file['car'])
            print('Post', file['id'])
            return Response('created!', status=201)
        except Exception:
            return Response('Неправильный запрос', status=400)
    elif request.method == 'DELETE':
        try:
            print('Delete', file['id'])
            if str(driver.select_driver(file['id'])) == '[]':
                return Response('Объект в базе не найден ', status=404)
            driver.delete_driver(file['id'])
            return Response('Удалено', status=204)
        except Exception:
            return Response('Неправильный запрос', status=400)


@app.route('/clients/<int:client_id>')
def show_client(client_id: int) -> Any:
    """Поиск клиента в базе."""
    try:
        client = Clients()
        ans = str(client.select_client(client_id))
        if ans == '[]':
            return Response('Объект в базе не найден', status=404)
        return ans
    except Exception:
        return Response('Неправильный запрос', status=400)


@app.route('/clients', methods=['DELETE', 'POST'])
def client() -> Response:
    """Добавление/удаление клиента."""
    try:
        client = Clients()
        file = json.loads(request.data.decode('utf-8'))
    except Exception:
        return Response('Неправильный запрос', status=400)

    if request.method == 'POST':
        try:
            client.insert_client(file['name'], file['is_vip'])
            print('Post', file['id'])
            return Response('created!', status=201)
        except Exception:
            return Response('Неправильный запрос', status=400)
    elif request.method == 'DELETE':
        try:
            print('Delete', file['id'])
            if str(client.select_client(file['id'])) == '[]':
                return Response('Объект в базе не найден', status=404)
            client.delete_client(file['id'])
            return Response('Удалено', status=204)
        except Exception:
            return Response('Неправильный запрос', status=400)
    else:
        return Response('Неправильный запрос', status=400)


@app.route('/orders/<int:order_id>', methods=['GET', 'PUT', 'POST'])
def show_order(order_id: int) -> Any:
    """Изменение/поиск заказа."""
    try:
        order = Orders()
        ans = str(order.select_order(order_id))
    except Exception:
        return Response('Неправильный запрос', status=400)
    if request.method == 'GET':
        if ans == '[]':
            return Response('Объект в базе не найден', status=404)
        return str(ans)
    if request.method == 'PUT':
        file = json.loads(request.data.decode('utf-8'))
        if ans == '[]':
            return Response('Объект не найден в базе', status=404)
        print(converter(ans)['status'])
        if converter(ans)['status'] == 'not_accepted' and file['status'] in ['in_progress', 'cancelled']:
            order.update_order_not_accepted(order_id,
                                            file['status'],
                                            file['date_created'],
                                            file['driver_id'],
                                            file['client_id'])
            return Response('Изменено', status=200)
        if converter(ans)['status'] == 'in_progress' and file['status'] in ['done', 'cancelled']:
            order.update_order_in_progress(order_id, file['status'])
            return Response('Изменено!', status=200)
        return Response("Неправильный запрос", status=400)


@app.route('/orders', methods=['POST'])
def order() -> Response:
    """Добавление заказа."""
    try:
        order = Orders()
        file = json.loads(request.data.decode('utf-8'))
    except Exception:
        return Response('Неправильный запрос', status=400)
    if request.method == 'POST':
        try:
            order.insert_order(file['address_from'], file['address_to'],
                               file['client_id'], file['driver_id'],
                               file['date_created'], file['status'])
            return Response('created!', status=201)
        except Exception:
            return Response('Плохой json', status=400)
    else:
        return Response('Неправильный запрос', status=400)


if __name__ == '__main__':
    app.run()
