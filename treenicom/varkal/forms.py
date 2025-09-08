from django.forms import ModelForm
from .models import *

class TimeSlotForm(ModelForm):
	class Meta:
		model = TimeSlot
		fields = [
			"service",
			"place",
			"participants_min",
			"participants_max",
			"start_time",
			"end_time",
		]
		labels = {
			"service": "Palvelu",
			"place": "Paikka",
			"participants_min": "Osallistuja min",
			"participants_max": "Osallistuja max",
			"start_time": "Alkaa",
			"end_time": "Päättyy",
		}

class PlaceForm(ModelForm):
	class Meta:
		model = Place
		fields = [
			"name",
			"address",
			"city",
			"info",
		]
		labels = {
			"name": "Paikan nimi",
			"address": "Osoite",
			"city": "Kaupunki",
			"info": "Lisätiedot",
		}			

class ServiceForm(ModelForm):
	class Meta:
		model = Service
		fields = [
			"name",
			"info",
			"duration",
		]
		labels = {
			"name": "Palvelu",
			"info": "Lisätiedot",
			"duration": "Kesto minuuteissa",
		}

# Customer's ModelForm
'''class ReservationCreateForm(ModelForm):
	class Meta:
		model = Reservation
		fields = [
			"service",
			"customer",
		]'''
#		labels = {
#			"customer.first_name": "Etunimi",
#			"customer.last_name": "Sukunimi",
#			"customer.email": "Sähköposti",
#		}

class CustomerCreateForm(ModelForm):
	class Meta:
		model = Customer
		fields = [
			"first_name",
			"last_name",
			"email",
		]
		labels = {
			"first_name": "Etunimi",
			"last_name": "Sukunimi",
			"email": "Sähköposti",
		}

class ReservationCreateForm(ModelForm):
	class Meta:
		model = Reservation
		fields = [
			"customer",
			"timeslot",
		]
		
# This is used when the coach/calendar's owner makes a reservation for a customer
class ReservationStaffCreateForm(ModelForm):
	class Meta:
		model = Reservation
		fields = [
			"customer",
			"timeslot",
		]
		labels = {
			"customer": "Asiakas",
			"timeslot": "Aika",
		}

class ReservationUpdateForm(ModelForm):
	class Meta:
		model = Reservation
		fields = [
			"customer",
			"timeslot",
			"cancelled",
		]
		labels = {
			"customer": "Asiakas",
			"timeslot": "Aika",
			"cancelled": "Peruutettu",
		}

class ReservationCancelForm(ModelForm):
	class Meta:
		model = Reservation
		fields = []

