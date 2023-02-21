"""Admin related views
"""
import sqladmin

from fuelpricesgr import models


class DailyCountryAdmin(sqladmin.ModelView, model=models.DailyCountry):
    """The daily country admin.
    """
    name = "Daily Country Data"
    name_plural = "Daily Country Data"
    column_list = (models.DailyCountry.date, models.DailyCountry.fuel_type, models.DailyCountry.price)
    column_formatters = {models.DailyCountry.fuel_type: lambda m, _: m.fuel_type.description}
    column_searchable_list = (models.DailyCountry.date, )
    column_sortable_list = (models.DailyCountry.date, )
    column_default_sort = [(models.DailyCountry.date, True), (models.DailyCountry.fuel_type, False)]
    page_size = 100
    page_size_options = [100, 200, 500, 1000]


class DailyPrefectureAdmin(sqladmin.ModelView, model=models.DailyPrefecture):
    """The daily country admin.
    """
    name = "Daily Prefecture Data"
    name_plural = "Daily Prefecture Data"
    column_list = (
        models.DailyPrefecture.date, models.DailyPrefecture.prefecture, models.DailyPrefecture.fuel_type,
        models.DailyPrefecture.price
    )
    column_formatters = {
        models.DailyPrefecture.fuel_type: lambda m, _: m.fuel_type.description,
        models.DailyPrefecture.prefecture: lambda m, _: m.prefecture.description,
    }
    column_searchable_list = (models.DailyPrefecture.date,)
    column_sortable_list = (models.DailyPrefecture.date,)
    column_default_sort = [
        (models.DailyPrefecture.date, True), (models.DailyPrefecture.prefecture, False),
        (models.DailyPrefecture.fuel_type, False)
    ]
    page_size = 100
    page_size_options = [100, 200, 500, 1000]


class WeeklyCountryAdmin(sqladmin.ModelView, model=models.WeeklyCountry):
    """The daily country admin.
    """
    name = "Weekly Country Data"
    name_plural = "Weekly Country Data"
    column_list = (
        models.WeeklyCountry.date, models.WeeklyCountry.fuel_type, models.WeeklyCountry.lowest_price,
        models.WeeklyCountry.highest_price, models.WeeklyCountry.median_price
    )
    column_formatters = {models.WeeklyCountry.fuel_type: lambda m, _: m.fuel_type.description}
    column_searchable_list = (models.WeeklyCountry.date,)
    column_sortable_list = (models.WeeklyCountry.date,)
    column_default_sort = [(models.WeeklyCountry.date, True), (models.WeeklyCountry.fuel_type, False)]
    page_size = 100
    page_size_options = [100, 200, 500, 1000]


class WeeklyPrefectureAdmin(sqladmin.ModelView, model=models.WeeklyPrefecture):
    """The daily country admin.
    """
    name = "Weekly Prefecture Data"
    name_plural = "Weekly Prefecture Data"
    column_list = (
        models.WeeklyPrefecture.date, models.WeeklyPrefecture.fuel_type, models.WeeklyPrefecture.prefecture,
        models.WeeklyPrefecture.lowest_price, models.WeeklyPrefecture.highest_price,
        models.WeeklyPrefecture.median_price
    )
    column_formatters = {
        models.WeeklyPrefecture.fuel_type: lambda m, _: m.fuel_type.description,
        models.WeeklyPrefecture.prefecture: lambda m, _: m.prefecture.description,
    }
    column_searchable_list = (models.WeeklyPrefecture.date, )
    column_sortable_list = (models.WeeklyPrefecture.date, )
    column_default_sort = [
        (models.WeeklyPrefecture.date, True), (models.WeeklyPrefecture.prefecture, False),
        (models.WeeklyPrefecture.fuel_type, True)
    ]
    page_size = 100
    page_size_options = [100, 200, 500, 1000]
