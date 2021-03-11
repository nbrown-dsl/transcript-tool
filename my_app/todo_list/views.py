from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import login,logout,authenticate
from django.http import HttpResponseRedirect, HttpResponse
# module to read string from entity list as class name
import sys
from django.core.mail import send_mail
from django.conf import settings


def str_to_class(classname):
    return getattr(sys.modules[__name__], classname)

# Create your views here.
def home(request,nameFilter=""):
    #if from filter form
    all_items = taskdata.objects.all()
    #for populating dropdown menus
    protocols = protocol.objects.all()
    people = persons.objects.all()
    protocoltypeObjects = protocoltype.objects.all()

    #form filter form request from form post, cumalatively builds up filter queryset
    if request.method == 'POST':
        
        form = filterForm(request.POST or None)
        if form.is_valid():
            protocolName = form.cleaned_data['protocols']
            if str(protocolName) != "All protocols":
                all_items = all_items.filter(protocol__forename__contains=protocolName)
            personName = form.cleaned_data['person']
            if str(personName) != "All people":
                all_items = all_items.filter(task__person__name__contains=personName)
            protocolTypeName = form.cleaned_data['protocolType']
            if str(protocolTypeName) != "All types":
                all_items = all_items.filter(protocol__type__protocolTypeName__contains=protocolTypeName)
            
            messages.success(request,('Filtered'))
    
    else:
        #if request from email link with name filter or from 'clear' button 
        if nameFilter:
            if nameFilter != "clear":
                name = nameFilter
                all_items = all_items.filter(task__person__name__contains=name)
            else:
                name = "All people"            
            try:
                allpeople = persons.objects.get(name=name)
                peopleFilter = allpeople.id
            except persons.DoesNotExist:
                peopleFilter = 1
        else:
            try:
                allpeople = persons.objects.get(name="All people")
                peopleFilter = allpeople.id
            except protocoltype.DoesNotExist:
                peopleFilter = 1    
        try:
            allprotocolType = protocoltype.objects.get(protocolTypeName="All types")
            protocolTypeFilter = allprotocolType.id
        except protocoltype.DoesNotExist:
            protocolTypeFilter = 1
        try:
            allprotocol = protocol.objects.get(forename="All protocols")
            protocolFilter = allprotocol.id
        except protocol.DoesNotExist:
            protocolFilter = 1
        form = filterForm({'person':peopleFilter,'protocols':protocolFilter, 'protocolType':protocolTypeFilter})  
    
    all_items = all_items.order_by('protocol')

    #compile comma separated string of emails of those people who have tasks incomplete on selected items
    incompleteTasks = all_items.filter(completed=False)
    emails = ""
    links = ""
    for taskdataRecord in incompleteTasks:
        email = taskdataRecord.task.person.email
        if email not in emails:
            emails=emails+email+"," 
            username = email.split("@")[0]       
            links = links + "<a href=\'https://dwight-london-protocols.herokuapp.com/home/" + username + "\' target=\'_blank\'>" + username + "</a><br>"

          
    return render(request,'home.html',{'all_items' : all_items,'people' : people,'protocoltype':protocoltypeObjects,'protocols':protocols, 'filterForm': form,'emails': emails, 'links': links})

def protocolAdd(request,type):
    typeObject = protocoltype.objects.get(pk=type) 

    if request.method == 'POST':
        form = ListForm(request.POST or None)
        if form.is_valid():
            form.save()
            newprotocol = form.instance
            tasks = task.objects.filter(protocolType = typeObject)
            for protocoltask in tasks:
                newTask = taskdata(task=protocoltask,protocol=newprotocol)
                newTask.save()
            messages.success(request,('Protocol created'))
        else:
            messages.success(request,(form.errors))
        return redirect('home')
    else: 
        newProtocol = protocol()
        newProtocol.type = typeObject 
        form = ListForm(instance=newProtocol)
        removeFields(form,newProtocol)        
        protocoltypeName = typeObject.protocolTypeName
        return render(request,'protocolAdd.html',{'form' : form, 'protocoltype' : protocoltypeName})

