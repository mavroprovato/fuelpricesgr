"""Admin related views
"""
import sqladmin

from fuelpricesgr import models


class DailyCountryAdmin(sqladmin.ModelView, model=models.DailyCountry):
    """The daily country admin.
    """
    column_list = (models.DailyCountry.date, models.DailyCountry.fuel_type, models.DailyCountry.price)


class DailyPrefectureAdmin(sqladmin.ModelView, model=models.DailyPrefecture):
    """The daily country admin.
    """
    column_list = (
        models.DailyPrefecture.date, models.DailyPrefecture.fuel_type, models.DailyPrefecture.fuel_type,
        models.DailyPrefecture.price
    )


class WeeklyCountryAdmin(sqladmin.ModelView, model=models.WeeklyCountry):
    """The daily country admin.
    """
    column_list = (
        models.WeeklyCountry.date, models.WeeklyCountry.fuel_type, models.WeeklyCountry.lowest_price,
        models.WeeklyCountry.highest_price, models.WeeklyCountry.median_price
    )


class WeeklyPrefectureAdmin(sqladmin.ModelView, model=models.WeeklyPrefecture):
    """The daily country admin.
    """
    column_list = (
        models.WeeklyPrefecture.date, models.WeeklyPrefecture.fuel_type, models.WeeklyPrefecture.prefecture,
        models.WeeklyPrefecture.lowest_price, models.WeeklyPrefecture.highest_price,
        models.WeeklyPrefecture.median_price
    )

