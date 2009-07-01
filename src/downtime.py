import time

class Downtime:
    id = 0

    #Schedules downtime for a specified service. If the "fixed" argument is set to one (1),
    #downtime will start and end at the times specified by the "start" and "end" arguments.
    #Otherwise, downtime will begin between the "start" and "end" times and last for "duration"
    #seconds. The "start" and "end" arguments are specified in time_t format (seconds since
    #the UNIX epoch). The specified service downtime can be triggered by another downtime
    #entry if the "trigger_id" is set to the ID of another scheduled downtime entry.
    #Set the "trigger_id" argument to zero (0) if the downtime for the specified service
    #should not be triggered by another downtime entry.
    def __init__(self, ref, start_time, end_time, fixed, trigger_downtime, duration, author, comment):
        self.id = self.__class__.id
        self.__class__.id += 1
        self.ref = ref #pointer to srv or host we are apply
        self.trigger_me = [] #The trigger i need to activate
        self.start_time = start_time
        if fixed:
            self.end_time = end_time
        else:
            self.end_time = self.start_time + duration
        if trigger_downtime is not None:
            trigger_downtime.trigger_me(self)
        self.author = author
        self.comment = comment


    def trigger_me(self, other_downtime):
        self.active_me.append(other_downtime)


    def is_in_downtime(self):
        now = time.time()
        return self.start_time <= now <= self.end_time
