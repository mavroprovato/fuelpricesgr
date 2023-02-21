"""Admin related views
"""
import sqladmin
import sqlalchemy
import sqlalchemy.orm

from fuelpricesgr import models


class BaseAdmin(sqladmin.ModelView):
    """Base admin class.
    """
    page_size = 100
    page_size_options = [100, 200, 500, 1000]

    def get_list_columns(self) -> list[tuple[str, sqlalchemy.orm.ColumnProperty]]:
        """Return the list columns. All columns are returned, except for the ID.

        :return: The list columns.
        """
        return [(attr.key, attr) for attr in sqlalchemy.inspect(self.model).attrs if attr.key != 'id']


class DailyCountryAdmin(BaseAdmin, model=models.DailyCountry):
    """The daily country admin.
    """
    name = "Daily Country Data"
    name_plural = "Daily Country Data"
    column_formatters = {models.DailyCountry.fuel_type: lambda m, _: m.fuel_type.description}
    column_searchable_list = (models.DailyCountry.date, )
    column_sortable_list = (models.DailyCountry.date, )
    column_default_sort = [(models.DailyCountry.date, True), (models.DailyCountry.fuel_type, False)]


class DailyPrefectureAdmin(BaseAdmin, model=models.DailyPrefecture):
    """The daily country admin.
    """
    name = "Daily Prefecture Data"
    name_plural = "Daily Prefecture Data"
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


class WeeklyCountryAdmin(BaseAdmin, model=models.WeeklyCountry):
    """The daily country admin.
    """
    name = "Weekly Country Data"
    name_plural = "Weekly Country Data"
    column_formatters = {models.WeeklyCountry.fuel_type: lambda m, _: m.fuel_type.description}
    column_searchable_list = (models.WeeklyCountry.date,)
    column_sortable_list = (models.WeeklyCountry.date,)
    column_default_sort = [(models.WeeklyCountry.date, True), (models.WeeklyCountry.fuel_type, False)]


class WeeklyPrefectureAdmin(BaseAdmin, model=models.WeeklyPrefecture):
    """The daily country admin.
    """
    name = "Weekly Prefecture Data"
    name_plural = "Weekly Prefecture Data"
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
