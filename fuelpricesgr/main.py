"""The FastAPI main module
"""
import atexit

import apscheduler.schedulers.background
import apscheduler.triggers.cron
import fastapi.middleware

from fuelpricesgr import settings, storage, tasks, views

# Initialize the storage
storage.init_storage()

# Create the application
app = fastapi.FastAPI(
    title="Fuel Prices in Greece",
    description="""
An API that returns data for fuel prices in Greece. Daily and weekly data about fuel prices are regularly uploaded at
the [Παρατηρητήριο Τιμών Υγρών Καυσίμων](http://www.fuelprices.gr/) website by the Greek Government, but the data are
published as PDF files. With this API you can get the data in a structured manner.
    """,
    contact={
        "name": "Kostas Kokkoros",
        "url": "https://www.mavroprovato.net",
        "email": "mavroprovato@gmail.com",
    },
    license_info={
        "name": "The MIT License (MIT)",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url='/docs'
)
app.include_router(views.api.router, prefix='/api')

# Add SQL admin if the backend is SQL Alchemy
if settings.STORAGE_BACKEND == 'fuelpricesgr.storage.sql_alchemy.SqlAlchemyStorage':
    import sqladmin
    import fuelpricesgr.storage.sql_alchemy
    import fuelpricesgr.views.admin

    admin = sqladmin.Admin(
        app, fuelpricesgr.storage.sql_alchemy.get_engine(),
        authentication_backend=fuelpricesgr.views.admin.AuthenticationBackend(secret_key=settings.SECRET_KEY)
    )
    admin.add_view(fuelpricesgr.views.admin.DailyCountryAdmin)
    admin.add_view(fuelpricesgr.views.admin.DailyPrefectureAdmin)
    admin.add_view(fuelpricesgr.views.admin.WeeklyCountryAdmin)
    admin.add_view(fuelpricesgr.views.admin.WeeklyPrefectureAdmin)
    admin.add_view(fuelpricesgr.views.admin.UserAdmin)

# Set up the task scheduler
scheduler = apscheduler.schedulers.background.BackgroundScheduler()
scheduler.add_job(tasks.import_data, apscheduler.triggers.cron.CronTrigger(hour="*/8"))
scheduler.start()


@atexit.register
def shutdown():
    """Graceful shutdown.
    """
    scheduler.shutdown()