def about(request):
    my_name ="Nick"
    return render(request,'about.html',{'name' : my_name})

def delete(request, list_id):
    item = protocol.objects.get(pk=list_id)
    item.delete()
    messages.success(request,('item deleted'))
    return redirect('home')

def crossoff(request, list_id):
    item = taskdata.objects.get(pk=list_id)
    item.completed = True
    item.save()
    messages.success(request,('Task complete')) 
    #trying to load same page with same data (ie same filters) but seems ot same as redirect to home def  
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#from ajax javascript call
def cross(request):
        if request.method == 'GET':
               post_id = request.GET['post_id']
               item = taskdata.objects.get(pk=post_id) #getting the liked posts
               if item.completed:
                   item.completed = False
               else:
                   item.completed = True
               item.save()
               return HttpResponse("Success!") # Sending an success response
        else:
               return HttpResponse("Request method is not a GET")


def uncross(request, list_id):
    item = taskdata.objects.get(pk=list_id)
    item.completed = False
    item.save()
    messages.success(request,('Task uncomplete')) 
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#view for editing or adding items
def edit(request,list_id):
    
#if request received from edit form submission
    if request.method == 'POST':
        #checks if form submission is from pre-existing item on list
        try:
            item = protocol.objects.get(pk=list_id)        
            form = ListForm(request.POST or None, instance=item)
            message="Item edited"
        #if is new item
        except:
            form = ListForm(request.POST or None)
            message="Item added"
            
        if form.is_valid():
            form.save()    
        
        #if form invalid
        else:
            message = 'Invalid form'

        messages.success(request,(message))
        return redirect('home')

#if request received from edit icon by item on home page list or add button
    else:
        #if item on list
        if list_id != '0':
            item = protocol.objects.get(pk=list_id)
            form = ListForm(request.POST or None, instance=item)
            removeFields(form,item)
            return render(request,'edit.html',{'form' : form, 'item' : item})
        #if request received from 'add' button on home page (passes id as 0)
        else:
            form = ListForm()
            return render(request,'edit.html',{'form' : form})


#view for editing or adding records in entities (eg persons, protocol types, tasks) 
# (this is very simliar code to def edit and so should be way to pass parameter to def than determines which form is run)
def entityForm(request,list_id,modelName):
    
#if request received from edit form submission
    if request.method == 'POST':
        #checks if form submission is from pre-existing record in model
        if modelName == 'persons':
            if list_id and list_id != "noId":
                item = persons.objects.get(pk=list_id)        
                form = personsForm(request.POST or None, instance=item)
                message="Person edited"
            #if is new item
            else:
                form = personsForm(request.POST or None)
                message="Person added"
            model = persons.objects.all

        elif modelName == 'protocoltype' or modelName == 'Protocol type':
            if list_id and list_id != "noId":
                item = protocoltype.objects.get(pk=list_id)        
                form = protocolTypeForm(request.POST or None, instance=item)
                message="protocl type edited"
            #if is new item
            else:
                form = protocolTypeForm(request.POST or None)
                message="protocol type added"
            model = protocoltype.objects.all

        elif modelName == 'task' or modelName == 'tasks':
            if list_id and list_id != "noId":
                item = task.objects.get(pk=list_id)        
                form = taskForm(request.POST or None, instance=item)
                message="task edited"
            #if is new item
            else:
                form = taskForm(request.POST or None)
                message="task added"
            model = task.objects.all

        elif modelName == 'protocol' or modelName == 'protocols':
            if list_id and list_id != "noId":
                item = protocol.objects.get(pk=list_id)        
                form = ListForm(request.POST or None, instance=item)
                message="protocol edited"
            #if is new item
            else:
                form = ListForm(request.POST or None)
                message="protocol added"
            model = protocol.objects.all
        
        elif modelName == 'ListFields':
            if list_id and list_id != "noId":
                item = ListFields.objects.get(pk=list_id)        
                form = fieldForm(request.POST or None, instance=item)
                message="field edited"
            #if is new item
            else:
                form = fieldForm(request.POST or None)
                message="field added"
            model = ListFields.objects.all
            
        if form.is_valid():
            form.save()    
        
        #if form invalid
        else:
            errors = form.errors
            message = errors

        messages.success(request,(message))
        return render(request,'entities.html',{'model' : model,'modelName':modelName})

