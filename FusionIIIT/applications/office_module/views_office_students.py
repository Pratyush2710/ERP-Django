from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from applications.academic_information.models import Meeting
from .models import Constants, hostel_allotment, Budget, hostel_capacity
from applications.gymkhana.models import Club_budget, Club_info, Session_info
from applications.globals.models import *
import json
from django.contrib.auth.decorators import login_required
import datetime, time
from notification.views import office_module_DeanS_notif
from django.views.decorators.csrf import csrf_protect

"""
    Default view for Dean Students Module
    All models are Loaded from respective Tables in Database and passed to default template
    List of Concerned Models :
    S.no. Model             |  Load Variables  |  Usage

    1.    Club_budget       |  budget_app      |  Budget reuests where status is open
                            |  past_budget     |  Past budget requests
                            |  approved_budgets|  Budget requests marked as approved
    2.    Meeting           |  minutes         |  Meeting entries where minutes file is not present
                            |  final_minutes   |  Meeting entries where minute file is present
    3.    hostel_allotment  |  hall_allotment  |  All entries
    4.    Club_info         |  clubNew         |  Clubs which are not approved/rejected
                            |  club            |  Clubs which are approved/rejected
                            |  budgets         |  Clubs which are approved
    5.    HoldsDesignation  |  designation     |  Designation of the active user
"""


def getUniversalContext(request, page, err_msg='none', success_msg='none', flag_dean_s=False,
                        flag_superintendent=False):
    budget_app = Club_budget.objects.all().filter(status='open')
    past_budget = Club_budget.objects.all().exclude(status='open')
    minutes = Meeting.objects.all().filter(minutes_file="")
    final_minutes = Meeting.objects.all().exclude(minutes_file="")
    hall_allotment = hostel_allotment.objects.all()
    clubNew = Club_info.objects.all().filter(status='open')
    session_requests_new = Session_info.objects.all().filter(status='open')
    session_requests = Session_info.objects.all().exclude(status='open')
    club = Club_info.objects.all().exclude(status='open')
    budgets = Club_info.objects.all().filter(status='confirmed')
    approved_budgets = Club_budget.objects.all().filter(status='confirmed')
    budget_allotment = Club_info.objects.all().filter(alloted_budget=0, status="confirmed")
    budget_alloted = Club_info.objects.all().exclude(alloted_budget=0)
    designation = HoldsDesignation.objects.all().filter(working=request.user)
    CAPACITY = hostel_capacity.objects.all()

    # getting roll and designation(s) of the active user in roll_
    desig = list(HoldsDesignation.objects.all().filter(working=request.user).values_list('designation'))
    b = [i for sub in desig for i in sub]
    roll_ = []
    for i in b:
        name_ = get_object_or_404(Designation, id=i)
        roll_.append(str(name_.name))

    # getting hostel allotment entries corresponding to each Hall
    HALL_NO = ['HALL-1-BOYS', 'HALL-1-GIRLS', 'HALL-3', 'HALL-4']
    PROGRAM = ['BTECH', 'BDES', 'MTECH', 'MDES', 'PHD']
    YEARS = ['FIRST-YEAR', 'SECOND-YEAR', 'THIRD-YEAR', 'FOURTH-YEAR']
    GENDER = ['MALE', 'FEMALE']

    context = {'meetingMinutes': minutes,
               'final_minutes': final_minutes,
               'hall': HALL_NO,
               'program': PROGRAM,
               'years': YEARS,
               'gender': GENDER,
               'capacity': CAPACITY,
               'hall_allotment': hall_allotment,
               'budget_app': budget_app,
               'p_budget': past_budget,
               'clubNew': clubNew,
               'session_requests': session_requests,
               'session_requests_new': session_requests_new,
               'club': club,
               'budgets': budgets,
               'approved_budgets': approved_budgets,
               'budget_allotment': budget_allotment,
               'budget_alloted': budget_alloted,
               'all_designation': roll_,
               'page': page,
               'err_msg': err_msg,
               'success_msg': success_msg,
               'flag_dean_s': flag_dean_s,
               'flag_superintendent': flag_superintendent,
               }
    return context


