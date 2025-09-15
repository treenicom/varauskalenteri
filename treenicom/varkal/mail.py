import pytz
from datetime import datetime
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string

TZ = pytz.timezone('Europe/Helsinki')

class Email:
	def send_event_email(self, customer, reservation):
		html_content = render_to_string("mail_template.html", {"customer": customer, "reservation": reservation})
		text_content = strip_tags(html_content)
		message = EmailMultiAlternatives(
			subject=f"{reservation.timeslot}",
			body = text_content,
			#body=f"Hei, {customer.first_name} tässä muistutus tehdystä varauksestasi: {reservation.timeslot}.\n\nPeruutuskoodi: {reservation.cancel_code}",
			to=[customer.email],
			# TODO: cancel code, add field to model
			# if POST match reservation cancel code -> cancelled = True
		)
		ics_file_path = self.make_event_ics(reservation)
		#  TODO: attach right file, match reservation pk to first two characters of ics file
		message.attach_alternative(html_content, "text/html")
		message.attach_file(ics_file_path, "text/calendar")
		message.send()

	def make_event_ics(self, reservation):
		created = datetime.now(tz=TZ).strftime("%Y%m%dT%H%M%S")
		filename = f"{reservation.pk}-{created}.ics"
		# TODO: Implement absolute path into env var
		with open(f"varkal/calendarinvites/{filename}", "x") as cal_event:
			for line in self.get_template_ics():
				cal_event.write(line.format(
					summary=reservation.timeslot,
					uid=filename.replace(".ics", "") + "@rennejamsen.com",
					dtstamp=created,
					dtstart=reservation.timeslot.start_time.strftime("%Y%m%dT%H%M%S"),
					duration=f"PT{int((reservation.timeslot.end_time - reservation.timeslot.start_time).seconds / 60)}M"
				) + "\n")
		return f"varkal/calendarinvites/{filename}"

	def get_template_ics(self):
		with open("varkal/templates/calendar_template.ics", "r", encoding="UTF-8") as template:
			lines = [line.rstrip() for line in template]
			return lines
