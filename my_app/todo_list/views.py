from django.shortcuts import render
from .models import List
from django.contrib import messages
from .key import keyToken

import json
import requests

def studentData(id):
    headers = {
        'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/students/'+id, headers=headers)
    
    # converts to python dict
    return json.loads(response.content)

def mbClasses():
    headers = {
        'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/classes?archived=true', headers=headers)
    
    # converts to python dict
    return json.loads(response.content)


def academicYears():
    headers = {
    'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/school/academic-years', headers=headers)

    return json.loads(response.content)


def studentClasses(id,archived):
    if not archived:
        archived = 'false'
    headers = {
    'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/students/'+id+'/memberships?archived='+archived, headers=headers)

    return json.loads(response.content)

def allClasses(archived):
    headers = {
    'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/classes?archived='+archived, headers=headers)

    return json.loads(response.content)
    

def classTermGrades(classId,termId):
    headers = {
    'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/classes/'+classId+'/assessments/term/'+termId+'/term-grades?include_archived_students=true', headers=headers)

    return json.loads(response.content)


def home(request):
    
    return render(request,'home.html',{'mbClasses' : mbClasses()['classes']})

    from .classroomList import main
    global courses
    courses = main()

    return render(request,'home.html',{'mbClasses' : courses})


def about(request):
    my_name ="Nick"
    return render(request,'about.html',{'name' : my_name})



def search(request):
    
    if request.method == 'POST' and len(request.POST['item'])>0:
        filterTerm = request.POST['item']
        filteredList = []

        for classes in mbClasses()["classes"]:
            if filterTerm in classes['name']:
                filteredList.append({'name':classes['name']})

        messages.success(request,('Courses containing '+filterTerm))
        return render(request,'home.html',{'mbClasses()' : filteredList})
    
    return render(request,'home.html',{'mbClasses' : mbClasses()['classes']})

def student(request):
    
    if request.method == 'POST':
        id = request.POST['studentID']
        mypyears = []
        dpyears = []
        #returns array of class objects
        all_archived_Classes=allClasses('true')["classes"]
        all_active_Classes=allClasses('false')["classes"]
        all_Classes=all_archived_Classes+all_active_Classes

        studentObject = studentData(id)["student"]
        studentStart = studentObject["created_at"]
        
        archived_student_Classes = studentClasses(id,'true')["memberships"]["classes"]
        current_student_Classes = studentClasses(id,'false')["memberships"]["classes"]
        all_student_classes=archived_student_Classes+current_student_Classes
        # termID = 168734
        mypyearsData = academicYears()["academic_years"]["myp"]["academic_years"]
        dpyearsData = academicYears()["academic_years"]["diploma"]["academic_years"]

        for year in mypyearsData:
            hasyearGrades = False
            terms = []
            if int(year["starts_on"][0:4]) >= int(studentStart[0:4]):
                for term in year["academic_terms"]:               
                    transcriptData = []
                    hasGrade = False
                    for classes in all_student_classes:
                        classGrades = classTermGrades(str(classes['id']),str(term['id']))
                        try:
                            for student in classGrades["students"]:
                                if student['id'] == int(id) and student['term_grade']['grade']!=None:
                                    hasGrade = True
                                    i=0
                                    while classes['id'] != all_Classes[i]['id'] and i+1<len(all_Classes):
                                        i=i+1
                                    transcriptData.append({'classData':all_Classes[i],'grade':student['term_grade']['grade']})
                        except:
                            print("oops")
                    if hasGrade:
                        terms.append({'termID':term['id'], 'termName':term['name'], 'classGrades':transcriptData})
                        hasyearGrades = True
                if hasyearGrades:
                    mypyears.append({'yearName':year["name"],'terms':terms})
        
        for year in dpyearsData:
            hasyearGrades = False
            terms = []
            #only checks in years since student joined
            if int(year["starts_on"][0:4]) >= int(studentStart[0:4]):
                for term in year["academic_terms"]:               
                    transcriptData = []
                    hasGrade = False
                    for classes in all_student_classes:
                        classGrades = classTermGrades(str(classes['id']),str(term['id']))
                        try:
                            for student in classGrades["students"]:
                                if student['id'] == int(id) and student['term_grade']['grade']!=None:
                                    hasGrade = True
                                    i=0
                                    while classes['id'] != all_Classes[i]['id']:
                                        i=i+1
                                    transcriptData.append({'classData':all_Classes[i],'grade':student['term_grade']['grade']})
                        except:
                            print("oops")
                    if hasGrade:
                        terms.append({'termID':term['id'], 'termName':term['name'], 'classGrades':transcriptData})
                        hasyearGrades = True
                if hasyearGrades:
                    dpyears.append({'yearName':year["name"],'terms':terms})

        years = [mypyears, dpyears]    
        
        messages.success(request,('Student Classes'))
        return render(request,'student.html',{'years' : years,'student': studentObject})
    
    return render(request,'student.html')


#sort items alphabetically
def sortAlpha(request):
    
        sorted_items = List.objects.order_by('item')
        return render(request,'home.html',{'all_items' : sorted_items})

#sort items alphabetically
def filterDone(request,state):
    filterSwitch = ''
    if state == 'done':
        filterSwitch = True
    else:
        filterSwitch = False
    filtered_items = List.objects.filter(completed=filterSwitch)
    return render(request,'home.html',{'all_items' : filtered_items})

# def delete(request, list_id):
#     item = List.objects.get(pk=list_id)
#     item.delete()
#     messages.success(request,('Item deleted'))
#     return redirect('home')

# def cross_off(request, list_id):
#     item = List.objects.get(pk=list_id)
#     item.completed = True
#     item.save()
#     return redirect('home')

# def uncross(request, list_id):
#     item = List.objects.get(pk=list_id)
#     item.completed = False
#     item.save()
#     return redirect('home')

# def edit(request,list_id):

#     if request.method == 'POST':
#         item = List.objects.get(pk=list_id)

#         form = ListForm(request.POST or None, instance=item)

#         if form.is_valid():
#             form.save()
#             messages.success(request,('Item edited'))
#             return redirect('home')

#     else:

#         item = List.objects.get(pk=list_id)
#         return render(request,'edit.html',{'item' : item})