@login_required
def officeOfDeanStudents(request):
    # getting roll and designation(s) of the active user in roll_
    desig = list(HoldsDesignation.objects.all().filter(working=request.user).values_list('designation'))
    b = [i for sub in desig for i in sub]
    roll_ = []
    for i in b:
        name_ = get_object_or_404(Designation, id=i)
        roll_.append(str(name_.name))
    page = 0
    flag_dean_s = False
    flag_superintendent = False
    if 'Dean_s' in roll_:
        page = 0
        flag_dean_s = True
    elif 'Junior Superintendent' in roll_:
        page = 6
        flag_superintendent = True
    return render(request, "officeModule/officeOfDeanStudents/officeOfDeanStudents.html",
                  getUniversalContext(request, page=page, flag_dean_s=flag_dean_s,
                                      flag_superintendent=flag_superintendent))


"""
    View for the meeting being called by Dean_Student
    Inputs:- Agenda, Date, Time, Venue, Minutes_File
        (*) Minutes file is to be added by JuniorSuprintendent
    An object holdMeeting object is being created and accessed in the holding_form.html template. 
"""


@login_required
def holdingMeeting(request):
    err_msg = 'none'
    success_msg = 'none'
    """getting input form data from POST request"""
    date = request.POST.get('date')
    Time = request.POST.get('time')
    Venue = request.POST.get('venue')
    Agenda = request.POST.get('agenda')
    time_diff = 0

    if date == '':
        err_msg = 'Date is required'
    elif Time == '':
        err_msg = 'Time is required'
    elif Venue == '':
        err_msg = 'Venue is required'
    elif Agenda == '':
        err_msg = 'Agenda is required'
    elif date == None:
        err_msg = 'none'
    else:
        curr = datetime.datetime.now().timestamp()
        given = datetime.datetime.strptime(date + " " + Time, '%Y-%m-%d %H:%M').timestamp()
        time_diff = given - curr
        if time_diff < 0:
            err_msg = "Back Date and Time not allowed."
        else:
            """inserting a new record with these values in database"""
            p = Meeting(venue=Venue, date=date, time=Time, agenda=Agenda)
            p.save()
            success_msg = "Meeting created successfully. Waiting for Suprintendent for the MOM"

    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=1, success_msg=success_msg, err_msg=err_msg))


"""
    View for the minutes of the meeting initiated by the Junior Suprintendent
    Inputs:- file
        (*) Minutes file is to be added by JuniorSuprintendent
    An object meeting_object saves the file 
"""


@login_required
def meetingMinutes(request):
    err_msg = 'none'
    success_msg = 'none'
    if 'minutes_file' not in request.FILES:
        err_msg = "none"
    else:
        file = request.FILES['minutes_file']
        id = request.POST.get('id')
        meeting_object = Meeting.objects.get(pk=int(id))
        meeting_object.minutes_file = file
        meeting_object.save()
        success_msg = "MOM uploaded successfully"
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=6, success_msg=success_msg, err_msg=err_msg))


@login_required
def hostelRoomAllotment(request):
    err_msg = 'none'
    success_msg = 'none'
    hall_no = request.POST.get('hall_no')
    year = request.POST.get('year')
    gender = request.POST.get('gender')
    num_students = request.POST.get('num_students')
    remarks = request.POST.get('remarks')
    program = request.POST.get('program')

    if hall_no == None:
        err_msg = 'none'
    if hall_no == '':
        err_msg = 'Hall No. is required'
    elif year == '':
        err_msg = 'Year is required'
    elif gender == '':
        err_msg = 'Gender is required'
    elif num_students == '':
        err_msg = 'No. of Students is required'
    elif program == '':
        err_msg = 'Program is required'
    elif hall_no == 'HALL-1-GIRLS' and gender == 'MALE':
        err_msg = 'Boys cannont reside in ' + hall_no
    elif gender == 'FEMALE' and hall_no != 'HALL-1-GIRLS':
        err_msg = 'Girls cannot reside in ' + hall_no
    else:
        print("hall no obtained : ", hall_no)

        # changing the capacity
        capacity = hostel_capacity.objects.get(name=hall_no)
        if (int(capacity.current_capacity) - int(num_students)) >= 0:
            # saving the new allotment
            p = hostel_allotment(hall_no=hall_no, year=year, gender=gender, number_students=num_students,
                                 remark=remarks, program=program)
            p.save()
            capacity.current_capacity = int(capacity.current_capacity) - int(num_students)
            capacity.save()
            success_msg = 'Hall Alloted Successfully'
            office_module_DeanS_notif(request.user, request.user, 'hostel_alloted')
        else:
            err_msg = 'Hostel Limit Exceeded!'
    print("error msg : " + err_msg)
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=7, err_msg=err_msg, success_msg=success_msg))


