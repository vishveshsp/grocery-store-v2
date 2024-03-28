from datetime import datetime
from flask import render_template
from app.models import Credentials, User, Order
from mail.app import send_email, send_email_1
from app.celery import client
from io import BytesIO
import matplotlib.pyplot as plt
from collections import defaultdict
import ast




import celeryconfig
print (celeryconfig)
from celery import Celery



    

    
client = Celery(__name__,  broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

def make_celery(celery, app):

    celery.conf.update(app.config)
    celery.config_from_object(celeryconfig)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask






@client.task()
def send_welcome_email(username, email_id):
    message = render_template('welcome.html', username=username)
    send_email(email_id, 'Welcome to Grocesory App!', message)

@client.task()
def send_daily_reminder():
    #app = app.create_app()  # Create a Flask app instan

    creds = Credentials.query.all()
    today = datetime.utcnow().date()
    for cred in creds[1:]:
            # if cred.last_login.date() == today:
            #     pass
            # else:
        user = User.query.filter_by(user_id = cred.user_id).first()
        username = f'{user.first_name} {user.last_name}'
        message = render_template('Daily_remiender.html', username=username)
        send_email(cred.email_id, 'Daily Reminder!', message)
        #app.app_context().push()


@client.task()
def send_monthly_reports():
    users = Credentials.query.all()

    for user in users:
        orders = Order.query.filter_by(user_id=user.user_id).all()

        if orders:
            # Prepare data for the report
            monthly_total = 0
            category_totals = defaultdict(float)

            for order in orders:
                monthly_total += order.total_price
                items_data = ast.literal_eval(order.items_data)

                for item in items_data:
                    category_totals[item['category_id']] += item['price']

            # Generate a bar graph for categorical money distribution
            categories = list(category_totals.keys())
            values = list(category_totals.values())

            plt.bar(categories, values)
            plt.xlabel('Categories')
            plt.ylabel('Money Distribution')
            plt.title('Categorical Money Distribution')

            # Save the plot to a BytesIO object
            graph_io = BytesIO()
            plt.savefig(graph_io, format='png')
            graph_io.seek(0)
            plt.close()

            # Generate the report content
            report_content = f"Monthly Total: {monthly_total}\n"
            report_content += f"Order Date | Total | Month's Total\n"
            for order in orders:
                report_content += f"{order.order_date} | {order.total_price} | {monthly_total}\n"

            # Send the email with the report and graph to the user's email
            send_email_1(user.email_id, report_content, graph_io)






