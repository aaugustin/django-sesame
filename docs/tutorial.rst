Tutorial
========

Let's get practical.

First, we'll implement :ref:`login by email <Login by email>`, also known as
"Magic Links", in a Django project. Login by email can provide a better user
experience as users generally don't forget their email address. Keep in mind
that it requires fast and reliable email delivery.

Then, we'll create :ref:`authenticated links <Authenticated links>` to share
private content without logging in a user. As an example, a vacation rentals
service could let a customer share a booking with other travelers, while not
giving them full access to the customer's account.

The two sections are independent. Once you implement the :ref:`prerequisites
<Prerequisites>`, you may proceed with the first or the second section.

Prerequisites
-------------

Create a Django project
.......................

You may work in an existing project or you may initialize a new project as follows:

.. code-block:: console

    $ django-admin startproject tutorial
    $ cd tutorial
    $ ./manage.py migrate

If you reuse an existing project, it should enable :mod:`django.contrib.auth`.

If you have a custom user model, ensure that the email address of users is
stored in a field named ``email``. Else, you will have to adapt references
to this field.

You need a user for testing. The tutorial uses ``jane.doe@example.com`` in
examples. In a new project, you can create a superuser this purpose:

.. code-block:: console

    $ ./manage.py createsuperuser

Install django-sesame
.....................

Follow the instructions in the :ref:`getting started guide <Getting started>` to
install and configure django-sesame.

Login by email
--------------

We are going to build the following login flow:

1. The user provides their email address.
2. We create an authentication token and build a magic link.
3. We email the magic link to them to confirm that they own the email address.
4. The user clicks the link, we check the token, and we log them in.

Configure short-lived tokens
............................

Before we start coding, we should think about the security of the system. Tokens
are only intended to allow the user to log in now. Let's limit their validity to
5 minutes.

Open your project settings and add this line:

.. code-block:: python

    SESAME_MAX_AGE = 600  # 600 seconds = 10 minutes

Configure redirect after login
..............................

Set :setting:`LOGIN_REDIRECT_URL` to a URL that tells whether the user is
authenticated so you can easily tell whether login succeeds.

If you initialized a new project and you test with a superuser, you can simply
use the admin. Conveniently, it provides a link to log out:

.. code-block:: python

    LOGIN_REDIRECT_URL = "/admin/"

Now we can go back to building the login flow.

Create a login form
...................

Decide where you're going to add the code. In an existing project, perhaps you
already have an app for project-wide concerns; that's a good place. Otherwise,
you can create a new app.

In this app, create a login form with only one field, the email address of the
user.

.. literalinclude:: tutorial/email_login/forms.py
    :caption: forms.py

Create templates to display the form and to show a message after submitting it
successfully.

.. literalinclude:: tutorial/email_login/email_login.html
    :caption: templates/email_login.html
    :language: html+django

.. literalinclude:: tutorial/email_login/email_login_success.html
    :caption: templates/email_login_success.html
    :language: html+django

In an existing project, you may inherit a base template and add styling.

Make sure that Django can find the templates. If needed, add the directory where
they're stored to the :setting:`DIRS <TEMPLATES-DIRS>` option of the
:setting:`TEMPLATES` setting.

Create a view to handle the form display and submission logic.

.. code-block:: python
    :caption: views.py

    from django.shortcuts import render
    from django.views.generic import FormView

    from .forms import EmailLoginForm

    class EmailLoginView(FormView):
        template_name = "email_login.html"
        form_class = EmailLoginForm

        def form_valid(self, form):
            # TODO: email magic link to user.
            return render(self.request, "email_login_success.html")

.. admonition:: Why does ``form_valid()`` ignore the Post/Redirect/Get pattern?
    :class: hint

    After handling a form submission, it is a good practice to redirect the user
    to a new URL to avoid a duplicate if the user reloads the page.

    In our case, resubmitting the form will send another Magic Link. This is a
    sensible result after refreshing a page that says "We sent a log in link."

    If you prefer to stick to Post/Redirect/Get, you can replace ``render(...)``
    with ``redirect(...)`` and add a view for rendering the success template.

