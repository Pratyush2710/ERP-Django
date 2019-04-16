from django.shortcuts import render
from notifications.signals import notify

# Create your views here.

def leave_module_notif(sender, recipient, type):
    url = 'leave:leave'
    module = 'Leave Module'
    sender=sender
    recipient=recipient
    verb=''
    if type=='leave_applied':
        verb="Your leave has been successfully submitted."
    if type=='request_accepted':
        verb = "Your responsibility has been accepted "
    if type=='request_declined':
        verb = "Your responsibility has been declined "
    if type=='leave_accepted':
        verb = "You leave request has been accepted "
    if type == 'leave_forwarded':
        verb = "You leave request has been forwarded "
    if type=='leave_rejected':
        verb = "You leave request has been rejected "
    if type=='offline_leave':
        verb = "Your offline leave has been updated "
    if type=='replacement_request':
        verb = "You have a replacement request "


    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def placement_cell_notif(sender, recipient, type):
    url = ''
    module = 'Placement Cell'
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def academics_module_notif(sender, recipient, type):
    url=''
    module="Academic's Module"
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def central_mess_notif(sender, recipient, type):
    url='mess:mess'
    module='Central Mess'
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def visitors_hostel_notif(sender, recipient, type):
    url=''
    module="Visitor's Hostel"
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def healthcare_center_notif(sender, recipient, type):
    url=''
    module='Healthcare Center'
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def file_tracking_notif(sender, recipient, type):
    url=''
    module='File Tracking'
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def scholarship_portal_notif(sender, recipient, type):
    url=''
    module='Scholarship Portal'
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def complaint_system_notif(sender, recipient, type):
    url=''
    module='Complaint System'
    sender = sender
    recipient = recipient
    verb = ''

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

def office_module_DeanS_notif(sender, recipient, type):
    url='office:officeOfDeanStudents'
    module='Office Module'
    sender = sender
    recipient = recipient
    verb = ""

    if type == 'hostel_alloted':
        verb = "Hostel has been alloted successfully."
    elif type == 'insufficient_funds':
        verb = "Insufficient Funds! Please contact Junior Superintendent to allot funds."
    elif type == 'MOM_submitted':
        verb = "MOM of the meeting has been submitted successfully."
    elif type == 'budget_approved':
        verb = "Budget has been approved by Dean Students."
    elif type == 'budget_rejected':
        verb = "Budget has been rejected by Dean Students."
    elif type == 'club_approved':
        verb = "New Club has been approved by Dean Students."
    elif type == 'club_rejected':
        verb = "New Club has been rejected by Dean Students."
    elif type == 'meeting_booked':
        verb = "Meeting has been booked and members has been notified"
    elif type == 'session_approved':
        verb = "Club session has been approved"
    elif type == 'session_rejected':
        verb = "Club session has been rejected."
    elif type == 'budget_alloted':
        verb = "Budget has been alloted by Junior Superintendent"

    notify.send(sender=sender, recipient=recipient, url=url, module=module, verb=verb)

