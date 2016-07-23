from django.shortcuts import render, render_to_response
from django.contrib.auth import authenticate
from django.template import RequestContext
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from .models import BBSPost, BBSUser
from .forms import PostForm
from .forms import ImageForm
from .forms import ChangepwdForm


def update_time(request):
    return HttpResponseRedirect('/personal/' + request.user.username)


def bbs_list(request):
    params = request.POST if request.method == 'POST' else None
    form = PostForm(params)
    if form.is_valid():
        post = form.save(commit=False)
        post.PUserID = request.user
        post.save()
        form = PostForm()
    posts = BBSPost.objects.filter(PParentID__isnull=True)
    return render(request, 'index.html', {'posts': posts, 'form': form})


def get_user(request):
    posts = BBSPost.objects.filter(PUserID=request.user)
    user = BBSUser.objects.get(user=request.user)
    return render(request, 'personal.html', {'posts': posts, 'user': user})


def bbs_post_detail(request, param):
    threadID = int(param)
    PPost = BBSPost.objects.get(id=threadID)
    params = request.POST if request.method == 'POST' else None
    form = PostForm(params)
    if form.is_valid():
        post = form.save(commit=False)
        post.PUserID = request.user
        post.PParentID = PPost
        post.save()
        form = PostForm()

    posts = list(BBSPost.objects.filter(id=threadID)) + \
        list(BBSPost.objects.filter(PParentID=threadID))
    for i in range(1, len(posts)):
        posts[i] = [posts[i]] + \
            list(BBSPost.objects.filter(PParentID=posts[i].id))
    print(posts)
    return render(request, 'postDetail.html', {'posts': posts, 'form': form})


def change_password(request, username):
    error = []
    user = BBSUser.objects.get(user=request.user)
    if request.method == 'POST':
        form = ChangepwdForm(request.POST)
        print('as')
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=username, password=data['old_pwd'])
            if user is not None:
                if data['new_pwd'] == data['new_pwd2']:
                    newuser = User.objects.get(username__exact=username)
                    newuser.set_password(data['new_pwd'])
                    newuser.save()
                    return HttpResponseRedirect('/accounts/login/')
                else:
                    error.append('Please input the same password')
            else:
                error.append('Please correct the old password')
        else:
            error.append('Please input the required domain')
    else:
        form = ChangepwdForm()
    return render_to_response('changepassword.html', {'form': form, 'error': error, 'user': user}, context_instance=RequestContext(request))


def change_image(request, username):
    files = request.FILES if request.method == 'POST' else None
    user = BBSUser.objects.get(user=request.user)
    if files:
        user = BBSUser.objects.get(user=request.user)
        user.UImage = files['UImage']
        user.save()
    posts = BBSUser.objects.all()
    return render(request, 'revisehead.html', {'posts': posts, 'user': user})
