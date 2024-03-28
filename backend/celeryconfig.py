from celery.schedules import crontab

beat_schedule = {
    'monthly_report': {
        'task': 'app.tasks.send_monthly_report',
        # send on 1st of every month
        'schedule': crontab(0, 0, day_of_month=1),
    },
    'daily_reminder': {
        'task': 'app.tasks.send_daily_reminder',
        # run every 10 seconds
        'schedule': crontab(minute="*"),
    }
    
}