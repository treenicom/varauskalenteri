from calendar import HTMLCalendar
from datetime import datetime, timedelta
from .models import TimeSlot
import pytz

class Week:
    def make_week(date):
        week_start = datetime(date.year, date.month, date.day, tzinfo=pytz.timezone("Europe/Helsinki")) - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6, hours=23, minutes=59)
        week_tuples = []
        week_dict = {
            "start": week_start,
            "end": week_end,
        }

        for i in range(0, 7):
            d = week_start + timedelta(days=i)
            wd = i
            date_tuple = (d.day, wd, d.month)
            week_tuples.append(date_tuple)

            # Tuples are for HTMLcalendar formatting, dict is for db query
        return week_tuples, week_dict

class ReservationWeekCalendar(HTMLCalendar):

# https://github.com/python/cpython/blob/132243957ce834cf5ffced4bf8e39d00f6e34e5f/Lib/calendar.py
# Added month number to be included in the formatting
    def formatday(self, day, weekday, month):
        """
        Return a day as a table cell.
        """
        if day == 0:
        # day outside month
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        else:
            return '<td class="%s">%d.%d</td>' % (self.cssclasses[weekday], day, month)

    def formatweek(self, week_tuple, week_dict):
        # is it smart to make a new query every time calendar loads?
        week_data = TimeSlot.objects.filter(start_time__gte=week_dict["start"]).filter(start_time__lte=week_dict["end"])
        s = ''.join(self.formatday(d, wd, m) for (d, wd, m) in week_tuple)
        weekdays_row = '<tr><th>Ma</th><th>Ti</th><th>Ke</th><th>To</th><th>Pe</th><th>La</th><th>Su</th></tr>'
        date_row = '<tr class="date-row">%s</tr>' % s
        timeslot_rows = []
        timeslot_cells = {
            1:"mon",
            2:"tue",
            3:"wed",
            4:"thu",
            5:"fri",
            6:"sat",
            7:"sun",
        }

        for hour in range(10, 20):
            row_data = []
            for day_cell in timeslot_cells:
                timeslot_data = ''
                for timeslot in week_data:
                    timeslot_start_h = int(timeslot.start_time.strftime("%H"))
                    timeslot_day = int(timeslot.start_time.strftime("%u"))
                    if hour == timeslot_start_h and day_cell == timeslot_day:
                        timeslot_data = f'<a href="calendar/{timeslot.id}/reserve">{timeslot.service}: {timeslot.place}</a>'
                td = f'<td class="{timeslot_cells[day_cell]}">{timeslot_data}</td>'
                row_data.append(td)
            row_data = ''.join(row_data)
            row = f'<tr class="hour-row" id="hr{hour}">{row_data}</tr>'
            timeslot_rows.append(row)
            
        timeslot_rows = ''.join(timeslot_rows)
        table_data = weekdays_row + date_row + timeslot_rows

        return table_data

'''
if not week_data:
pass
else:
for hour in range(10, 20):
timeslot_cells = {
0:"",
1:"",
2:"",
3:"",
4:"",
5:"",
6:"",
}

for wd in timeslot_cells:
for timeslot in week_data:
if timeslot.start_time.hour == hour and timeslot.start_time.weekday() == wd:
data = '<td class="%s"><a href="calendar/%d/reserve">%s</a></td>' % (self.cssclasses[wd], timeslot.pk, timeslot)
elif not timeslot_cells[wd]:
data = '<td class="%s">&nbsp</td>' % self.cssclasses[wd]
timeslot_cells[wd] = data
print(data)
timeslots_str = ''.join(timeslot_cells[value] for value in sorted(timeslot_cells))
row = '<tr class="hour-row" id="hr%d">%s</tr>' % (hour, timeslots_str)
timeslot_rows.append(row)

timeslot_rows = ''.join(timeslot_rows)
wd_row = '<tr><th>Ma</th><th>Ti</th><th>Ke</th><th>To</th><th>Pe</th><th>La</th><th>Su</th></tr>'
table_data = wd_row + date_row + timeslot_rows

return table_data
'''