Add a route to this view in your URLconf:

.. code-block:: python
    :caption: urls.py

    from django.urls import path

    from .views import EmailLoginView

    urlpatterns = [
        ...,
        path("login/", EmailLoginView.as_view(), name="email_login"),
        ...,
    ]

Check that your development server is running.

Open http://127.0.0.1:8000/login/ in a browser. You should see this form:

.. image:: tutorial/email_login/email_login.png
    :width: 640
    :align: center

If you see a message saying that you are already logged in, log out.

Put an email address in the form and submit it. You should see this message:

.. image:: tutorial/email_login/email_login_success.png
    :width: 640
    :align: center

Good. With the scaffolding in place, we can move on to the actual logic.

Generate a magic link
.....................

Now we're going to use two APIs provided by django-sesame:

- :func:`sesame.utils.get_query_string` to generate a URL query string with an
  authentication token;
- :class:`sesame.views.LoginView` to parse this query string, validate the
  token, and log the user in.

Add a route to :class:`~sesame.views.LoginView` in your URLconf. The magic link
will point to this route.

.. code-block:: python
    :caption: urls.py

    from sesame.views import LoginView

    urlpatterns = [
        ...,
        path("login/auth/", LoginView.as_view(), name="login"),
        ...,
    ]

Add logic in ``EmailLoginView.form_valid`` to look up the user with the given
email address and call :func:`~sesame.utils.get_query_string`. For now, we'll
focus on the happy path; we'll handle errors later.

.. code-block:: python
    :caption: views.py

    from django.contrib.auth import get_user_model
    from django.shortcuts import render
    from django.urls import reverse
    from django.views.generic import FormView

    from .forms import EmailLoginForm

    class EmailLoginView(FormView):
        template_name = "email_login.html"
        form_class = EmailLoginForm

        def form_valid(self, form):
            email = form.cleaned_data["email"]

            User = get_user_model()
            user = User.objects.get(email=email)

            link = reverse("login")
            link += sesame.utils.get_query_string(user)
            print("magic link:", link)

            return render(self.request, "email_login_success.html")

Open the login form, type the email of the test user, and submit the form.

In the console, you should see:

.. code-block::

    magic link: /login/auth/?sesame=AAAAAQSR1RR4dQ8Oa_2nO25r

This looks pretty good! We're missing the domain name, though, so this link
won't work in an email. Let's fix that:

.. code-block:: python
    :caption: views.py

            link = reverse("login")
            link = self.request.build_absolute_uri(link)  # add this
            link += sesame.utils.get_query_string(user)
            print("magic link:", link)

Try again. You should see:

.. code-block::

    magic link: http://127.0.0.1:8000/login/auth/?sesame=AAAAAQSR1UAocK9OxRHSjn-B

Open that link. You're logged in and redirected to
:setting:`LOGIN_REDIRECT_URL`!

Log out now so you can try logging in again later.

Email the magic link
....................

Instead of displaying the link in the console, let's send an email to the user:

.. code-block:: python
    :caption: views.py

            # replace print("magic link:", link) with this
            user.email_user(
                subject="[django-sesame] Log in to our app",
                message=f"""\
    Hello,

    You requested that we send you a link to log in to our app:

        {link}

    Thank you for using django-sesame!
    """)

You are following this tutorial in a development environment where you don't
usually have access to an email server.

Open your project settings and tell Django to display emails in the console
rather than send them:

.. code-block:: python

    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

During local development, you will still find the magic link in the console.
When deploying to a production environment where an email server is configured,
magic links will be sent by email.

Log out and try logging in with the test user again. You should see:

.. code-block::

    Content-Type: text/plain; charset="utf-8"
    MIME-Version: 1.0
    Content-Transfer-Encoding: 7bit
    Subject: [django-sesame] Log in to our app
    From: webmaster@localhost
    To: jane.doe@example.com
    Date: Mon, 06 Jun 2022 08:10:01 -0000
    Message-ID: <165450300108.98358.6800704408988069350@53.1.168.192.in-addr.arpa>

    Hello,

    You requested that we send you a link to log in to our app:

        http://127.0.0.1:8000/login/auth/?sesame=AAAAAQSR1VluboTQNaLaBLYs

    Thank you for using django-sesame!

    -------------------------------------------------------------------------------

