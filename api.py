from flask import make_response, url_for, Flask, jsonify, redirect, request
from flask_login import login_required, login_user, logout_user, current_user

from flask_restful import reqparse, abort, Api, Resource
import werkzeug

from data.db_session import get_session
from flask_socketio import SocketIO

from operations import abort_if_restaurant, abort_if_user

from data.models.menus import Menu
from data.models.users import User
from data.models.profile_types import ProfileType
from data.models.menu_items import MenuItem
from data.models.restaurants import Restaurant
from data.models.categories import Category
from data.models.orders import Order
from data.models.order_items import OrderItem
from data.models.restaurant_places import RestaurantPlace

app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
print(f' * SECRET_KEY: {os.environ.get("SECRET_KEY")}')
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['SQLALCHEMY_POOL_SIZE'] = 20

socketio = SocketIO(app)


# Images
@app.route('/menu_item_image/<int:menu_item_id>')
def menu_item_image(menu_item_id):
    image_binary = get_session().query(MenuItem).get(menu_item_id).item_image
    if not image_binary:
        return redirect('/static/no_image/item.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


@app.route('/restaurant_image/<int:restaurant_id>')
def restaurant_image(restaurant_id):
    image_binary = get_session().query(Restaurant).get(restaurant_id).profile_image
    if not image_binary:
        return redirect('/static/no_image/profile.png')
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/jpeg')
    return response


# Menu
class MenuItemListResource(Resource):
    def get(self, restaurant_id):
        restaurant = get_session().query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        response = jsonify({'categories': [category.to_dict(only=('id', 'title', 'menu_items.id', 'menu_items.title', 'menu_items.price')) for category in restaurant.menu.categories], 'restaurant': restaurant.to_dict(only=('id', 'title'))})
        return response

    @login_required
    def post(self, restaurant_id):
        abort_if_user()
        parser = reqparse.RequestParser()
        parser.add_argument('item_image', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('title', required=True, type=str, location='values')
        parser.add_argument('price', required=True, type=int, location='values')
        parser.add_argument('category', required=True, type=str, location='values')
        args = parser.parse_args()

        # Check to errors
        if restaurant_id != current_user.id:
            abort(404)
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == restaurant_id, current_user.id == restaurant_id).first()
        if not restaurant:
            abort(404)

        nice = True
        errors = []
        if get_session().query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.title == args['title']).first():
            errors.append({'error': 'Продукт с таким именем уже существует', 'error_field': 'title'})
            nice = False
        if not get_session().query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first():
            errors.append({'error': 'Такой категории не существует', 'error_field': 'category'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response

        menu = get_session().query(Menu).get(current_user.menu_id)
        menu_item = MenuItem(
            title=args['title'],
            price=args['price'],
            category=get_session().query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first(),
            menu=menu
        )
        menu.items.append(menu_item)
        get_session().commit()
        if args['item_image']:
            f = args['item_image']
            menu_item.item_image = f.read()
        get_session().commit()
        return jsonify({'successfully': True})


class MenuItemResource(Resource):
    def get(self, restaurant_id, menu_item_id):
        restaurant = get_session().query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        menu_item = get_session().query(MenuItem).filter(MenuItem.menu == restaurant.menu, MenuItem.id == menu_item_id).first()
        if not menu_item:
            abort(404)
        response = jsonify(**menu_item.to_dict(only=('title', 'price', 'category.title')), **{'item_image_url': f'/menu_item_image/{menu_item_id}'})
        return response

    @login_required
    def put(self, restaurant_id, menu_item_id):
        abort_if_user()
        parser = reqparse.RequestParser()
        parser.add_argument('item_image', type=werkzeug.datastructures.FileStorage, location='files')
        parser.add_argument('title', required=True, type=str, location='values')
        parser.add_argument('price', required=True, type=int, location='values')
        parser.add_argument('category', required=True, type=str, location='values')
        args = parser.parse_args()

        if restaurant_id != current_user.id:
            abort(404)
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == restaurant_id, current_user.id == restaurant_id).first()
        if not restaurant:
            abort(404)
        menu_item = get_session().query(MenuItem).filter(MenuItem.menu == restaurant.menu, MenuItem.id == menu_item_id).first()
        if not menu_item:
            abort(404)

        nice = True
        errors = []
        if get_session().query(MenuItem).filter(MenuItem.menu == current_user.menu, MenuItem.title == args['title'], MenuItem.id != menu_item_id).first():
            errors.append({'error': 'Продукт с таким названием уже существует', 'error_field': 'title'})
            nice = False
        if not get_session().query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first():
            errors.append({'error': 'Такой категории не существует', 'error_field': 'category'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response

        menu_item.title = args['title']
        menu_item.price = args['price']
        menu_item.category = get_session().query(Category).filter(Category.menu == current_user.menu, Category.title == args['category']).first()
        if args['item_image']:
            f = request.files['item_image']
            menu_item.item_image = f.read()
        get_session().commit()
        return jsonify({'successfully': True})

    @login_required
    def delete(self, restaurant_id, menu_item_id):
        abort_if_user()
        if restaurant_id != current_user.id:
            abort(404)
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == restaurant_id, current_user.id == restaurant_id).first()
        if not restaurant:
            abort(404)
        menu_item = get_session().query(MenuItem).filter(MenuItem.menu == restaurant.menu, MenuItem.id == menu_item_id).first()
        if not menu_item:
            abort(404)
        get_session().query(MenuItem).filter(MenuItem.id == menu_item_id).delete()
        get_session().commit()
        return jsonify({'successfully': True})


class MenuCategoryListResource(Resource):
    def get(self, restaurant_id):
        restaurant = get_session().query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        response = jsonify({'categories': [category.to_dict(only=('id', 'title', 'menu_items.id', 'menu_items.title', 'menu_items.price')) for category in restaurant.menu.categories], 'restaurant': restaurant.to_dict(only=('id', 'title'))})
        return response

    @login_required
    def post(self, restaurant_id):
        abort_if_user()
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, type=str, location='values')
        args = parser.parse_args()

        if restaurant_id != current_user.id:
            abort(404)
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == restaurant_id, current_user.id == restaurant_id).first()
        if not restaurant:
            abort(404)

        nice = True
        errors = []
        if get_session().query(Category).filter(Category.menu == current_user.menu, Category.title == args['title']).first():
            errors.append({'error': 'Категория с таким названием уже существует', 'error_field': 'title'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response

        menu = get_session().query(Menu).get(current_user.menu_id)
        category = Category(
            title=args['title']
        )
        menu.categories.append(category)
        get_session().commit()
        return jsonify({'successfully': True})


class MenuCategoryResource(Resource):
    def get(self, restaurant_id, category_id):
        restaurant = get_session().query(Restaurant).get(restaurant_id)
        if not restaurant:
            abort(404)
        category = get_session().query(Category).filter(Category.menu == restaurant.menu, Category.id == category_id).first()
        if not category:
            abort(404)
        response = jsonify(category.to_dict(only=('title',)))
        return response

    @login_required
    def put(self, restaurant_id, category_id):
        abort_if_user()
        parser = reqparse.RequestParser()
        parser.add_argument('title', required=True, type=str, location='values')
        args = parser.parse_args()

        if restaurant_id != current_user.id:
            abort(404)
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == restaurant_id, current_user.id == restaurant_id).first()
        if not restaurant:
            abort(404)
        category = get_session().query(Category).filter(Category.id == category_id).first()
        if not category:
            abort(404)

        nice = True
        errors = []
        if get_session().query(Category).filter(Category.menu == current_user.menu, Category.title == args['title'], Category.id != category_id).first():
            errors.append({'error': 'Категория с таким названием уже существует', 'error_field': 'title'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response

        category.title = args['title']
        get_session().commit()
        return jsonify({'successfully': True})

    @login_required
    def delete(self, restaurant_id, category_id):
        abort_if_user()
        if restaurant_id != current_user.id:
            abort(404)
        restaurant = get_session().query(Restaurant).filter(Restaurant.id == restaurant_id, current_user.id == restaurant_id).first()
        if not restaurant:
            abort(404)
        category = get_session().query(Category).filter(Category.id == category_id).first()
        if not category:
            abort(404)

        nice = True
        errors = []
        if category.menu_items:
            errors.append({'error': 'В категории остались продукты', 'error_field': 'menu'})
            nice = False
        if not nice:
            response = jsonify({'successfully': False, 'errors': errors})
            return response

        get_session().query(Category).filter(Category.id == category_id).delete()
        get_session().commit()
        return jsonify({'successfully': True})


api.add_resource(MenuItemListResource, '/api/menu/<int:restaurant_id>')
api.add_resource(MenuItemResource, '/api/menu/<int:restaurant_id>/item/<int:menu_item_id>')
api.add_resource(MenuCategoryListResource, '/api/menu/<int:restaurant_id>/categories')
api.add_resource(MenuCategoryResource, '/api/menu/<int:restaurant_id>/category/<int:category_id>')


# Order
def update_order_price(order_id):
    order = get_session().query(Order).get(order_id)
    order.price = sum([item.menu_item.price * item.count for item in order.order_items])
    get_session().commit()


class OrderListResource(Resource):
    @login_required
    def get(self, order_id):
        order = get_session().query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404)
        if current_user.__class__ == 'User':
            if order.user_id != current_user.id:
                abort(404)
        if current_user.__class__ == 'Restaurant':
            if order.restaurant_id == current_user.id:
                abort(404)
        return jsonify(order.to_dict(only=('id', 'price', 'state', 'restaurant.id', 'restaurant.menu.id', 'restaurant.places.id', 'restaurant.places.title', 'user.id', 'user.name', 'order_items.id', 'order_items.count', 'order_items.menu_item.title', 'order_items.menu_item.price', 'restaurant_place_id')))

    @login_required
    def post(self, order_id):  # For change state of order
        parser = reqparse.RequestParser()
        parser.add_argument('new_state', required=True, type=str, location='values')
        args = parser.parse_args()

        if current_user.__class__.__name__ == 'User':
            order = get_session().query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
            allowed_state = ['Awaiting payment']
        if current_user.__class__.__name__ == 'Restaurant':
            order = get_session().query(Order).filter(Order.id == order_id, Order.restaurant_id == current_user.id).first()
            allowed_state = ['In progress', 'Ready']

        if not order:
            abort(404)
        if args['state'] not in allowed_state:
            abort(403)

        if order.state == 'Is not sent' and args['new_state'] == 'Awaiting payment':
            socketio.emit('order_add', {'order_id': order_id}, to=order.restaurant_place_id)
        else:
            socketio.emit('order_change', {'order_id': order_id}, to=order.restaurant_place_id)

        order.state = args.state
        get_session().commit()
        return jsonify({'successfully': True})

    @login_required
    def put(self, order_id):  # For change data
        abort_if_restaurant()
        parser = reqparse.RequestParser()
        parser.add_argument('restaurant_place_id', required=True, type=int, location='values')
        args = parser.parse_args()

        order = get_session().query(Order).filter(Order.id == order_id).first()
        if not order:
            abort(404)
        if order.user_id != current_user.id:
            abort(404)
        restaurant_place = get_session().query(RestaurantPlace).filter(RestaurantPlace.id == args['restaurant_place_id'], RestaurantPlace.restaurant_id == order.restaurant_id).first()
        if not restaurant_place:
            abort(404)
        order.restaurant_place_id = restaurant_place.id
        get_session().commit()
        return jsonify({'successfully': True})


class OrderItemResource(Resource):
    @login_required
    def put(self, order_id, order_item_id):  # Put for user
        abort_if_restaurant()
        parser = reqparse.RequestParser()
        parser.add_argument('count', required=True, type=int, location='values')
        args = parser.parse_args()

        order = get_session().query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
        if not order:
            abort(404)
        order_item = get_session().query(OrderItem).filter(OrderItem.id == order_item_id, OrderItem.order_id == order.id).first()
        if not order_item:
            abort(404)
        order_item.count = args['count']
        get_session().commit()
        update_order_price(order_id)
        return jsonify({'successfully': True})

    def delete(self, order_id, order_item_id):
        abort_if_restaurant()
        order = get_session().query(Order).filter(Order.id == order_id, Order.user_id == current_user.id).first()
        if not order:
            abort(404)
        order_item = get_session().query(OrderItem).filter(OrderItem.id == order_item_id, OrderItem.order_id == order.id).delete()
        get_session().commit()
        update_order_price(order_id)
        return jsonify({'successfully': True})


api.add_resource(OrderListResource, '/api/order/<int:order_id>')
api.add_resource(OrderItemResource, '/api/order/<int:order_id>/<int:order_item_id>')
