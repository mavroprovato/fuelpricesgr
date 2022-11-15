"""Module containing the database models.
"""
from tortoise import fields, models

from fuelpricesgr import enums


class DailyCountry(models.Model):
    """The daily country database model
    """
    id = fields.IntField(pk=True)
    date = fields.DateField(index=True)
    fuel_type = fields.CharEnumField(enum_type=enums.FuelType)
    number_of_stations = fields.IntField()
    price = fields.FloatField()

    class Meta:
        table = 'daily_country'


class DailyPrefecture(models.Model):
    """The daily prefecture database model
    """
    id = fields.IntField(pk=True)
    date = fields.DateField(index=True)
    prefecture = fields.CharEnumField(enum_type=enums.Prefecture)
    fuel_type = fields.CharEnumField(enum_type=enums.FuelType)
    price = fields.FloatField()

    class Meta:
        table = 'daily_prefecture'


class WeeklyCountry(models.Model):
    """The weekly country database model
    """
    id = fields.IntField(pk=True)
    date = fields.DateField(index=True)
    fuel_type = fields.CharEnumField(enum_type=enums.FuelType)
    lowest_price = fields.FloatField()
    highest_price = fields.FloatField()
    median_price = fields.FloatField()

    class Meta:
        table = 'weekly_country'


class WeeklyPrefecture(models.Model):
    """The weekly prefecture database model
    """
    id = fields.IntField(pk=True)
    date = fields.DateField(index=True)
    fuel_type = fields.CharEnumField(enum_type=enums.FuelType)
    prefecture = fields.CharEnumField(enum_type=enums.Prefecture)
    lowest_price = fields.FloatField()
    highest_price = fields.FloatField()
    median_price = fields.FloatField()

    class Meta:
        table = 'weekly_prefecture'
