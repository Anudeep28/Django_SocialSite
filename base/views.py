from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Room, Topic, User, Message
from django.contrib.auth import authenticate, login, logout
from .forms import RoomForm, userForm
from django.db.models import Q
from django.contrib import messages
# Restrict a user see pages
from django.contrib.auth.decorators import login_required
# Django has a user creation form built in forms
#from django.contrib.auth.forms import UserCreationForm
from .forms import myUserForm

def loginPage(request):

    page = 'login'
    
    # this below piece is for 
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # check if user exists
        try:
            user = User.objects.get(email=email)
        except:
            # how to output the flash messages
            messages.error(request, "User does not exist")
        # Either gives error or user object with those credentials
        user = authenticate(request, email=email,\
                             password=password)
        if user is not None:
            # go ahead and add in the session in the db
            # and the browser
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exists')
    context = {'page':page}
    return render(request,'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    #page = 'register'
    # creates blank instance of the form
    
    #form = UserCreationForm()
    form = myUserForm()

    if request.method == 'POST':
        form = myUserForm(request.POST)
        if form.is_valid():
            #we want to access the user that is created
            # we want to access the user right away an object
            # user object is created here
            # ? we want to able to clean the user data
            user = form.save(commit=False)
            # lower case method
            # this has to be updated int he login as well
            user.username = user.username.lower()
            user.save()
            # logging the user in the app
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,form.errors)

    return render(request, 'base/login_register.html', {'form':form})

# Create your views here.
def home(request):
    
    # blank '' is important to tell show eveything when no filter string is present
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    # search can be case sensitive or insensitive i
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |\
                                Q(name__icontains=q) |
                                Q(description__icontains=q)
                                )

    # Get all the topics for now
    # no given to limit what user sees of topics
    topics = Topic.objects.all()[:5]
    # to get the count of rooms available
    room_count = rooms.count()

    # activities in the room
    room_messages = Message.objects.all().order_by('-created')\
        .filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms, 'topics':topics,
               'room_count':room_count,'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    # get the comments int he room
    # message_set is like querying child object values
    # the other way around
    roomMessages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
        # Message instance in which create method
        # it creates a message instance with the added 
        # values just like save updates
        # the db but before sabe step
        message = Message.objects.create(
        user = request.user,
        room = room,
        body = request.POST.get('body')
        )
        # when the new user adds his comments he gets added 
        # to the room
        room.participants.add(request.user)
        # make sure we are on the same page for the get request
        return redirect('room', pk=room.id)
        room
    context = {'room':room,'roomMessages':roomMessages, 
               'participants':participants}

    return render(request, 'base/room.html', context)

# this is page is restricted to login
# there is more functionality in it 
# we can filter user as per requirements
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    #.objects.filter(id!=request.user.id)
    # after the form is displayed check wether the user has clicked submit
    topics = Topic.objects.all()
    if request.method == 'POST':
        # get the delected option of topic
        topic_name = request.POST.get('topic')
        # below line it will return object or create it 
        # in the db and then get the value of the topic
        # so basically user wants to create a new topic 
        # this helps us to make it more dynamic and gets added into the 
        # topic instance
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # create the room instance same as form which
        # creates the instance
        Room.objects.create(
            host=request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )
        # we have created the form already and can extract field just like html
        # Request.POST is passing all the data from the user into the form
        # form = RoomForm(request.POST)
        # All types of Room match
        # if form.is_valid():
            
        #     # below line saves the forms which is a instance is added to the 
        #     # Room database of model
        #     # taking the instances of the form filled by user
        #     room = form.save(commit=False)
        #     # filling the user who is logged in
        #     room.host = request.user
        #     room.save()
        return redirect('home')
        
    context = {'form':form,'topics':topics,'room':room}
    return render(request,'base/room_form.html',context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    # get the user created rooms
    rooms = user.room_set.all()
    # for messages
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages':room_messages,
               'topics':topics}
    return render(request, 'base/profile.html', context)

# pk is added to know what room are we updating
@login_required(login_url='login')
def updateRoom(request, pk):
    # get the item to be updated
    room = Room.objects.get(id=pk)
    # below line gives the empty form of the Room
    # adding instance add that instance room extracted above
    # into the fields of the empty form in RoomForm
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    # if the user is not the owner
    # this required because we have only given permission to 
    # login users and 
    if request.user != room.host:
        return HttpResponse("""<h1>You are not allowed here!!</h1>""")

    if request.method=='POST':
        topic_name = request.POST.get('topic')
        # below line it will return object or create it 
        # in the db and then get the value of the topic
        # so basically user wants to create a new topic 
        # this helps us to make it more dynamic and gets added into the 
        # topic instance
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # the instance is important as it affects only the current room
        # form = RoomForm(request.POST, instance=room)

        # if form.is_valid():
        #     form.save()
        room.topic = topic
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form':form,'topics':topics, 'room':room}
    return render(request,'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("""<h1>You are not allowed here!!</h1>""")
    
    if request.method == 'POST':
        # remove that room instance from the db
        room.delete()

        return redirect('home')
    
    return render(request,'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse("""<h1>You are not allowed to delete!!</h1>""")
    
    if request.method == 'POST':
        # remove that room instance from the db
        message.delete()

        return redirect('home')
    
    return render(request,'base/delete.html',{'obj':message})

@login_required(login_url='login')
def updateUser(request):
    user =request.user
    form = userForm(instance=user)
    

    if request.method == 'POST':
        form = userForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    
    
    context = {'form':form}
    return render(request,'base/update-user.html',context)


def topicsPage(request):
    # blank '' is important to tell show eveything when no filter string is present
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages = Message.objects.all()
    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)