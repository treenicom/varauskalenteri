from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import *

urlpatterns = [
	path("register", RegisterView.as_view()),
	path("login", LoginView.as_view(next_page="/")),
	path("accounts/login/", LoginView.as_view(next_page="/")),
	path("logout", LogoutView.as_view(next_page="/")),

	path("", CalendarListView.as_view()),
	path("calendar", CalendarListView.as_view()),
	path("calendar/add", CalendarCreateView.as_view()),
	path("calendar/<int:pk>/edit", CalendarUpdateView.as_view()),
	path("calendar/<int:pk>/delete", CalendarDeleteView.as_view()),
	path("calendar/<int:pk>/reserve", ReservationCreateView.as_view()),
	#HTMX
	path("calendar/nextweek", get_next_week),
	path("calendar/prevweek", get_prev_week),
	#path("flush", onclick_flush),
	
	path("place", PlaceListView.as_view()),
	path("place/add", PlaceCreateView.as_view()),
	path("place/<int:pk>/edit", PlaceUpdateView.as_view()),
	path("place/<int:pk>/delete", PlaceDeleteView.as_view()),

	path("service", ServiceListView.as_view()),
	path("service/add", ServiceCreateView.as_view()),
	path("service/<int:pk>/edit", ServiceUpdateView.as_view()),
	path("service/<int:pk>/delete", ServiceDeleteView.as_view()),

	path("reservation", ReservationListView.as_view()),
	path("reservation/add", ReservationCreateView.as_view()),
	path("reservation/<int:pk>/edit", ReservationUpdateView.as_view()),
	path("reservation/<int:pk>/cancel", ReservationCancelView.as_view()),
	path("reservation/<int:pk>/delete", ReservationDeleteView.as_view()),

]
