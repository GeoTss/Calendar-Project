import datetime, calendar

class Event:
    def __init__(self, event="NULL,00:00,0,NULL") -> None:
        self.event = event.strip().split(',')
        self.full_date = self.event[0]
        self.full_date_mut = self.event[0].split('-')
        self.timedelta_begin = datetime.timedelta(hours=self.get_hour(), minutes=self.get_minute())
        self.timedelta_end = self.timedelta_begin + datetime.timedelta(minutes=self.get_dur())
        
    def __eq__(self, other) -> bool:
        return all([self.event[i] == other.get_reformed_event()[i] for i in range(4)])

    def __str__(self):
        return f'[{self.get_title()}] -> Date: {self.full_date}, Time: {self.get_time()}, Duration: {self.get_dur()}'

    def get_timedeltaBegin(self):
        "Returns the begining time of the event in a timedelta object."
        return self.timedelta_begin
    def get_timedeltaEnd(self):
        "Returns the ending time of the event in a timedelta object. (begining_time + event_duration)"
        return self.timedelta_end
    def get_reformed_event(self):
        "Returns event in a list which contains each element of the event seperately in the format: [date, time, duration, title]"
        return self.event
    def get_full_date(self):
        "Returns date in format: YYYY-MM-DD"
        return self.full_date
    def get_year(self):
        return int(self.full_date_mut[0])
    def get_month(self):
        return int(self.full_date_mut[1])
    def get_day(self):
        return int(self.full_date_mut[2])
    def get_time(self):
        return self.event[1]
    def get_hour(self):
        return int(self.event[1].split(':')[0])
    def get_minute(self):
        return int(self.event[1].split(':')[1])
    def get_dur(self):
        return int(self.event[2])
    def get_title(self):
        return self.event[3]
    
    
def overlapse(added: Event, toAdd: Event):
    """
    Tests if two events have overlapsing hours with two test cases:
    1) Added event ends before toAdd ends
        (added.get_timedeltaBegin() < toAdd.get_timedeltaBegin() < added.get_timedeltaEnd())
    
    2) Added event ends after toAdd ends
        (added.get_timedeltaBegin() < toAdd.get_timedeltaEnd() < added.get_timedeltaEnd())
    """
    return (added.get_timedeltaBegin() < toAdd.get_timedeltaBegin() < added.get_timedeltaEnd()) or\
        (added.get_timedeltaBegin() < toAdd.get_timedeltaEnd() < added.get_timedeltaEnd())

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
        
        self.changed = False
        file = open(file_path, 'r')
        for line in file:
            event = Event(line)
            self.data[event.get_month()].append(event)
        file.close()
    
    def getData(self):
        return self.data
        
    def save(self):
        """
            Saves all data in events.csv file by rewriting it.
            If no change is detected by self.change, then it does nothing
        """
        if self.changed:
            open(self.file_path, 'r+').truncate(0)
            file = open(self.file_path, 'w')
            
            for i in range(1, 13):
                for j in self.data[i]:
                    file.write(','.join(j.get_reformed_event())+'\n')
            file.close()
            print("Changes saved.\n")
        else:
            print("No modification found to save.\n")
    
    def event_exists(self, event, month):
        """
            Checks if an event exists in a specific month
        """
        for j in self.data[month]:
            if j.get_reformed_event() == event.get_reformed_event():
                return True
        return False
    
    def dateHasEvent(self, date, month): 
        """
            Checks if a specific date has any events. Returns bool
        """
        for i in self.data[month]:
            if i.get_full_date() == date:
                return True
        return False
    
    def findEventsInDay(self, date, month, day, ignore: Event = Event()):
        """
            Finds all events in a specific day and returns them in a list. If none found then it returns an empty list
        """
        if not self.dateHasEvent(date, month):
            return []
        return [i for i in self.data[month] if (i.get_day() == day and i != ignore)]
    
    def getAvaiableHours(self, event: Event, ignore: Event = Event()):
        """
            Finds all avaiable hours that do not overlapse with other events in the same day to add a specific event and returns them in a two dimensional list containing other lists with two timedelta elements representing a time space.
            First element is the begining of the time space.
            Second element is the end of the time space
        """
        eventsInDay = self.findEventsInDay(event.full_date, event.get_month(), event.get_day(), ignore)
        eventsInDay.sort(key=lambda x: x.get_timedeltaBegin())
        
        startHour = datetime.timedelta(minutes=0)
        flag = False
        avaiableHours = []
        if eventsInDay[0].get_timedeltaBegin() < datetime.timedelta(minutes=event.get_dur()):
            startHour = eventsInDay[0].get_timedeltaEnd()
            flag = True
        
        for i in eventsInDay:
            if flag or i == event:
                flag = False
                continue
            if i.get_timedeltaEnd() > datetime.timedelta(minutes=1440-event.get_dur()):
                break
            if i.get_timedeltaBegin() - startHour >= datetime.timedelta(minutes=event.get_dur()):
                avaiableHours.append([startHour, i.get_timedeltaBegin()-datetime.timedelta(minutes=event.get_dur())])
            startHour = i.get_timedeltaEnd()
                
        if eventsInDay[-1].get_timedeltaEnd() <= datetime.timedelta(minutes=1440-event.get_dur()):
            avaiableHours.append([eventsInDay[-1].get_timedeltaEnd(), datetime.timedelta(minutes=0)])
        return avaiableHours
        
    
    def doesOverlapseInSameDay(self, event: Event, ignore: Event = Event()):
        return any(overlapse(i, event) for i in self.findEventsInDay(event.full_date, event.get_month(), event.get_day(), ignore))
    
    def add_event(self, event):
        if not self.event_exists(event, event.get_month()):
            if not self.doesOverlapseInSameDay(event):
                self.data[event.get_month()].append(event)
                self.changed = True
                return 1
            else:
                return 2
        else:
            print("Event already added")
            return 3
        
    
    def delete_event(self, event):
        if self.event_exists(event, event.get_month()):
            self.data[event.get_month()].remove(event)
            self.changed = True
            return True
        else:
            print("Event doesn't exist")
            return False

    def update_event(self, month, index, new_date, new_time, new_dur, new_title):
        new_event = new_date + ',' + new_time + ',' + new_dur + ',' + new_title
        self.data[month][index] = Event(new_event)
        self.changed = True
        

