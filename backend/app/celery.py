# import celeryconfig
# print (celeryconfig)
# from celery import Celery



    

    
# client = Celery(__name__,  broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# def make_celery(celery, app):

#     celery.conf.update(app.config)
#     celery.config_from_object(celeryconfig)

#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)

#     celery.Task = ContextTask
