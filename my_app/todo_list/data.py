
#data API calls to managebac

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
    response = requests.get('https://api.managebac.com/v2/classes?per_page=1000&archived='+archived, headers=headers)

    return json.loads(response.content)
    

def classTermGrades(classId,termId):
    headers = {
    'auth-token': keyToken(),}
    response = requests.get('https://api.managebac.com/v2/classes/'+classId+'/assessments/term/'+termId+'/term-grades?include_archived_students=true', headers=headers)

    return json.loads(response.content)