@login_required
def deleteHostelRoomAllotment(request):
    id = request.POST.get('delete')
    print("Delete record: ", id)
    hall_no = hostel_allotment.objects.get(id=id).hall_no
    num_students = hostel_allotment.objects.get(id=id).number_students

    capacity = hostel_capacity.objects.get(name=hall_no)
    if (int(capacity.current_capacity) + int(num_students)) <= capacity.total_capacity:
        capacity.current_capacity = int(capacity.current_capacity) + int(num_students)
    else:
        capacity.current_capacity = capacity.total_capacity
    capacity.save()

    hostel_allotment.objects.get(id=id).delete()
    success_msg = 'Hostel Allotment Deleted Successfully'
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=7, success_msg=success_msg))


@login_required
def deleteAllHostelRoomAllotment(request):
    # deleting all allotments
    hostel_allotment.objects.all().delete()

    # resetting capacities to max
    capacity = hostel_capacity.objects.all()
    for item in capacity:
        item.current_capacity = item.total_capacity
        item.save()

    success_msg = 'All Allotments Deleted Successfully'
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=7, success_msg=success_msg))


@login_required
def budgetApproval(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.getlist('check')
    remark = request.POST.getlist('remark')
    for i in range(len(id_r)):

        Club_budget_object = Club_budget.objects.get(id=id_r[i])
        avail_budget = Club_info.objects.get(club_name=Club_budget_object.club_id)
        Club_budget_object.status = 'confirmed'
        Club_budget_object.remarks = request.POST.get(id_r[i])
        budget = request.POST.get('amount ' + id_r[i])
        if int(budget) > avail_budget.avail_budget:
            err_msg = "Insufficient fund. Ask suprintendent to update total allotment"
        else:
            Club_info_object = Club_info.objects.get(club_name=Club_budget_object.club.club_name)
            Club_info_object.spent_budget = int(budget) - Club_info_object.spent_budget  # (spentBudget + int(budget))
            Club_info_object.avail_budget = Club_info_object.avail_budget - int(budget)  # (availBudget - int(budget))
            Club_budget_object.save()
            Club_info_object.save()
            success_msg = "Club Budget approved succesfully"
            office_module_DeanS_notif(request.user, request.user, 'budget_approved')
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=2, success_msg=success_msg, err_msg=err_msg))


@login_required
def budgetRejection(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.getlist('check')
    remark = request.POST.getlist('remark')
    for i in range(len(id_r)):
        Club_budget_object = Club_budget.objects.get(id=id_r[i])
        Club_budget_object.status = 'rejected'
        Club_budget_object.remarks = request.POST.get(id_r[i])
        Club_budget_object.save()
        success_msg = "Club Budget rejected successfully"
        office_module_DeanS_notif(request.user, request.user, 'budget_rejected')
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=2, success_msg=success_msg))


"""
    View for club Approval initiated by the Dean_S
    Inputs:- Club name, coordinator, cocoordinator details, designation
    Output :- Updates the club approval status to approved        
    An object Club_info_object is created and accessed in newClubApprovalsModal.html 
"""


