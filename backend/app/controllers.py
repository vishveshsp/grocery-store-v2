from flask_restful import marshal
from flask import request, current_app as app, make_response, jsonify
from app.cache import cache
from datetime import datetime, timedelta
from app.models import Credentials, User, Trackers, Logs, db, token_required, Item, Order, Category, Approval
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import desc
from app.extra import *
from app.resources import *
import jwt
from app.tasks import send_welcome_email,send_daily_reminder,send_monthly_reports
from sqlalchemy.exc import IntegrityError

#send_welcome_email('hello',"vishvsh@gmail.com")

#send_monthly_reports()
 

@app.template_filter()
def format_time(time):
    return datetime.strftime(time, format)


@app.template_filter()
def format_time_code(time):
    return datetime.strftime(time, code_time)


@app.route('/ping', methods=['GET'])
def ping():
    send_monthly_reports.delay()
    return jsonify({'msg': 'Pong!'})



def create_owner_if_not_present(db):
    try:
        # Check if the owner with email admin@store exists
        owner = db.session.query(Credentials).filter_by(email_id='admin@store').first()

        if owner is None:
            # Owner not found, create a new owner
            from hashlib import sha256
            from jwt import encode

            # Hashing the password using the SECRET_KEY
            SECRET_KEY = 'your_secret_key_here'  # Replace with your actual secret key
            password = '1234'
            hashed_password = generate_password_hash(password, method='sha256')
            # Creating the owner record
            new_owner = Credentials(
                email_id='admin@store',
                password=hashed_password,
                last_login=datetime.now(),
                user_id=0,  # Replace with the appropriate user_id
                is_admin=None,
                request=None,
                owner='True'
            )

            # Add the new owner to the session and commit to the database
            db.session.add(new_owner)
            db.session.commit()
            print("Owner 'admin@store' created successfully.")

    except IntegrityError as e:
        db.session.rollback()
        print(f"IntegrityError: {str(e)}")
        

create_owner_if_not_present(db)


@app.route('/login', methods=['POST'])
def login():
    cache.clear()
    data = request.get_json()
    email_id = data['email_id']
    password = data['password']
    
    if bool(login_re(email_id)) or bool(password_re(password)):
        return make_response(jsonify({"message": 'Please use only a-z A-Z 0-9 or $'}), 203)
    
    check_cred = Credentials.query.filter_by(email_id=email_id).first()
    
    if check_cred:
        if check_password_hash(check_cred.password, password):
            check_cred.last_login = datetime.utcnow()
            db.session.commit()
            token = jwt.encode({
                'user_id': check_cred.user_id,
                'exp': datetime.utcnow() + timedelta(hours=1)
            }, app.config['SECRET_KEY'], 'HS256')
            token = token.decode('utf-8')
            is_admin = check_cred.is_admin
            is_owner = check_cred.owner
            return make_response(jsonify({
                "message": 'Logged In!',
                "token": token,
                "is_admin": is_admin,
                "is_owner": is_owner,
            }), 201)
        else:
            return make_response(jsonify({"message": 'Wrong Password!'}), 203)
    else:
        return make_response(jsonify({"message": 'User Does Not Exist!'}), 203)


@app.route('/validate_owner_token', methods=['POST'])
def validate_owner_token():
    token = request.get_json().get('token')  # Assuming the token is sent in the request body
    
    # Check if the token exists and is valid for an owner
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        # Fetch user details from the database to determine the owner status
        user = Credentials.query.filter_by(user_id=user_id).first()
        
        if user and user.owner:
            return jsonify({"is_owner": True}), 200
        else:
            return jsonify({"is_owner": False}), 403  # Forbidden if the user is not an owner
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401

@app.route('/validate_manager', methods=['POST'])
def validate_manager_token():
    token = request.get_json().get('token')  # Assuming the token is sent in the request body
    
    # Check if the token exists and is valid for an owner
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    
    try:
        decoded_token = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        user_id = decoded_token.get('user_id')
        # Fetch user details from the database to determine the owner status
        user = Credentials.query.filter_by(user_id=user_id).first()
        
        if user and user.is_admin:
            return jsonify({"is_admin": True}), 200
        else:
            return jsonify({"is_admin": False}), 403  # Forbidden if the user is not an owner
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token"}), 401
    

