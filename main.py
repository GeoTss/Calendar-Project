import datetime, calendar
# import Database

def reformStr(s):
    return s.strip().split(',')

def get_month(s):
    return int(s[0].split('-')[1])

class Database:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: [],
            9: [],
            10: [],
            11: [],
            12: [],
        }
        
        file = open(file_path, 'r')
        for line in file:
            self.data[get_month(reformStr(line))].append(reformStr(line))
        
        print("Loaded events: ", self.data)
        file.close()
    
    def save(self):
        open(self.file_path, 'r+').truncate(0)
        file = open(self.file_path, 'w')
        
        for i in range(1, 13):
            for j in self.data[i]:
                file.write(','.join(j)+'\n')
        file.close()
     
    def print_events(self):
        for i in range(1, 13):
            for j in self.data[i]:
                print(j)
    
    def event_exists(self, event, month):
        return event in self.data[month]
        
    def dateHasEvent(self, date, month): 
        for i in self.data[month]:
            if i[0] == date:
                return True
        return False
    
    def add_event(self, event):
        toAddEvent = reformStr(event)

        if not self.event_exists(toAddEvent, get_month(toAddEvent)):
            self.data[get_month(toAddEvent)].append(toAddEvent)
            return True
        else:
            print("Event already added")
            return False
    
    def delete_event(self, event):
        toDeleteEvent = reformStr(event)
        if self.event_exists(toDeleteEvent, get_month(toDeleteEvent)):
            self.data[get_month(toDeleteEvent)].remove(toDeleteEvent)
            return True
        else:
            print("Event doesn't exist")
            return False

    def update_event(self, month, old_event, index, new_date, new_time, new_dur, new_title):
        if self.event_exists(old_event, month):
            self.data[month][index][0] = new_date
            self.data[month][index][1] = new_time
            self.data[month][index][2] = new_dur
            self.data[month][index][3] = new_title
        
        
month_dict = {
    1: 'ΙΑΝ',
    2: 'ΦΕΒ',
    3: 'ΜΑΡ',
    4: 'ΑΠΡ',
    5: 'ΜΑΙ',
    6: 'ΙΟΥΝ',
    7: 'ΙΟΥΛ',
    8: 'ΑΥΓ',
    9: 'ΣΕΠ',
    10: 'ΟΚΤ',
    11: 'ΝΟΕ',
    12: 'ΔΕΚ'
}


d = Database("events.csv")
def print_calendar(year, month):
    print("-"*47)
    print(month_dict[month], year, end='\n\n')
    print("-"*47)
    
    month_list = calendar.monthcalendar(year, month)

    prev_year = year
    prev_month = month
    if month == 1:
        prev_year -= 1
        prev_month = 12
    else:
        prev_month -= 1
    
    prev_month_range = calendar.monthrange(prev_year, prev_month)
    curr_month_range = calendar.monthrange(year, month)

    k = curr_month_range[0]-1
    for i in range(curr_month_range[0]):
        month_list[0][k] = prev_month_range[1]-i
        k -= 1
    
    n = len(month_list)
    k = 1
    for i in range(7):
        if month_list[n-1][i] == 0:
            month_list[n-1][i] = k
            k += 1
    
    print("  ΔΕΥ |  ΤΡΙ |  ΤΕΤ |  ΠΕΜ |  ΠΑΡ |  ΣΑΒ |  ΚΥΡ")
    for w in range(n):
        week = []
        for i in range(7):
            if not((w == 0 and month_list[0][i] > 7) or (w == n-1 and month_list[w][i] < 10)):
                asterisk = ''
                date = str(year) + '-' + str(month) + '-' + str(month_list[w][i])
                if d.dateHasEvent(date, month):
                    asterisk = '*'
                week.append("%5s" % ('[' + ("%3s" % (asterisk + str(month_list[w][i]))) + ']'))
            else:
                week.append("%5s"%(str(month_list[w][i])))
        print(' |'.join(week))


d.add_event("2023-1-8,13:30,60,C++ course lesson 2")
d.add_event("2023-1-20,13:30,60,C++ course")
d.add_event("2023-1-31,13:45,90,Event 2")
d.add_event("2024-1-4,13:30,60,C++ course lesson 3")

d.delete_event("2023-1-8,13:30,60,C++ course lesson 2")
d.print_events()
print_calendar(2023, 1)

d.delete_event("2023-1-10,14:00,100,Updated event4")
d.delete_event("2023-1-10,14:00,100,Updated event2")
d.delete_event("2023-1-10,14:00,100,Updated event3")

d.print_events()
d.save()
print_calendar(2023, 1)
d.print_events()

# index = int(input("Enter input: "))
# d.update_event(1, d.data[1][index], index, "2023-1-10", "14:00", "100", "Updated event4")
# print_calendar(2023, 2)
# print_calendar(datetime.datetime.now().year, datetime.datetime.now().month)