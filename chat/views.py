from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from chat.forms import RegistrationForm, LoginForm
from chat.models import Room, Message, UserModel, Notification, ReplyMessage
from chat.templatetags.my_tags import ProductFilter
from django.http import HttpResponseForbidden


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
    existing_room = get_object_or_404(Room, room_name=room_name)
    get_messages = Message.objects.filter(room=existing_room)
    rooms = request.user.chats.all()
    other_members = existing_room.members.exclude(id=request.user.id)
    q = request.GET.get("q")
    qs = UserModel.objects.filter(username__icontains=q) if q else UserModel.objects.none()

    queryset = request.user.chats.all()
    room_filter = ProductFilter(request.GET, queryset=queryset)
    filtered_queryset = room_filter.qs

    all_chats = request.user.chats.order_by('-pk')

    paginator = Paginator(all_chats, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    Notification.objects.filter(
        owner=request.user,
        message__room=existing_room,
        is_read=False
    ).update(is_read=True)


    context = {
        'rooms': rooms,
        'page_obj': page_obj,
        'messages': get_messages,
        'username': request.user,
        "room_name": existing_room.room_name,
        'members': qs,
        'other_members': other_members,
        'filter': room_filter,
        'filtered_queryset': filtered_queryset,
    }
    return render(request, 'room.html', context)



@login_required
def another_user_profile_view(request, username):
    user = get_object_or_404(UserModel, username=username)
    users = UserModel.objects.exclude(id=request.user.id).order_by('username')

    q = request.GET.get('q')
    if q:
        users = users.filter(username__icontains=q)

    room_name = f"private_{'_'.join(sorted([request.user.username, user.username]))}"

    room = Room.objects.filter(room_name=room_name, chat_type='private').first()

    # If not found → create it
    if not room:
        room = Room.objects.create(
            room_name=room_name,
            chat_type='private'
        )
        room.members.add(request.user, user)

    return redirect('room', room_name=room.room_name, username=request.user.username)


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
        'rooms': rooms,

    }

    return render(request, 'profile.html', context)


@login_required(login_url='login')
def chats_list(request):
    qs = UserModel.objects.exclude(id=request.user.id).order_by('username')

    rooms = request.user.chats.order_by('-room_name')

    rooms_with_notifications = []
    for room in rooms:
        has_unread = Notification.objects.filter(
            owner=request.user,
            message__room=room,
            is_read=False
        ).exists()
        rooms_with_notifications.append((room, has_unread))

    users = UserModel.objects.exclude(id=request.user.id).order_by('username')
    q = request.GET.get("q")

    if q:
        users = users.filter(username__icontains=q)

    unread_count = Notification.objects.filter(owner=request.user, is_read=False).count()

    context = {
        'rooms_with_notifications': rooms_with_notifications,
        'users': users,
        'unread_notifications': unread_count,
        'qs': qs,
    }

    return render(request, 'chats.html', context)




def another_profile(request, pk):
    user = UserModel.objects.get(pk=pk)
    qs = UserModel.objects.exclude(pk=request.user.pk).order_by('username')

    return render(request, 'view_another_profile.html', {
        'user': user,
        'users': qs
    })


@login_required
def edit_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender != request.user:
        return HttpResponseForbidden("You are not allowed to edit this message.")

    if request.method == "POST":
        new_text = request.POST.get("message")
        if new_text:
            message.message = new_text
            message.save()
            messages.success(request, "Message updated successfully!")
            return redirect("room", room_name=message.room.room_name, username=request.user.username)

    return render(request, "edit_message.html", {"message": message})


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(Message, id=message_id)

    if message.sender != request.user:
        return HttpResponseForbidden("You are not allowed to delete this message.")

    if request.method == "POST":
        room_name = message.room.room_name
        message.delete()
        messages.success(request, "Message deleted successfully!")
        return redirect("room", room_name=room_name, username=request.user.username)

    return render(request, "confirm_delete.html", {"message": message})


@login_required
def reply_message(request, parent_message_id):
    if request.method == "POST":
        parent_message = get_object_or_404(Message, id=parent_message_id)
        reply_text =request.POST.get('reply')
        if reply_text:
            ReplyMessage.objects.create(
                owner =request.user,
                message=parent_message,
                reply_comment=reply_text
            )

        next_url =request.POST.get('next', 'home')
        return redirect(next_url)

    return redirect(request.path)