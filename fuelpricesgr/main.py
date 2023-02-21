"""The FastAPI main module
"""
import fastapi.middleware
import fastapi.middleware.cors
import sqladmin

from fuelpricesgr import database, settings, views

app = fastapi.FastAPI(
    title="Fuel Prices in Greece",
    description=
    """An API that returns data for fuel prices in Greece. Daily and weekly data about fuel prices are regularly
    uploaded at the [Παρατηρητήριο Τιμών Υγρών Καυσίμων](http://www.fuelprices.gr/) website by the Greek Government, but
    the data are published as PDF files. With this API you can get the data in a structured manner.""",
    contact={
        "name": "Kostas Kokkoros",
        "url": "https://www.mavroprovato.net",
        "email": "mavroprovato@gmail.com",
    },
    license_info={
        "name": "The MIT License (MIT)",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url=None,
    redoc_url='/docs',
    middleware=[
        fastapi.middleware.Middleware(
            fastapi.middleware.cors.CORSMiddleware,
            allow_origins=settings.CORS_ALLOW_ORIGINS,
            allow_methods=['GET'],
        )
    ]
)
app.include_router(views.api.router)

admin = sqladmin.Admin(app, database.engine)
admin.add_view(views.admin.DailyCountryAdmin)
admin.add_view(views.admin.DailyPrefectureAdmin)
admin.add_view(views.admin.WeeklyCountryAdmin)
admin.add_view(views.admin.WeeklyPrefectureAdmin)
