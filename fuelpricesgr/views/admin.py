"""Admin related views
"""
from collections.abc import Mapping

import sqladmin.authentication
import sqlalchemy
import sqlalchemy.orm
from starlette.requests import Request
from starlette.responses import RedirectResponse

from fuelpricesgr import storage


class BaseAdmin(sqladmin.ModelView):
    """Base admin class.
    """
    column_exclude_list = ('id', )
    column_details_exclude_list = ('id', )
    page_size = 100
    page_size_options = (100, 200, 500, 1000)

    def get_column_labels(self) -> Mapping[sqlalchemy.orm.ColumnProperty, str]:
        """Get the column labels. This method replaces underscores and capitalizes the string.

        :return: The column labels.
        """
        return {attr: attr.key.replace('_', ' ').capitalize() for attr in sqlalchemy.inspect(self.model).attrs}


class DailyCountryAdmin(BaseAdmin, model=storage.sql_alchemy.DailyCountry):
    """The daily country admin.
    """
    name = "Daily Country Data"
    name_plural = "Daily Country Data"
    column_formatters = {'fuel_type': lambda m, _: m.fuel_type.description}
    column_searchable_list = ('date', )
    column_sortable_list = ('date', )
    column_default_sort = [('date', True), ('fuel_type', False)]


class DailyPrefectureAdmin(BaseAdmin, model=storage.sql_alchemy.DailyPrefecture):
    """The daily country admin.
    """
    name = "Daily Prefecture Data"
    name_plural = "Daily Prefecture Data"
    column_formatters = {
        'fuel_type': lambda m, _: m.fuel_type.description,
        'prefecture': lambda m, _: m.prefecture.description,
    }
    column_searchable_list = ('date', )
    column_sortable_list = ('date', )
    column_default_sort = [('date', True), ('prefecture', False), ('fuel_type', False)]


class WeeklyCountryAdmin(BaseAdmin, model=storage.sql_alchemy.WeeklyCountry):
    """The daily country admin.
    """
    name = "Weekly Country Data"
    name_plural = "Weekly Country Data"
    column_formatters = {'fuel_type': lambda m, _: m.fuel_type.description}
    column_searchable_list = ('date', )
    column_sortable_list = ('date', )
    column_default_sort = [('date', True), ('fuel_type', False)]


class WeeklyPrefectureAdmin(BaseAdmin, model=storage.sql_alchemy.WeeklyPrefecture):
    """The daily country admin.
    """
    name = "Weekly Prefecture Data"
    name_plural = "Weekly Prefecture Data"
    column_formatters = {
        'fuel_type': lambda m, _: m.fuel_type.description,
        'prefecture': lambda m, _: m.prefecture.description,
    }
    column_searchable_list = ('date', )
    column_sortable_list = ('date', )
    column_default_sort = [('date', True), ('prefecture', False), ('fuel_type', True)]


class UserAdmin(BaseAdmin, model=storage.sql_alchemy.User):
    """The user admin.
    """
    column_searchable_list = ('email', )
    column_exclude_list = ('id', 'password')
    column_details_exclude_list = ('id', 'password')
    form_excluded_columns = ('password', )
    form_widget_args = {
        'created_at': {'readonly': True}, 'updated_at': {'readonly': True}, 'last_login': {'readonly': True},
    }
    can_create = False


class AuthenticationBackend(sqladmin.authentication.AuthenticationBackend):
    """The admin authentication backend.
    """
    async def login(self, request: Request) -> bool:
        """Log in the user.

        :param request: The request.
        :return: True if the user logged in successfully, False otherwise.
        """
        # Get form data
        form = await request.form()
        username, password = form['username'], form['password']

        # Check user credentials
        with storage.get_storage() as s:
            if not s.authenticate(email=username, password=password):
                return False

        request.session.update({"username": username})

        return True

    async def logout(self, request: Request) -> bool:
        """Logout the user. Clear the user session.

        :param request: The request.
        :return: True if the logout attempt was successful.
        """
        request.session.clear()

        return True

    async def authenticate(self, request: Request) -> RedirectResponse | bool:
        """Authenticate the user.

        :param request: The request.
        :return: True if the user was authenticated successfully.
        """
        username = request.session.get("username")
        if not username:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        # Check user is active
        with storage.get_storage() as s:
            user = s.get_user(email=username)
            if user is None or not user.active or not user.admin:
                return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True
