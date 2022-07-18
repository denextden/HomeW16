from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from date import users, orders, offers
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    email = db.Column(db.String(20))
    role = db.Column(db.String(20))
    phone = db.Column(db.String(20))


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(20))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    address = db.Column(db.String(20))
    price = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class Offer(db.Model):
    __tablename__ = 'offers'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'))
    executor_id = db.Column(db.Integer, db.ForeignKey('orders.id'))


def main():
    db.create_all()
    insert_data()
    app.run(debug=True)


def insert_data():
    new_users = []
    for user in users:
        new_users.append(
            User(
                id=user['id'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                age=user['age'],
                email=user['email'],
                role=user['role'],
                phone=user['phone'],
            )
        )
        with db.session.begin():
            db.session.add_all(new_users)

    new_orders = []
    for order in orders:
        new_orders.append(
            Order(
                id=order['id'],
                name=order['name'],
                description=order['description'],
                start_date=datetime.strptime(order['start_date'], '%m/%d/%Y'),
                end_date=datetime.strptime(order['end_date'], '%m/%d/%Y'),
                address=order['address'],
                price=order['price'],
                customer_id=order['customer_id'],
                executor_id=order['executor_id']
            )
        )
        with db.session.begin():
            db.session.add_all(new_orders)

    new_offers = []
    for offer in offers:
        new_offers.append(
            Offer(
                id=offer['id'],
                order_id=offer['order_id'],
                executor_id=offer['executor_id'],
            )
        )
        with db.session.begin():
            db.session.add_all(new_offers)


@app.route('/users', methods=['GET', 'POST'])  # все пользователи
def get_all_users():
    if request.method == 'GET':
        results = []
        for user in User.query.all():
            results.append({
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'age': user.age,
                'email': user.email,
                'role': user.role,
                'phone': user.phone,
            })
        return jsonify(results)

    elif request.method == 'POST':
        result = request.get_json()
        new_offer = Offer(
            id=result['id'],
            first_name=result['first_name'],
            last_name=result['last_name'],
            age=result['age'],
            email=result['email'],
            role=result['role'],
            phone=result['phone']
        )
        with db.session.begin():
            db.session.add_all(new_offer)


@app.route('/users/<int:uid>', methods=['GET', 'PUT', 'DELETE'])  # один пользователь
def get_user_by_id(uid):
    if request.method == 'GET':
        user = User.query.get(uid)
        result = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'age': user.age,
            'email': user.email,
            'role': user.role,
            'phone': user.phone,
        }
        return jsonify(result)

    elif request.method == 'PUT':
        result = request.get_json()
        user = User.query.get(uid)
        user.id = result['id'],
        user.first_name = result['first_name'],
        user.last_name = result['last_name'],
        user.age = result['age'],
        user.email = result['email'],
        user.role = result['role'],
        user.phone = result['phone']

        # with db.session.begin():
        db.session.add(user)
        db.session.commit()

    elif request.method == 'DELETE':
        user = Order.query.get(uid)
        db.session.delete(user)
        db.session.commit()


@app.route('/orders', methods=['GET', 'POST'])
def get_all_orders():
    if request.method == 'GET':
        result = []
        for order in Order.query.all():
            customer = User.query.get(order.customer_id).first_name if User.query.get(
                order.customer_id) else order.customer_id
            executor = User.query.get(order.executor_id).first_name if User.query.get(
                order.executor_id) else order.executor_id
            result.append({
                'id': order.id,
                'name': order.name,
                'description': order.description,
                'start_date': order.start_date,
                'end_date': order.end_date,
                'address': order.address,
                'price': order.price,
                'customer_id': customer,
                'executor_id': executor,
            })
        return jsonify(result)

    elif request.method == 'POST':
        result = request.get_json()
        new_order = Order(
            id=result['id'],
            name=result['name'],
            description=result['description'],
            start_date=datetime.strptime(result['start_date'], '%m/%d/%Y'),
            end_date=datetime.strptime(result['end_date'], '%m/%d/%Y'),
            address=result['address'],
            price=result['price'],
            customer_id=result['customer_id'],
            executor_id=result['executor_id']
        )
        with db.session.begin():
            db.session.add_all(new_order)


@app.route('/orders/<int:oid>', methods=['GET', 'PUT', 'DELETE'])
def get_order_by_oid(oid):
    if request.method == 'GET':
        order = Order.query.get(oid)
        result = {
            'id': order.id,
            'name': order.name,
            'description': order.description,
            'start_date': order.start_date,
            'end_date': order.end_date,
            'address': order.address,
            'price': order.price,
            'customer_id': order.customer_id,
            'executor_id': order.executor_id,
        }
        return jsonify(result)

    elif request.method == 'PUT':
        result = request.get_json()
        order = Order.query.get(oid)
        order.name = result['name'],
        order.description = result['description'],
        order.start_date = datetime.strptime(result['start_date'], '%m/%d/%Y')
        order.end_date = datetime.strptime(result['end_date'], '%m/%d/%Y')
        order.address = result['address'],
        order.price = result['price'],
        order.customer_id = result['customer_id'],
        order.executor_id = result['executor_id']

        # with db.session.begin():
        db.session.add(order)
        db.session.commit()

    elif request.method == 'DELETE':
        order = Order.query.get(oid)
        db.session.delete(order)
        db.session.commit()


@app.route('/offers', methods=['GET', 'POST'])  # все офферы
def get_all_offers():
    if request.method == 'GET':
        result = []
        for offer in Offer.query.all():
            result.append({
                'id': offer.id,
                'order_id': offer.order_id,
                'executor_id': offer.executor_id,
            })
        return jsonify(result)

    elif request.method == 'POST':
        result = request.get_json()
        new_offer = Offer(
            id=result['id'],
            order_id=result['order_id'],
            executor_id=result['executor_id']
        )
        with db.session.begin():
            db.session.add_all(new_offer)


@app.route('/offers/<int:oid>', methods=['GET'])  # один пользователь
def get_offer_by_id(oid):
    if request.method == 'GET':
        offer = Offer.query.get(oid)
        result = {
            'id': offer.id,
            'order_id': offer.order_id,
            'executor_id': offer.executor_id,
        }
        return jsonify(result)

    elif request.method == 'PUT':
        result = request.get_json()
        offer = Offer.query.get(oid)
        offer.id = result['id'],
        offer.order_id = result['order_id'],
        offer.executor_id = result['executor_id']

        db.session.add(offer)
        db.session.commit()

    elif request.method == 'DELETE':
        offer = Offer.query.get(oid)
        db.session.delete(offer)
        db.session.commit()


if __name__ == '__main__':
    main()
