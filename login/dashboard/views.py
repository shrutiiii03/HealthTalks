from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, LoginForm
from .models import User
from .models import BlogPost
from .forms import BlogPostForm
from django.urls import reverse
from django.shortcuts import render, get_object_or_404

def signup(request):
    if request.method == 'POST':
        print("Request method is POST")  # Debugging statement
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data.get('user_type')
            user.user_type = user_type  # Ensure user_type is set
            if user_type == 'patient':
                user.is_patient = True
                user.is_doctor = False
            elif user_type == 'doctor':
                user.is_patient = False
                user.is_doctor = True
            user.save()
            return redirect(reverse('login_dashboard:login'))  
        else:
            print("Form is not valid")  # Debugging statement
            print("Form errors:", form.errors)  # Debugging statement
    else:
        print("Request method is not POST")  # Debugging statement
        form = SignupForm()
    return render(request, 'dashboard/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.user_type == 'patient':
                    return redirect(reverse('login_dashboard:patient_dashboard'))
                elif user.user_type == 'doctor':
                    return redirect(reverse('login_dashboard:doctor_dashboard'))
            else:
                form.add_error(None, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'dashboard/login.html', {'form': form})

@login_required
def patient_dashboard(request):
    return render(request, 'dashboard/patient_dashboard.html', {'user': request.user})

@login_required
def doctor_dashboard(request):
    return render(request, 'dashboard/doctor_dashboard.html', {'user': request.user})

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect('dashboard:blog_post_list')  # Redirect to blog post list view
    else:
        form = BlogPostForm()
    return render(request, 'dashboard/blog_post_form.html', {'form': form})

@login_required
def blog_post_list(request):
    if request.user.is_doctor:
        posts = BlogPost.objects.filter(author=request.user)
    else:  # Assuming patients see all non-draft posts categorized by category
        posts = BlogPost.objects.filter(is_draft=False)
    
    category = request.GET.get('category')
    if category:
        posts = posts.filter(category=category) 

    for post in posts:
        post.summary = ' '.join(post.summary.split()[:15]) + ('...' if len(post.summary.split()) > 15 else '')

    context = {
        'posts': posts,
        'categories': BlogPost.CATEGORY_CHOICES,       
    }
    return render(request, 'dashboard/blog_post_list.html', context)

@login_required
def blog_post_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'dashboard/blog_post_detail.html', {'post': post})