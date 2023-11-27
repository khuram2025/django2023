from django.db import models

from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3)  # ISO Alpha-3 country code

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='cities')

    def __str__(self):
        return self.name

class Address(models.Model):
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=10)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    # Include latitude and longitude if you need to perform geographic calculations
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.line1}, {self.city.name}"