Click that link and check that you're logged in. Then log out.

If you're patient, you can wait five minutes for the link to expire and confirm
that it doesn't work anymore. You should get a :func:`403 Forbidden
<django.views.defaults.permission_denied>` error.

Improve the view
................

For reference, here's a version of ``EmailLoginView`` with error handling and
more structure.

Feel free to make your own improvements!

.. literalinclude:: tutorial/email_login/views.py
    :caption: views.py

Authenticated links
-------------------

In the first part, we saw how to log a user in with a magic link. This requires
a user account. What if we'd like to share a private page without requiring the
recipient to sign up for an account?

We will use a vacation rentals service as an example. We will provide customers
with private links to share bookings with other travelers. These links point to
a specific view of a booking. They mustn't log the recipient in, lest they gain
access to the whole customer account.

Configure long-lived tokens
............................

We expect that customers may book a rental up to one year before it starts. Our
private links don't give access to anything particularly sensitive. Therefore,
we can safely set the lifetime of private links to a bit more than one year.

By default, django-sesame invalidates tokens when a user changes their password
(and when a user logs in after upgrading Django; their password hash is updated
which has the same effect). We will disable this behavior so that private links
always remain valid.

Open your project settings and add these lines:

.. code-block:: python

    import datetime
    SESAME_MAX_AGE = datetime.timedelta(days=400)

    SESAME_INVALIDATE_ON_PASSWORD_CHANGE = False

We're all set. Now we can focus on the app.

Create a booking app
....................

Initialize an app:

.. code-block:: console

    $ ./manage.py startapp bookings

Add it to the :setting:`INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = [
        ...
        "bookings",
    ]

Open ``models.py`` and create this model:

.. code-block:: python
    :caption: bookings/models.py

    from django.conf import settings
    from django.db import models

    class Booking(models.Model):
        name = models.CharField(max_length=100)
        customer = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

For the purposes of this tutorial, we need only a foreign key to the user model.
Of course, a realistic model would provide many other fields.

Generate and apply the database migration:

.. code-block:: console

    $ ./manage.py makemigrations bookings
    $ ./manage.py migrate bookings

Open ``admin.py`` and configure a model admin:

.. code-block:: python
    :caption: bookings/admin.py

    from django.contrib import admin

    from .models import Booking

    @admin.register(Booking)
    class BookingAdmin(admin.ModelAdmin):
        list_display = ["id", "name", "customer"]

Check that your development server is running.

Open http://127.0.0.1:8000/admin/bookings/booking/add/ in a browser. Log in with
an admin account. Create a booking for your test user:

.. image:: tutorial/auth_links/add_booking.png
    :width: 800
    :align: center

Create a sharing page
.....................

At first, the sharing page will be public. We will make it private later.

Create this template:

.. literalinclude:: tutorial/auth_links/share_booking.html
    :caption: bookings/templates/bookings/share_booking.html
    :language: html+django


Open ``views.py`` and create this view:

.. code-block:: python
    :caption: bookings/views.py

    from django.shortcuts import get_object_or_404, render

    from .models import Booking

    def share_booking(request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        return render(request, "bookings/share_booking.html", {"booking": booking})

Add a route to this view in your URLconf:

.. code-block:: python
    :caption: urls.py

    from django.urls import path

    from bookings.views import share_booking

    urlpatterns = [
        ...,
        path("booking/<int:pk>/share/", share_booking, name="share-booking"),
        ...,
    ]

Open http://127.0.0.1:8000/booking/1/share/. You should see the sharing page for
your booking:

.. image:: tutorial/auth_links/share_booking.png
    :width: 800
    :align: center

Looks gorgeous. Now let's restrict access to those who have a private link.

Generate a private link
.......................

A private link must give access to only one booking. To achieve this, we will
add a scope to access tokens.

The scope for a booking will be ``"booking:<pk>"``, where ``<pk>`` is replaced
with the primary key of the booking. This sets a unique scope for each booking.
We are including ``booking`` in the name of the scope in case we want to create
tokens for other kinds of objects later.

Scopes are arbitrary. The only requirement is to provide the same scope when
generating a token and when authenticating it. If scopes don't match, then the
token is rejected. This prevents reuse of a token generated for a booking in
order to view another booking.

We can create tokens with :func:`sesame.utils.get_query_string`. It generates a
URL query string with an authentication token. It accepts a ``scope`` argument.

Add a method to the ``Booking`` model to generate private links:

.. literalinclude:: tutorial/auth_links/models.py
    :caption: bookings/models.py

For the purposes of this tutorial, you will get the private link in the admin.
In an actual app, you would provide it to the customer in his booking summary.

Display private links in the model admin:

.. literalinclude:: tutorial/auth_links/admin.py
    :caption: bookings/admin.py

Navigate to your booking in the admin:

.. image:: tutorial/auth_links/view_booking.png
    :width: 800
    :align: center

Copy the URL of the link, paste it in a notepad, and check that it looks like
http://127.0.0.1:8000/booking/1/share/?sesame=AAAAAQSZEgSh6g4hVT_PJqO6, except
with a different token.

Add access control
..................

Now let's modify the sharing view to look for the token and authenticate it.

We can use :func:`sesame.utils.get_user` for this purpose. It accepts a
``scope`` argument.

Modify the ``share_booking`` view:

.. literalinclude:: tutorial/auth_links/views.py
    :caption: bookings/views.py

When a valid token is found, :func:`~sesame.utils.get_user` returns the user
authenticated by the token. Here, that's the customer who made the booking.
Else, :func:`~sesame.utils.get_user` returns :obj:`None`.

.. admonition:: Why restrict the search to ``customer.booking_set``?
    :class: hint

    Given the following assumptions:

    * We create tokens scoped on a given booking only for the customer who made
      that booking;
    * The customer of a booking never changes;

    we know that the user authenticated by the token is always the customer of
    the booking.

    Restricting the lookup to bookings by this customer isn't strictly needed.
    It's more of a safety net in case we create tokens incorrectly.

Simplify the view
.................

You can decorate a view with :func:`sesame.decorators.authenticate` to look for
a token and authenticate a user. If a valid token is found,
:func:`~sesame.decorators.authenticate` stores the user in ``request.user``.
Else, it raises :exc:`~django.core.exceptions.PermissionDenied`.

Take advantage of this decorator to simplify ``share_booking``:

.. literalinclude:: tutorial/auth_links/views_decorator.py
    :caption: bookings/views.py

Perhaps you noticed that ``scope="booking:{pk}"`` is a regular string, not a
f-string like ``scope=f"booking:{pk}"`` previously. Indeed, the ``scope``
parameter is evaluated when importing ``bookings.views``, not when processing
an HTTP request, so the value of ``pk`` isn't known yet.

How will the scope eventually contain the right value of ``pk``?

At each HTTP request, :func:`~sesame.decorators.authenticate` performs string
formatting on ``scope`` using the arguments extracted from the URL and passed
to the view. This is where ``{pk}`` is replaced with the current value of the
``pk`` parameter of ``share_booking``.

One more thing
..............

Here's what the sharing view would look like as a class-based view:

.. literalinclude:: tutorial/auth_links/views_generic.py
    :caption: bookings/views.py

You would reference it in the URLconf as follows:

.. code-block:: python
    :caption: urls.py

    from django.urls import path

    from bookings.views import ShareBooking

    urlpatterns = [
        ...
        path("booking/<int:pk>/share/", ShareBooking.as_view(), name="share-booking"),
        ...
    ]

Alternatively, here's a a class-based view decorated with
:func:`~sesame.decorators.authenticate`:

.. literalinclude:: tutorial/auth_links/views_generic_decorator.py
    :caption: bookings/views.py

Using a class-based view brings no benefit here. This was just an example of how
you could add authentication with django-sesame to an existing class-based view.