#if request received from entity page
    else:
        #if from item on list finds object instance and returns model appropriate form
        item=""
        if list_id != 'noId':
            model = str_to_class(modelName)
            item = model.objects.get(pk=list_id)
            if modelName == 'persons':
                form = personsForm(request.POST or None, instance=item)
            elif modelName == 'Protocol type' or modelName == 'protocoltype':
                form = protocolTypeForm(request.POST or None, instance=item)    
            elif modelName == 'task' or modelName == 'tasks':
                form = taskForm(request.POST or None, instance=item) 
            elif modelName == 'protocol' :
                form = ListForm(request.POST or None, instance=item) 
            elif modelName == 'ListFields' :
                form = fieldForm(request.POST or None, instance=item) 
                   
        #if request received from 'add' button on entity page (passes id as 0)
        else:   
            if modelName == 'persons':
                form = personsForm(request.POST or None)
            elif modelName == 'Protocol type' or modelName == 'protocoltype':
                form = protocolTypeForm(request.POST or None)
            elif modelName == 'task' or modelName == 'tasks':
                form = taskForm(request.POST or None)
            elif modelName == 'protocol':
                form = ListForm(request.POST or None)
            elif modelName == 'ListFields':
                form = fieldForm(request.POST or None)
            else:
                form = taskForm(request.POST or None)
        
        return render(request,'edit.html',{'form' : form, 'item' : item})

def entities(request,modelName):
    if modelName == 'persons':
        model = persons.objects.all
    elif modelName == 'Protocol type':
        model = protocoltype.objects.all
    elif modelName == 'tasks':
        model = task.objects.all
    elif modelName == 'protocols':
        model = protocol.objects.all
    elif modelName == 'ListFields':
        model = ListFields.objects.all
    else:
        model = persons.objects.all
    return render(request,'entities.html',{'model' : model,'modelName':modelName})

def deleteInstance(request, list_id,modelName):
    
    if modelName == 'persons':
        item = persons.objects.get(pk=list_id)
        model = persons.objects.all
    elif modelName == 'protocoltype':
        item = protocoltype.objects.get(pk=list_id)
        model = protocoltype.objects.all
    elif modelName == 'protocol':
        item = protocol.objects.get(pk=list_id)
        model = protocol.objects.all 
    elif modelName == 'ListFields':
        item = ListFields.objects.get(pk=list_id)
        model = ListFields.objects.all 
    item.delete()
    messages.success(request,(modelName +' deleted'))
    return render(request,'entities.html',{'model' : model,'modelName':modelName})

#sets visible fields in form according to protocol type
def removeFields(form,protocol):
    visible_fields = protocol.visibleFields()
    visible_fields.append('type')
    invisible_fields = []
    #generates array of field names not to show on form
    for field in form.fields:
        if field not in visible_fields:
            invisible_fields.append(field)
    #removes fields not to show from field dictionary        
    for field in invisible_fields :
        if field in form.fields:
            form.fields.pop(field)

def logout_request(request):
    logout(request)
    return render (request,'index.html')

def email(request):
    subject = 'Thank you for registering to our site'
    message = ' it  means a world to us '
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['nick@browndesign.co.uk',]
    send_mail( subject, message, email_from, recipient_list )
    return redirect('home')