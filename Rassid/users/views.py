import os
from email.mime.image import MIMEImage

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


# Custom Password Reset Views
class CustomPasswordResetView(auth_views.PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.txt'          # نص احتياطي
    html_email_template_name = 'users/password_reset_email.html'    # HTML
    subject_template_name = 'users/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = render_to_string(subject_template_name, context).strip()
        body_txt = render_to_string(email_template_name, context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=body_txt,
            from_email=from_email,
            to=[to_email],
        )

        if html_email_template_name:
            body_html = render_to_string(html_email_template_name, context)
            msg.attach_alternative(body_html, "text/html")

            # ✅ شعار من media (بدون مسار ويندوز)
            # تأكد اسم المجلد والملف مطابقين: media/airport_images/plane.png
            logo_path = os.path.join(settings.MEDIA_ROOT, "airport_images", "plane.png")

            if os.path.exists(logo_path):
                with open(logo_path, "rb") as f:
                    image = MIMEImage(f.read())
                    image.add_header("Content-ID", "<rassid_logo>")
                    image.add_header("Content-Disposition", "inline", filename="plane.png")
                    msg.attach(image)

        msg.send()

    def form_valid(self, form):
        # Debug (اختياري)
        print('EMAIL_BACKEND:', getattr(settings, "EMAIL_BACKEND", None))
        print('DEFAULT_FROM_EMAIL:', getattr(settings, "DEFAULT_FROM_EMAIL", None))
        print('EMAIL_HOST_USER:', getattr(settings, "EMAIL_HOST_USER", None))
        return super().form_valid(form)


class CustomPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class CustomPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


def login_view(request):
    if request.user.is_authenticated:
        return redirect_user_based_on_role(request.user)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect_user_based_on_role(user)
            else:
                messages.error(request, "This account is inactive.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('users:login')


def redirect_user_based_on_role(user):
    if user.role == 'superadmin':
        return redirect('public_home')
    elif user.role == 'airport_admin':
        return redirect('public_home')
    elif user.role == 'operator':
        return redirect('operator_dashboard')
    else:
        return redirect('public_home')