@login_required
def clubApproval(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.getlist('check')
    """changing club approval status from open to confirmed and added to the field"""
    for i in range(len(id_r)):
        Club_info_object = Club_info.objects.get(pk=id_r[i])
        co_ordinator = Club_info_object.co_ordinator.id.user
        co_co = Club_info_object.co_coordinator.id.user
        Club_info_object.status = 'confirmed'
        Club_info_object.save()
        designation = get_object_or_404(Designation, name="co-ordinator")
        designation1 = get_object_or_404(Designation, name="co co-ordinator")
        HoldsDesig = HoldsDesignation(user=co_ordinator, working=co_ordinator, designation=designation)
        HoldsDesig.save()
        HoldsDesig = HoldsDesignation(user=co_co, working=co_co, designation=designation1)
        HoldsDesig.save()
        success_msg = "Club Approved successfully"
        office_module_DeanS_notif(request.user, request.user, 'club_approved')
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=5, success_msg=success_msg))


"""
    View for club Rejection initiated by the Dean_S
    Inputs:- All the budgets in open state
    Output :- Updates the club approval status to rejected        
    An object Club_info_object is created and accessed in newClubApprovalsModal.html 
"""


@login_required
def clubRejection(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.getlist('check')
    for i in range(len(id_r)):
        Club_info_object = Club_info.objects.get(pk=id_r[i])
        Club_info_object.status = 'rejected'
        Club_info_object.save()
        err_msg = "Club Rejected successfully"
        office_module_DeanS_notif(request.user, request.user, 'club_rejected')
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=5, err_msg=err_msg))


@login_required
def sessionApproval(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.getlist('check')
    for i in range(len(id_r)):
        Session_info_object = Session_info.objects.get(pk=id_r[i])
        venue = Session_info_object.venue
        date = Session_info_object.date
        Session_info_object.status = 'confirmed'
        Session_info_object.save()
    success_msg = "Club Session approved succesfully"
    office_module_DeanS_notif(request.user, request.user, 'session_approved')
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=11, success_msg=success_msg))


@login_required
def sessionRejection(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.getlist('check')
    for i in range(len(id_r)):
        Session_info_object = Session_info.objects.get(pk=id_r[i]);
        Session_info_object.status = 'rejected'
        Session_info_object.save()
    success_msg = "Club Session rejected successfully"
    office_module_DeanS_notif(request.user, request.user, 'session_rejected')

    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=11, success_msg=success_msg))


"""
    View for allotment of budget initiated by the Dean_S
    Inputs:- Unique id for club, budget object
    Outputs:- Alloted budget, availed budget
    An object Club_info_object saves the file and accessed in budgetAllotmentModal.html
"""


@login_required
def budgetAllot(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.get('id')
    budget = request.POST.get('budget')
    if id_r == None:
        err_msg = 'none'
    else:
        Club_info_object = Club_info.objects.get(pk=id_r)
        Club_info_object.alloted_budget = int(budget)
        Club_info_object.avail_budget = int(budget)
        Club_info_object.save()
        success_msg = "Budget alloted successfully"
    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=10, success_msg=success_msg))


"""
    View for the budgetALlotEdit initiated by the Junior Suprintendent
    Output: club alloted budget, availed budget, spent budget
    An object Club_info_object saves the file and is accessed in budgetAllotmentModal.html 
"""


@login_required
def budgetAllotEdit(request):
    err_msg = 'none'
    success_msg = 'none'
    id_r = request.POST.get('id')
    budget = request.POST.get('budget')
    if id_r == None:
        err_msg = 'none'
    else:
        Club_info_object = Club_info.objects.get(pk=id_r)
        if int(budget) < Club_info_object.spent_budget:
            err_msg = "Cannot reduce below spent budget"
        else:
            Club_info_object.alloted_budget = int(budget)
            Club_info_object.avail_budget = int(budget) - Club_info_object.spent_budget
            # Club_info_object.spent_budget = int(0)
            success_msg = "Budget alloted successfully"
            Club_info_object.save()

    return render(request, 'officeModule/officeOfDeanStudents/officeOfDeanStudents.html',
                  getUniversalContext(request, page=10, err_msg=err_msg, success_msg=success_msg))