@app.route('/signup', methods=['POST'])
def signup():
    cache.clear()
    data = request.get_json()
    first_name = data['first_name']
    last_name = data['last_name']
    if not first_name.isalpha() or not last_name.isalpha():
        return make_response(jsonify({"message": 'Please use only alphabets for names!'}), 203)
    email_id = data['email_id']
    password = data['password']
    is_store_manager = data.get('is_store_manager', False)  # Fetch the value of is_store_manager
    if bool(login_re(email_id)) or bool(password_re(password)):
        return make_response(jsonify({"message": 'Please use only a-z A-Z 0-9 or $'}), 203)
    check_cred = Credentials.query.filter_by(email_id=email_id).first()
    if check_cred:
        return make_response(jsonify({"message": 'User with that login already exists!'}), 203)
    else:
        new_user = User(first_name=first_name,
                        last_name=last_name) 
        db.session.add(new_user)
        db.session.commit()
        if is_store_manager!=1:
            is_store_manager=None

        new_cred = Credentials(email_id=email_id, password=generate_password_hash(
            password, method='sha256'), last_login=datetime.utcnow(), user_id=new_user.user_id,request=is_store_manager)
        db.session.add(new_cred)
        db.session.commit()
        send_welcome_email(f'{first_name} {last_name}', email_id)
        return make_response(jsonify({"message": "Signed up successfully"}), 201)

@app.route("/owner/dashboard", methods=["GET"])
@token_required
@cache.memoize()
def dashboard(user_id):
    added_trackers = Trackers.query.filter_by(user_id=user_id).all()
    tracks = []
    for tracker in added_trackers:
        last_log = Logs.query.filter_by(
            track_id=tracker.track_id).order_by(desc(Logs.time)).first()
        if last_log:
            tracks.append({
                'track_id': tracker.track_id,
                'track_name': tracker.track_name,
                'time': last_log.time,
                'last_log': last_log.info, })
        else:
            tracks.append({
                'track_id': tracker.track_id,
                'track_name': tracker.track_name,
                'time': None,
                'last_log': 'No Log', })
    tracks = [marshal(track, tracker_with_log_resource_fields)
              for track in tracks]
    return jsonify(tracks)



@app.route('/user/items',methods=["GET"])
@token_required
def get_items(hello):
    
    items = Item.query.all()
    item_list = [{
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'category_id': item.category_id,
        'stock_left': item.stock_left,
        'expiration_date': item.expiration_date,
        'image_url': item.image_url,


    } for item in items]
    return jsonify(item_list)

