"""Admin related views
"""
import sqladmin
import sqlalchemy
import sqlalchemy.orm

from fuelpricesgr import models


class BaseAdmin(sqladmin.ModelView):
    """Base admin class.
    """
    column_exclude_list = 'id',
    column_details_exclude_list = 'id',
    page_size = 100
    page_size_options = (100, 200, 500, 1000)

    def get_column_labels(self) -> dict[sqlalchemy.orm.ColumnProperty, str]:
        """Get the column labels. This method replaces underscores and capitalizes the string.

        :return: The column labels.
        """
        return {attr: attr.key.replace('_', ' ').capitalize() for attr in sqlalchemy.inspect(self.model).attrs}


class DailyCountryAdmin(BaseAdmin, model=models.DailyCountry):
    """The daily country admin.
    """
    name = "Daily Country Data"
    name_plural = "Daily Country Data"
    column_formatters = {'fuel_type': lambda m, _: m.fuel_type.description}
    column_searchable_list = 'date',
    column_sortable_list = 'date',
    column_default_sort = [('date', True), ('fuel_type', False)]


class DailyPrefectureAdmin(BaseAdmin, model=models.DailyPrefecture):
    """The daily country admin.
    """
    name = "Daily Prefecture Data"
    name_plural = "Daily Prefecture Data"
    column_formatters = {
        'fuel_type': lambda m, _: m.fuel_type.description,
        'prefecture': lambda m, _: m.prefecture.description,
    }
    column_searchable_list = 'date',
    column_sortable_list = 'date',
    column_default_sort = [('date', True), ('prefecture', False), ('fuel_type', False)]


class WeeklyCountryAdmin(BaseAdmin, model=models.WeeklyCountry):
    """The daily country admin.
    """
    name = "Weekly Country Data"
    name_plural = "Weekly Country Data"
    column_formatters = {'fuel_type': lambda m, _: m.fuel_type.description}
    column_searchable_list = 'date',
    column_sortable_list = 'date',
    column_default_sort = [('date', True), ('fuel_type', False)]


class WeeklyPrefectureAdmin(BaseAdmin, model=models.WeeklyPrefecture):
    """The daily country admin.
    """
    name = "Weekly Prefecture Data"
    name_plural = "Weekly Prefecture Data"
    column_formatters = {
        'fuel_type': lambda m, _: m.fuel_type.description,
        'prefecture': lambda m, _: m.prefecture.description,
    }
    column_searchable_list = 'date',
    column_sortable_list = 'date',
    column_default_sort = [('date', True), ('prefecture', False), ('fuel_type', True)]


class UserAdmin(BaseAdmin, model=models.User):
    """The user admin.
    """
    column_searchable_list = 'email',
    column_exclude_list = ('id', 'password')
    column_details_exclude_list = ('id', 'password')
    form_excluded_columns = 'password',
    form_widget_args = {
        'created_at': {'readonly': True}, 'updated_at': {'readonly': True}, 'last_login': {'readonly': True},
    }
