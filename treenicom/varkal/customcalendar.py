from calendar import HTMLCalendar
from datetime import datetime, timedelta
from .models import TimeSlot
import pytz

class Week:
    def make_week(date):
        week_start = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Helsinki")) - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6, hours=23, minutes=59)
        week_tuples = []

        for wd in range(0, 7):
            d = week_start + timedelta(days=wd)
            data = TimeSlot.objects.filter(start_time__date=datetime(d.year, d.month, d.day))
            date_tuple = (d.day, wd, d.month, data)
            week_tuples.append(date_tuple)

            # Tuples are for HTMLcalendar formatting, dict is for db query
        return week_tuples

class ReservationWeekCalendar(HTMLCalendar):

    weekdays_fin = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]

# https://github.com/python/cpython/blob/132243957ce834cf5ffced4bf8e39d00f6e34e5f/Lib/calendar.py
# Added month number to be included in the formatting. 
    def formatday(self, day, weekday, month, timeslots):
        """
        Return a day as an article. Header + data. 
        """
        if day == 0:
        # day outside month
            return '<h1 class="%s">&nbsp;</h1>' % self.cssclass_noday
        else:
            day_header = f'<h1 class="cal-header-item">{self.weekdays_fin[weekday]} {day}.{month}</h1>'
            day_data = ''
            
            if timeslots:
                for timeslot in timeslots:
                    day_data = day_data + (f'<a class="cal-timeslot" href="calendar/{timeslot.id}/reserve">{timeslot.service}: {timeslot.place}</a>')   
            return f'<article class="cal-article">{day_header}{day_data}'
            
    def formatweek(self, week_tuple):
        week_articles = ''.join(self.formatday(d, wd, m, data) for (d, wd, m, data) in week_tuple)
        return week_articles