def enterEventElement(msg, verification, can_skip, alt_ret=""):
    """
        Higher order function to enter an element for a event using it's own verification.
        It can also utilise the enter keyword, if is allowed by can_skip returning alt_ret as an alternative
    """
    ret = verification(input(msg), can_skip)
    while not ret[0]:
        print('Μη έγκυρη απάντηση.')
        ret = verification(input(msg), can_skip)
        
    if ret[1] == " ":
        return alt_ret
    return ret[1]

"""
    ====================================
    Verifications for all event elements
    ====================================
"""
def timeInputVerification(time, can_skip: bool):
    if time == '':
        return [can_skip, " "]
    
    time.strip()
    if ':' in time:
        temp = time.split(':')
        if len(temp) == 2:
            if not(temp[0].isnumeric() and temp[1].isnumeric()):
                return [False, time]
            hours = int(temp[0])
            minutes = int(temp[1])
            
            if (not (0 <= hours <= 23)) or (not (0 <= minutes <= 59)):
                return [False, time]
        else:
            return [False, time]
    else:
        return [False, time]
    
    return [True, time]
        

def durationInputVerification(duration, can_skip: bool):
    if duration == '':
        return [can_skip, " "]
    
    if not duration.isnumeric():
        return [False, duration]
    if int(duration) <= 0:
        return [False, duration]
    return [True, duration]

def titleInputVerification(title, can_skip: bool):
    if title == '':
        return [can_skip, " "]
    if ',' in title:
        return [False, title]
    return [True, title]

def enterDay(howManyDays):
    DD = int(input("Εισάγετε Μέρα "))
    while DD < 1 or DD > howManyDays:
        print("Μη έγκυρη απάντηση!")
        DD = int(input("Εισάγετε Μέρα "))
    return DD
        

def enterMonth():
    MM = int(input("Εισάγετε Μήνα: "))
    while not (1 <= MM <= 12):
        print("Μη έγκυρη απάντηση!")
        MM = int(input("Εισάγετε Μήνα "))
    return MM

def enterYear():
    Y = int(input("Εισάγετε χρόνο: "))
    
    while Y <= 0:
        print("Μη έγκυρη απάντηση!")
        Y = int(input("Εισάγετε χρόνο: "))
    return Y