@app.route('/item/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    categories_list = [{'id': category.id, 'name': category.name} for category in categories]
    return jsonify(categories_list)

@app.route('/user/commit_cart', methods=['POST'])
@token_required
def commit_cart(user_id):
    current_date_time = datetime.now()
    data = request.json  
    cart = data.get('cart')

    # Calculate total price of the order
    total_price = sum(item['price'] * item['quantity'] for item in cart)

    # Update the stock available for each item in the cart
    for item in cart:
        item_id = item['id']
        quantity = item['quantity']
        db_item = Item.query.get(item_id)
        if db_item:
            if db_item.stock_left >= quantity:
                db_item.stock_left -= quantity
            else:
                return jsonify({'message': f'Not enough stock available for item: {db_item.name}'}), 400
        else:
            return jsonify({'message': f'Item with ID {item_id} not found'}), 404

    # Create an order and save it to the database
    order = Order(user_id=user_id, items_data=str(cart), total_price=total_price)
    db.session.add(order)
    db.session.commit()

    return jsonify({'message': 'Order committed successfully'}), 200

@app.route('/admin/modify', methods=['GET'])
#@token_required
def get_items_mod():
    items = Item.query.all()
    item_list = [{
        'id': item.id,
        'name': item.name,
        'price': item.price,
        'category_id': item.category_id,
        'stock_left': item.stock_left,
        'expiration_date': item.expiration_date,
        'image_url': item.image_url,

    } for item in items]
    return jsonify(item_list)


@app.route('/admin/updateitems', methods=['POST'])
def post():
    # Access the data sent in the POST request
    data = request.get_json()

    # Extract the item ID and edited data from the payload
    item_id = data.get('itemId')
    edited_item_data = data.get('editedItemData')

    # Find the item by ID
    item = Item.query.get(item_id)

    if item:
        # Update item attributes with the edited data
        for key, value in edited_item_data.items():
            setattr(item, key, value)
        # Commit changes to the database
        db.session.commit()
        return {"message": "Item updated successfully"}, 200
    else:
        # If item ID is not found or null, create a new item
        new_item = Item(**edited_item_data)  # Assuming Item is a SQLAlchemy model
        db.session.add(new_item)
        db.session.commit()
        return {"message": "New item created successfully"}, 201

@app.route('/admin/deleteitem', methods=['DELETE'])
def delete_item():
    # Access the data sent in the DELETE request
    data = request.get_json()

    # Extract the item ID from the payload
    item_id = data.get('itemId')

    # Find the item by ID and delete it
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
        return {"message": "Item deleted successfully"}, 200
    else:
        return {"message": "Item not found"}, 404

@app.route('/admin/create_category', methods=['POST'])
def request_category():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({'message': 'Category name is required'}), 400

    new_category = Approval(name=name)

    try:
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Category created successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create category', 'error': str(e)}), 500
    finally:
        db.session.close()





@app.route('/owner/delete_category', methods=['DELETE'])
def delete_category():
    data = request.get_json()
    category_id = data.get('categoryId')

    if category_id is None:
        return jsonify({'error': 'Category ID is missing'}), 400

    category = Category.query.get(category_id)
    if category is None:
        return jsonify({'error': 'Category not found'}), 404

    # Delete associated items before deleting the category
    items = Item.query.filter_by(category_id=category_id).all()
    for item in items:
        db.session.delete(item)

    db.session.delete(category)
    db.session.commit()

    return jsonify({'message': 'Category and associated items deleted successfully'}), 200


@app.route('/get_credentials', methods=['GET'])
def get_credentials():
    credentials = Credentials.query.all()
    credentials_list = []
    for cred in credentials:
        credentials_list.append({
            'email_id': cred.email_id,
            'last_login': cred.last_login,
            'is_admin': cred.is_admin,
            'request': cred.request
        })
    return jsonify(credentials_list)

@app.route('/fetch_orders', methods=['GET'])
def fetch_orders():

    user_id = 1  


    user = User.query.filter_by(user_id=user_id).first()
    if user:


        orders = Order.query.filter_by(user_id=user.user_id).all()

        # Prepare orders data to send as JSON response
        orders_data = []
        for order in orders:
            orders_data.append({
                'order_id': order.order_id,
                'order_date': order.order_date.strftime('%Y-%m-%d'),  # Example format, adjust as needed
                'total': order.total_price,  # Assuming product name field in Order model
                # Add more fields as needed
            })

        return jsonify(orders_data), 200
    else:
        return jsonify({'message': 'User not found'}), 404
    
@app.route('/approve_user', methods=['POST'])
def approve_user():
    if request.method == 'POST':
        email = request.json.get('email') if request.json else None  # Get email from JSON if available
        if email:
            user = Credentials.query.filter_by(email_id=email).first()

            if user:
                user.is_admin = True  # Update is_admin to True for the user
                user.request=None
                db.session.commit()
                
                return jsonify({'message': 'User approved successfully!'})
            else:
                return jsonify({'error': 'User not found.'}), 404
        else:
            return jsonify({'error': 'Email not provided in the request.'}), 400


@app.route('/approvals', methods=['GET'])
def get_approvals():
    try:
        all_approvals = Approval.query.all()
        # Convert the SQLAlchemy objects to a list of dictionaries
        approvals_list = [{'id': approval.id, 'name': approval.name} for approval in all_approvals]
        return jsonify(approvals_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/approve_request', methods=['POST'])
def approve_category_request():
    data = request.get_json()
    print(data)
    category_name = data.get('requestId')

    if category_name:
        # Assuming your Approvals model has an id field for requests
        request_to_approve = Approval.query.filter_by(name=category_name).first()
        print(request_to_approve)
        if request_to_approve:
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.delete(request_to_approve)  # Delete the approved request
            db.session.commit()
            return jsonify({"message": f"Category '{category_name}' approved and added successfully."}), 200
        else:
            return jsonify({"message": "Request not found."}), 404
    else:
        return jsonify({"message": "Request ID or Category name not provided."}), 400


@app.route('/decline_request', methods=['POST'])
def decline_category_request():
    data = request.get_json()
    print(data)
    category_name = data.get('requestId')

    if category_name:
        # Assuming your Approvals model has an id field for requests
        request_to_approve = Approval.query.filter_by(name=category_name).first()
        print(request_to_approve)
        if request_to_approve:
            db.session.delete(request_to_approve)  # Delete the approved request
            db.session.commit()
            return jsonify({"message": f"Category '{category_name}' approved and added successfully."}), 200
        else:
            return jsonify({"message": "Request not found."}), 404
    else:
        return jsonify({"message": "Request ID or Category name not provided."}), 400







