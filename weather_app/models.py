from django.db import models


class Location(models.Model):
  name = models.CharField(max_length=30)

  def __str__(self):
    return self.name

class Weather(models.Model):
  
  location = models.ForeignKey(Location, on_delete=models.CASCADE)
  temperature = models.FloatField()
  humidity = models.IntegerField() # Convert to percentage later 
  wind_speed = models.FloatField()
  temperature_description = models.CharField(max_length=100)
  image = models.ImageField(upload_to='weather_images')
  date = models.DateTimeField()

  def __str__(self):
    return self.location

