from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404,JsonResponse
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from socialnetwork.forms import LoginForm, RegisterForm, ProfileForm, PostForm, CommentForm

from socialnetwork.models import Post, Comment, Profile
from django.utils import timezone

import json

# Create your views here.

def login_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)

    form = LoginForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('global_stream'))

def register_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    profile = Profile(bio="Hi!", user=new_user)
    profile.save()
    login(request, new_user)
    return redirect(reverse('global_stream'))

@login_required
def global_stream(request):
    if request.method == 'GET':
        posts = Post.objects.all().order_by('-post_date')
    post = Post()
    post.user = request.user
    post.post_date = timezone.now()
    
    post_form = PostForm(request.POST)
    if not post_form.is_valid():
        context = { 'form': post_form }
        return render(request, 'socialnetwork/global_stream.html', context)
    
    post.text = post_form.cleaned_data['text']
    post.save()
    posts = Post.objects.all().order_by('-post_date')
    
    context = { 'posts': posts }
    return render(request, 'socialnetwork/global_stream.html', context)

def get_global(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    response_data = {
    'posts': [],
    'comments': []
    }
    
    for p_item in Post.objects.all():
        post = {
            'id': p_item.id,
            'text': p_item.text,
            'post_date': p_item.post_date.isoformat(),
            'user_id': p_item.user.id,
            'fname': p_item.user.first_name,
            'lname': p_item.user.last_name,
        }
        response_data['posts'].append(post)
        for c_item in Comment.objects.filter(post=p_item):
            comment = {
                'id': c_item.id,
                'post': p_item.id,
                'text': c_item.text,
                'creation_time': c_item.creation_time.isoformat(),
                'user_id': c_item.user.id,
                'fname': c_item.user.first_name,
                'lname': c_item.user.last_name,
            }
            response_data['comments'].append(comment)
    
    response_json = json.dumps(response_data, default=str)
    return HttpResponse(response_json, content_type='application/json')

def add_comment(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    if request.method != 'POST':
        return _my_json_error_response("You must use a POST request for this operation", status=405)

    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter an item to add.", status=400)
    
    post_id = request.POST.get('post_id', '')
    if not post_id or not post_id.isdigit() or not 'post_id' in request.POST:
        return _my_json_error_response("Invalid post_id.", status=400)
    
    comment = Comment()
    comment.user = request.user
    comment.creation_time = timezone.now()
    try:
        comment.post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return _my_json_error_response("Post not found.", status=400)
    
    comment_form = CommentForm(data={'text': request.POST['comment_text']})
    if not comment_form.is_valid():
        return _my_json_error_response("Comment form data is not valid.", status=400)
    comment.text = comment_form.cleaned_data['text']
    comment.save()
    
    type = request.POST.get('type', '')
    if type == 'follower':
        return get_follower(request)
    else:
        return get_global(request)    
    # new_comment_data = {
    #     'id': comment.id,
    #     'post': comment.post,
    #     'text': comment.text,
    #     'user': comment.user,
    #     'creation_time': comment.creation_time.strftime("%Y-%m-%d %H:%M:%S"),
    #     'user_id': comment.user.id,
    #     'fname': comment.user.first_name,
    #     'lname': comment.user.last_name,
    # }
    
    # response_data = {
    #     'posts': [],
    #     'comments': [new_comment_data]
    # }
    
    # response_json = json.dumps(response_data, default=str)
    # return HttpResponse(response_json, content_type='application/json')

def _my_json_error_response(message, status=200):
    response_json = '{"error": "' + message + '"}'
    return HttpResponse(response_json, content_type='application/json', status=status)

@login_required
def follower_stream(request):
    following_profiles = request.user.profile.following.all()
    posts = Post.objects.filter(user__in=following_profiles)
    context = {'posts': posts.order_by('-post_date')}
    return render(request, 'socialnetwork/follower_stream.html', context)

def get_follower(request):
    if not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)
    
    response_data = {
    'posts': [],
    'comments': []
    }

    try:
        following_users = request.user.profile.following.all()
    except Profile.DoesNotExist:
        following_users = []

    for p_item in Post.objects.filter(user__in=following_users).exclude(user=request.user):
        post = {
            'id': p_item.id,
            'text': p_item.text,
            'post_date': p_item.post_date.isoformat(),
            'user_id': p_item.user.id,
            'fname': p_item.user.first_name,
            'lname': p_item.user.last_name,
        }
        response_data['posts'].append(post)

        for c_item in Comment.objects.filter(post=p_item):
            comment = {
                'id': c_item.id,
                'post': p_item.id,
                'text': c_item.text,
                'creation_time': c_item.creation_time.isoformat(),
                'fname': c_item.user.first_name,
                'lname': c_item.user.last_name,
            }
            response_data['comments'].append(comment)

    response_json = json.dumps(response_data, default=str)
    return HttpResponse(response_json, content_type='application/json')

@login_required
def profile(request):
    context = {}
    if request.method == 'GET':
        form = ProfileForm(initial={'bio': request.user.profile.bio})
        context['form'] = form
        return render(request, 'socialnetwork/profile.html', context)
    
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context['form'] = form
        return render(request, 'socialnetwork/profile.html', context)

    pic = form.cleaned_data['picture']
    bio = form.cleaned_data['bio']
    profile = request.user.profile
    profile.content_type = pic.content_type
    profile.picture = pic
    profile.bio = bio
    profile.save()
    
    context['form'] = form
    return render(request, 'socialnetwork/profile.html', context)
    
@login_required
def logout_action(request):
    logout(request)
    return redirect(reverse('global_stream'))

@login_required
def other_profile(request, id):
    profile = get_object_or_404(Profile, id=id)
    return render(request, 'socialnetwork/other_profile.html', {'profile': profile})

@login_required
def unfollow(request, id):
    user_to_unfollow = get_object_or_404(User, id=id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return redirect(reverse('other_profile', args=[id]))

@login_required
def follow(request, id):
    user_to_follow = get_object_or_404(User, id=id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return redirect(reverse('other_profile', args=[id]))

@login_required
def get_photo(request, id):
    profile = get_object_or_404(Profile, id=id)
    print('Picture #{} fetched from db: {} (type={})'.format(id, profile.picture, type(profile.picture)))
    
    if not profile.picture:
        raise Http404

    return HttpResponse(profile.picture, content_type=profile.content_type)
