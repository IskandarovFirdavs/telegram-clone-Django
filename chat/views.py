from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from chat.forms import RegistrationForm, LoginForm
from chat.models import Room, Message, UserModel


@login_required(login_url='login')
def home(request):
    if request.method == 'POST':
        room = request.POST['room']
        chat_type = request.POST.get('chat_type', 'group')

        try:
            existing_room = Room.objects.get(room_name=room)
        except Room.DoesNotExist:
            existing_room = Room.objects.create(
                room_name=room,
                chat_type=chat_type
            )
        return redirect('room', room_name=room, username=request.user)
    return render(request, 'home.html')


@login_required(login_url='login')
def join(request):
    if request.method == 'POST':
        room = request.POST['room_name']
        try:
            r = Room.objects.get(room_name=room)
            if r.members.count() < 2 or request.user in r.members.all():
                return redirect('room', room_name=room, username=request.user)
            else:
                messages.error(request, "Room is full")
                return redirect('join')
        except Room.DoesNotExist:
            messages.error(request, "Bunday xona mavjud emas")
            return redirect('join')
    return render(request, 'join.html')



@login_required(login_url='login')
def room(request, room_name, username):
    existing_room = Room.objects.get(room_name=room_name)
    get_messages = Message.objects.filter(room=existing_room)
    rooms = request.user.chats.all()

    try:
        existing = Room.objects.get(room_name=existing_room)
        existing.members.add(request.user)
        existing.save()
    except Room.DoesNotExist:
        u = Room.objects.create(room_name=room_name, members=request.user)


    context = {
        'rooms': rooms,
        'messages': get_messages,
        'username': request.user,
        "room_name": existing_room
    }
    return render(request, 'room.html', context)


def rooms_list(request):
    rooms = Room.objects.order_by('room_name')

    return render(request, 'some_html.html', {'rooms': rooms})


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('profile')

    else:
        form = RegistrationForm()

    context = {
        'form': form
    }

    return render(request, 'register.html', context)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, 'Username or password is invalid')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required
def profile_view(request):
    user = get_object_or_404(UserModel, id=request.user.id)
    rooms = request.user.chats.all()

    context = {
        'user': user,
        'rooms': rooms
    }

    return render(request, 'profile.html', context)