def dateInputVerification(date, can_skip: bool):
    if date == '':
        return [can_skip, " "]
    
    date.strip()
    if '-' in date:
        temp = date.split('-')
        if len(temp) == 3:
            if temp[0].isnumeric() and temp[1].isnumeric() and temp[2].isnumeric():
                YYYY = int(temp[0])
                if YYYY <= 0:
                    return [False, date]
                MM = int(temp[1])
                if not(1 <= MM <= 12):
                    return [False, date]
                howManyDays = calendar.monthrange(YYYY, MM)[1]
                DD = int(temp[2])
                if not(1 <= DD <= howManyDays):
                    return [False, date]
            else:
                return [False, date]
        else:
            return [False, date]
    else:
        return [False, date]
        
    return [True, date]
"""
    ====================
    End of verifications
    ====================
"""

def eventinput():
    """
        Creates an event with it's elements seperated by commas. Every element is verified
    """
    date = enterEventElement('Hμερομηνία γεγονότος: ', dateInputVerification, False)
    time = enterEventElement("Ώρα γεγονότος: ", timeInputVerification, False)
    dur = enterEventElement("Διάρκεια γεγονότος: ", durationInputVerification, False)
    title = enterEventElement("Τίτλος γεγονότος: ", titleInputVerification, False)
        
    return date + "," + time + "," + dur + "," + title
    
