from datetime import datetime, timedelta
import pytz
import random
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db import IntegrityError
from django.db.models import ProtectedError, F
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .customcalendar import *
from .forms import *
from .models import *
from .mail import *

#Global vars
NOW = datetime.now(tz=pytz.timezone("Europe/Helsinki"))

class RegisterView(SuccessMessageMixin, CreateView):
	form_class = UserCreationForm
	template_name = "registration/register.html"
	success_url = "/login"
	success_message = "Käyttäjän luominen onnistui! Voit nyt kirjautua sisään."

'''class LogoutView(LogoutView):
	def post(self, request, *args, **kwargs):
		auth_logout(request)
		redirect_to = self.get_success_url()
		if redirect_to != request.get_full_path():
			# Redirect to target page once the session has been cleared.
			return HttpResponseRedirect(redirect_to)
		return super().get(request, *args, **kwargs)'''

class CalendarListView(ListView):
	model = TimeSlot
	ordering = "start_time"
	cal = ReservationWeekCalendar()

	def get(self, request, *args, **kwargs):
		# Flush session data on page reload. Show current week on page reload.
		try:
			del request.session['week']
		except KeyError:
			pass
		self.object_list = self.get_queryset()
		allow_empty = self.get_allow_empty()
		if not allow_empty:
			pass
			# When pagination is enabled and object_list is a queryset,
			# it's better to do a cheap query than to load the unpaginated
			# queryset in memory.
		if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, "exists"):
			is_empty = not self.object_list.exists()
		else:
			is_empty = not self.object_list
		if is_empty:
			pass
			#raise Http404(_("Empty list and “%(class_name)s.allow_empty” is False.")% {"class_name": self.__class__.__name__,})
		context = self.get_context_data()
		return self.render_to_response(context)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["week_calendar"] = make_week_context(NOW)
		#print(context)
		return context

class CalendarCreateView(UserPassesTestMixin, CreateView):
	model = TimeSlot
	success_url = "/"
	form_class = TimeSlotForm

	def test_func(self):
		return self.request.user.is_staff

class CalendarUpdateView(UserPassesTestMixin, UpdateView):
	model = TimeSlot
	success_url = "/"
	form_class = TimeSlotForm

	def test_func(self):
		return self.request.user.is_staff

class CalendarDeleteView(UserPassesTestMixin, DeleteView):
	model = TimeSlot
	success_url = "/"

	def test_func(self):
		return self.request.user.is_staff

class PlaceListView(ListView):
	model = Place

class PlaceCreateView(UserPassesTestMixin, CreateView):
	model = Place
	success_url = "/place"
	form_class = PlaceForm

	def test_func(self):
		return self.request.user.is_staff

class PlaceUpdateView(UserPassesTestMixin, UpdateView):
	model = Place
	success_url = "/place"
	form_class = PlaceForm

	def test_func(self):
		return self.request.user.is_staff

class PlaceDeleteView(UserPassesTestMixin, DeleteView):
	model = Place
	success_url = "/place"
	success_message = ""

	def test_func(self):
		return self.request.user.is_staff

	def form_valid(self, form):
		self.object = self.get_object()
		success_url = self.get_success_url()
		try:
			return self.object.delete()
		except ProtectedError:
			messages.error(self.request, "Et voi poistaa paikkaa, jonne on tehty varauksia!")
		finally:
			return HttpResponseRedirect(success_url)

class ServiceListView(ListView):
	model = Service

class ServiceCreateView(UserPassesTestMixin, CreateView):
	model = Service
	success_url = "/service"
	form_class = ServiceForm

	def test_func(self):
		return self.request.user.is_staff

class ServiceUpdateView(UserPassesTestMixin, UpdateView):
	model = Service
	success_url = "/service"
	form_class = ServiceForm

	def test_func(self):
		return self.request.user.is_staff

class ServiceDeleteView(UserPassesTestMixin, DeleteView):
	model = Service
	success_url = "/service"

	def test_func(self):
		return self.request.user.is_staff

	def form_valid(self, form):
		self.object = self.get_object()
		success_url = self.get_success_url()
		try:
			return self.object.delete()
		except ProtectedError:
			messages.error(self.request, "Et voi poistaa palvelua, johon on tehty varauksia!")
		finally:
			return HttpResponseRedirect(success_url)

class ReservationListView(ListView):
	model = Reservation

	def test_func(self):
		return self.request.user.is_authenticated

	def get_queryset(self):
		if(self.request.user.is_staff):
			return Reservation.objects.all()
		else:
			return Reservation.objects.filter(user__username=self.request.user).exclude(cancelled__isnull=False)

