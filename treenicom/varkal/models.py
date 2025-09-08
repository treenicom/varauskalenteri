from django.core.validators import MaxValueValidator, MinLengthValidator
from django.db import models
from django.db.models import CheckConstraint, Q, F

class Service(models.Model):
	name = models.CharField(max_length=100)
	info = models.TextField(max_length=500)
	duration = models.PositiveIntegerField(default=45, validators=[MaxValueValidator(120)])

	def __str__(self):
		return str(self.name)

class Place(models.Model):
	name = models.CharField(max_length=150)
	address = models.CharField(max_length=150)
	city = models.CharField(max_length=50)
	info = models.TextField(max_length=500)

	def __str__(self):
		return str(self.name)

class TimeSlot(models.Model):
	service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True)
	place = models.ForeignKey(Place, on_delete=models.PROTECT)
	participants_min = models.PositiveIntegerField()
	participants_max = models.PositiveIntegerField()
	participants = models.PositiveIntegerField(default=0)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField()

	class Meta:
		constraints = [
			CheckConstraint(
				check = Q(participants__lte=F("participants_max")),
				name = "check_participants",
			),
		]

	def __str__(self):
		start_format = self.start_time.strftime("%-d.%-m. %H:%M")
		#end_format = self.end_time.strftime("%H:%M")
		if self.service is None:
			return f"{self.place} VAPAA VALINTA"
		return f"{self.place} ({self.service} {self.service.duration}min {start_format})"

class Customer(models.Model):
	#user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
	id = models.BigAutoField(primary_key=True)
	first_name = models.CharField(max_length=120)
	last_name = models.CharField(max_length=120)
	email = models.CharField(max_length=255)

	def __str__(self):
		return f"{self.first_name} {self.last_name}"

class Reservation(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=0)
	timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
	service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
	cancel_code = models.CharField(max_length=8, validators=[MinLengthValidator(8)], unique=True)
	cancelled = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return f"{self.customer}: {self.timeslot}"