"""
    Calendar class
"""
class Calendar:
    def __init__(self, database: Database) -> None:
        self.month = datetime.datetime.now().month
        self.year = datetime.datetime.now().year
        self.database = database
        
        self.month_dict = {
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
    
    def getMonth(self):
        return self.month
    def getYear(self):
        return self.year
    
    def increaseMonth(self):
        "Increase's calendar's month caring for edge case where self.month==12"
        
        self.month += 1
        if self.month > 12:
            self.year += 1
            self.month = 1
    
    def decreaseMonth(self):
        "Decrease's calendar's month caring for the edge case where self.month==1"
        
        self.month -= 1
        if self.month <=0:
            self.month = 12
            self.year -= 1 
    
    def printEvents(self, year, month):
        "Prints all events of a specific month in a year"
        
        c = 0
        for i in self.database.data[month]:
            if i.get_year() == year:
                print(f"{c}. {i}")
                c += 1
        return c
    
    def printCalendar(self):
        "Prints calendar for one month"
        
        print("-"*47)
        print(self.month_dict[self.month],self.year, end='\n\n')
        print("-"*47)
        
        month_list = calendar.monthcalendar(self.year, self.month)

        prev_year = self.year
        prev_month = self.month
        if self.month == 1:
            prev_year -= 1
            prev_month = 12
        else:
            prev_month -= 1
        
        prev_month_range = calendar.monthrange(prev_year, prev_month)
        curr_month_range = calendar.monthrange(self.year, self.month)

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
                    date = str(self.year) + '-' + str(self.month) + '-' + str(month_list[w][i])
                    if self.database.dateHasEvent(date, self.month):
                        asterisk = '*'
                    week.append("%5s" % ('[' + ("%3s" % (asterisk + str(month_list[w][i]))) + ']'))
                else:
                    week.append("%5s"%(str(month_list[w][i])))
            print(' |'.join(week))

    def addEvent(self):
        """
        Adds an event and returns a list with the first element being the actual event and the second the status if the event is actually appended:
            list[1] == 1, event succesfully added to calendar
            list[1] == 2, event is overlapsed by other events and therefore not added
            list[1] == 3, event already exists and has not been added
        """
        event = Event(eventinput())
        return [event, self.database.add_event(event)]
    
    def deleteEvent(self, event):
        self.database.delete_event(Event(event))
    
    def printAvaiableHours(self, event: Event, ignore: Event = Event()):
        """
            Prints avaiable hours to add an event in a specific day. Utilises getAvaiableHours from Database class
        """
        l = self.database.getAvaiableHours(event, ignore)
        if len(l) == 0:
            return -1
        for timeSpace in l:
            print(timeSpace[0], '-',timeSpace[1])
        return 1


def printOptions():
        print('\n\tΠατήστε ENTER για προβολή του επόμενου μήνα, "q" για έξοδο ή κάποια από τις παρακάτω επιλογές:\n\
"-" για πλοήγηση στον προηγούμενο μήνα\n\
"+" για διαχείριση των γεγονότων του ημερολογίου\n\
"*" για εμφάνιση των γεγονότων ενός επιλεγμένου μήνα\n\
-> ', end='')

def printEventOptions():
    print('\n1 Καταγραφή νέου γεγονότος\n\
2 Διαγραφή γεγονότος\n\
3 Ενημέρωση γεγονότος\n\
0 Επιστροφή στο κυρίως μενού\n\
-> ', end='')

class UI:
    """
        Object containing a calendar that manages and organises all functionality with Handlers.
    """
    def __init__(self, calendar: Calendar) -> None:
        self.calendar = calendar
    
    def printCalendarHandler(self):
        self.calendar.printCalendar()
        
    def printEventsHandler(self, year, month):
        print("\nΓεγονότα για τον μήνα ", self.calendar.month_dict[month], year)
        c = self.calendar.printEvents(year, month)
        if c == 0:
            print("Κανένα καταγεγραμμένο γεγονός για αυτόν τον μήνα\n")
        print()
        return c
    
    def manageEvents(self):
        printEventOptions()
        match input():
            case '0':
                return
            case '1':
                self.addHandler()
            case '2':
                self.deleteHandler()
            case '3':
                self.updateHandler()

    def printPreviousMonth(self):
        self.calendar.decreaseMonth()
        self.printCalendarHandler()
    
    def printNextMonth(self):
        self.calendar.increaseMonth()
        self.printCalendarHandler()
    
    def addHandler(self):
        print("Εισαγωγή γεγονότος:")
        event_status = self.calendar.addEvent()
        while 2 <= event_status[1] <= 3:
            if event_status[1] == 3:
                print('Το γεγονός υπάρχει ήδη')
            if event_status[1] == 2:
                print("Το γεγονός σε αυτή την ώρα με αυτή την διάρκεια καλύπτεται από αλλά γεγονότα")
                print("Οι διαθέσιμες ώρες με αυτή την διάρκεια ειναί:")
                
                if self.calendar.printAvaiableHours(event_status[0]) == -1:
                    print("Δεν υπάρχουν διαθέσιμες ώρες την ημέρα αυτή για αυτό το γεγονός\n")
                    
            event_status = self.calendar.addEvent()
        

    def updateHandler(self):
        print("==== Αναζήτηση γεγονότων ====")
        year = enterYear()
        month = enterMonth()
        
        c = self.printEventsHandler(year, month)
        if c != 0:
            toUp = int(input("Επιλέξτε γεγονός προς ενημέρωση: "))
            while not (0 <= toUp <= c):
                print("Μη έγκυρη απάντηση.")
                toUp = int(input("Ποιό γεγονός θα θέλατε να ανανεώσετε: "))
            
            eventUpdate = self.calendar.database.data[month][toUp]
            
            new_date = enterEventElement(f"Ημερομηνία γεγονότος ( {eventUpdate.get_full_date()} ): ", dateInputVerification, True, eventUpdate.get_full_date())
            
            new_time = enterEventElement(f"Ώρα γεγονότος ({eventUpdate.get_time()})", timeInputVerification, True, eventUpdate.get_time())
            new_dur = enterEventElement(f"Διάρκεια γεγονότος ({eventUpdate.get_dur()}): ", durationInputVerification, True, eventUpdate.get_dur())
            
            temp = Event(f"{new_date},{new_time},{new_dur},{eventUpdate.get_title()}")
            
            actual_mod = True
            
            while self.calendar.database.doesOverlapseInSameDay(temp):
                if actual_mod:    
                    print("Το γεγονός σε αυτή την ώρα με αυτή την διάρκεια καλύπτεται από αλλά γεγονότα")
                    print("Οι διαθέσιμες ώρες με αυτή την διάρκεια ειναί:")
                    self.calendar.printAvaiableHours(temp, eventUpdate)
                    print()
                
                actual_mod = True
                c = int(input("Θέλετε να αλλάξετε την ώρα(1), την διάρκεια(2) ή και τα δύο(3); Μπορείτε να δείτε τις διαθέσιμες ώρες για μια συγκεκριμενη διάρκεια χώρις να την αλλάξετε με το 4. "))
                while not(1 <= c <= 4):
                    print('Παρακαλώ εισάγετε έναν αριθμό από το 1 ως το 3')
                    c = int(input("Θέλετε να αλλάξετε την ώρα(1), την διάρκεια(2) ή και τα δύο(3): "))
                    
                match c:
                    case 1:
                        new_time = enterEventElement(f"Ώρα γεγονότος ({eventUpdate.get_time()}): ", timeInputVerification, True, eventUpdate.get_time())
                    case 2:
                        new_dur = enterEventElement(f"Διάρκεια γεγονότος ({eventUpdate.get_dur()}): ", durationInputVerification, True, eventUpdate.get_dur())
                    case 3:
                        new_time = enterEventElement(f"Ώρα γεγονότος ({eventUpdate.get_time()}): ", timeInputVerification, True, eventUpdate.get_time())
                        new_dur = enterEventElement(f"Διάρκεια γεγονότος ({eventUpdate.get_dur()}): ", durationInputVerification, True, eventUpdate.get_dur())
                    case 4:
                        temp_dur = enterEventElement(f"Διάρκεια γεγονότος ({eventUpdate.get_dur()}): ", durationInputVerification, True, eventUpdate.get_dur())
                        temp2 = Event(f"{new_date},{eventUpdate.get_time()},{temp_dur},{eventUpdate.get_title()}")
                        print("Οι διαθέσιμες ώρες του γεγονότος με δοκιμαστική διάρκεια είναι:")
                        self.calendar.printAvaiableHours(temp2, eventUpdate)
                        actual_mod = False
                if actual_mod:
                    temp = Event(f"{new_date},{new_time},{new_dur},{eventUpdate.get_title()}")
            
            new_title = enterEventElement(f"Τίτλος γεγονότος ({eventUpdate.get_title()}): ", titleInputVerification, True, eventUpdate.get_title())
            
            self.calendar.database.update_event(month, toUp, new_date, new_time, str(new_dur), new_title)
            print(f'Το γεγονός ενημερώθηκε: <{self.calendar.database.data[month][toUp]}>')
                
    
    def deleteHandler(self):
        print("=== Αναζήτηση γεγονότων ====")
        year = enterYear()
        month = enterMonth()
        c = self.printEventsHandler(year, month)
        if c != 0:
            todel = int(input("Ποιό γεγονός θα θέλατε να διαγράψετε; "))
            while todel not in range(c + 1):
                print("Μη έγκυρη απάντηση!")
                todel = int(input("Ποιό γεγονός θα θέλατε να διαγράψετε; "))
            flag = False
            print("Είστε σίγουροι οτι θέλετε να διαγράψετε το συγκεκριμένο γεγονός;\
                Μόλις διαγραφεί το γεγονός δεν υπάρχει τρόπος να το επαναφέρετε.")
            yon = input("Ν για Ναι/Ο για Όχι: ")
            while yon != "N" and yon != "O":
                print("Μη έγκυρη απάντηση!")
                print("Είστε σίγουροι οτι θέλετε να διαγράψετε το συγκεκριμένο γεγονός;\n \
Μόλις διαγραφεί το γεγονός δεν υπάρχει τρόπος να το επαναφέρετε.\n")
                yon = input("Ν για Ναι/Ο για Όχι ")
            if yon == "N":
                flag = True
            if flag == True:
                self.calendar.database.delete_event(self.calendar.database.data[month][todel])
        
    def save(self):
        self.calendar.database.save()

def printEventsForToday(ui: UI):
    current_time = datetime.datetime.now()
    CurDate = str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day)
    TodayEvents = ui.calendar.database.findEventsInDay(CurDate, current_time.month, current_time.day)
    if len(TodayEvents) == 0:
        print("Δέν υπάρχουν γεγονότα σήμερα.")
    else:
        cur_timedelta = datetime.timedelta(hours = current_time.timetz().hour, minutes = current_time.timetz().minute)
        distance = min([(x.get_timedeltaBegin() - cur_timedelta) for x in TodayEvents if (x.get_timedeltaBegin() > cur_timedelta)])
        print("Next event in EST: " + str(distance))
    

if __name__ == "__main__":
    d = Database("events.csv")
    c = Calendar(d)
    ui = UI(c)

    current_time = datetime.datetime.now()
    CurDate = str(current_time.year) + "-" + str(current_time.month) + "-" + str(current_time.day)
    printEventsForToday(ui)
    
    printCalendar = True
    while True:
        if printCalendar:
            ui.printCalendarHandler()
        printOptions()
        printCalendar = True
        
        match input():
            case '-':
                ui.printPreviousMonth()
                printCalendar = False
            case '':
                ui.printNextMonth()
                printCalendar = False
            case '+':
                ui.manageEvents()
            case '*':
                ui.printEventsHandler(enterYear(), enterMonth())
            case 'q':
                ui.save()
                break