class ReservationCreateView(CreateView):
	model = Reservation
	success_url = "/"
	form_class = CustomerCreateForm

	def make_cancel_code(self):
		return "".join(random.choice('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ') for i in range(8))

    # https://docs.djangoproject.com/en/4.2/topics/class-based-views/generic-display/#adding-extra-context
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["timeslot"] = TimeSlot.objects.get(pk=self.kwargs["pk"])
		return context

	def form_valid(self, form):
    #If the form is valid, save the associated model.
    # TODO (not urgent): validate customer to reduce duplicates in db.
    # If fname, lname, email > filter existing customers then dont save new row
    # use existing customer to make new reservation
		try:
			TimeSlot.objects.filter(pk=self.kwargs["pk"]).update(participants=F("participants") + 1)
		except IntegrityError:
			messages.error(self.request, "Valitsemasi aika on täynnä.")
			return HttpResponseRedirect(self.success_url)
		else:
			#print("HEP", form['email'].value())
			self.object = form.save()
			customer=self.object
			timeslot=TimeSlot.objects.get(pk=self.kwargs["pk"])
			# This is here just in case the pseudo-random cancel code would be a duplicate
			max_attempts = 10
			for attempt in range(max_attempts):
				try:
					cancel_code = self.make_cancel_code()
					reservation = Reservation(customer=customer, timeslot=timeslot, cancel_code=cancel_code)
					reservation.save()
					break
				except IntegrityError:
					attempt = attempt + 1
					if attempt == max_attempts:
						messages.error(self.request, "Jotain meni pieleen. Kokeile uudestaan.")

			try:
				email = Email()
				#print(f"1: {customer} 2: {timeslot}")
				print("DOI", customer, reservation)
				email.send_event_email(customer, reservation)
			except FileExistsError:
			    pass
			return super().form_valid(form)

class ReservationUpdateView(UserPassesTestMixin, UpdateView):
	model = Reservation
	success_url = "/reservation"
	form_class = ReservationUpdateForm

	def test_func(self):
		return self.request.user.is_staff

	def form_valid(self, form):
		self.object = form.save()
		timeslot_id = self.object.timeslot.id
		participants_count = Reservation.objects.filter(timeslot__id=timeslot_id, cancelled__isnull=True).count()
		TimeSlot.objects.filter(pk=timeslot_id).update(participants=participants_count)
		return super().form_valid(form)

def cancelReservation(request):
    if(request.method=="GET"):
        return render(request, "varkal/reservation_customer_cancel.html")
    elif(request.method=="POST"):
        try:
            reservation = Reservation.objects.get(cancel_code=request.POST["cancel_code"])
            if(reservation.cancelled is None):
                reservation.cancelled = NOW
                reservation.save()
                messages.success(request, f"Varauksesi ({reservation}) peruminen onnistui.")
            else:
                messages.success(request, f"Varauksesi ({reservation}) on jo peruttu.")
            return HttpResponseRedirect("/")
        except Reservation.DoesNotExist:
            print("DOES NOT EXIST")
            messages.error(request, "Varausta ei löytynyt. Tarkista, että syötit peruutuskoodin oikein.")
            return HttpResponseRedirect("/reservation/cancel")       
        #return render(request, "varkal/reservation_customer_cancel.html")
        

class ReservationCancelView(UserPassesTestMixin, UpdateView):
    model = Reservation
    success_url = "/reservation"
    form_class = ReservationStaffCancelForm
    template_name = "varkal/reservation_confirm_cancel.html"

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        reservation_id = self.kwargs["pk"]
        form.instance.user = self.request.user
        form.instance.timeslot = Reservation.objects.get(pk=reservation_id).timeslot
        form.instance.cancelled = datetime.now()
        self.object = form.save()
        timeslot_id = self.object.timeslot.id
        participants_count = Reservation.objects.filter(timeslot__id=timeslot_id, cancelled__isnull=True).count()
        TimeSlot.objects.filter(pk=timeslot_id).update(participants=participants_count)
        return super().form_valid(form)

class ReservationDeleteView(UserPassesTestMixin, DeleteView):
	model = Reservation
	success_url = "/reservation"

	def test_func(self):
		return self.request.user.is_staff

	def form_valid(self, form):
		success_url = self.get_success_url()
		self.object.delete()
		timeslot_id = self.object.timeslot.id
		participants_count = Reservation.objects.filter(timeslot__id=timeslot_id, cancelled__isnull=True).count()
		TimeSlot.objects.filter(pk=timeslot_id).update(participants=participants_count)
		return HttpResponseRedirect(success_url)

#HTMX

#def onclick_flush(request):
#	request.session.flush()
#	return HttpResponse(make_week_context(NOW))

def make_week_context(d):
	try:
		wk_tuples, wk_dict = Week.make_week(d)
		week_cal = CalendarListView.cal.formatweek(wk_tuples, wk_dict)
	except IndexError:
		week_cal = []
	return week_cal

def get_next_week(request):
	# First click. Applies when there is no session data
	if 'week' not in request.session:
		next_week = datetime.today() + timedelta(days=7)
		request.session['week'] = next_week.strftime("%Y/%m/%d")
		week_cal = make_week_context(next_week)
	else:
		d = datetime.strptime(request.session['week'], "%Y/%m/%d")
		next_week = d + timedelta(days=7)
		request.session['week'] = next_week.strftime("%Y/%m/%d")
		week_cal = make_week_context(next_week)
	return HttpResponse(week_cal)

def get_prev_week(request):
	# First click. Applies when there is no session data
	if 'week' not in request.session:
		prev_week = datetime.today() - timedelta(days=7)
		request.session['week'] = prev_week.strftime("%Y/%m/%d")
		week_cal = make_week_context(prev_week)
	else:
		d = datetime.strptime(request.session['week'], "%Y/%m/%d")
		prev_week = d - timedelta(days=7)
		request.session['week'] = prev_week.strftime("%Y/%m/%d")
		week_cal = make_week_context(prev_week)
	return HttpResponse(week_cal)

def get_current_week(request):
    request.session.flush()
    curr_week = datetime.today()
    week_cal = make_week_context(curr_week)
    return HttpResponse(week_cal)
