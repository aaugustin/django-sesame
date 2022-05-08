Safari issues
-------------

The django-sesame middleware removes the token from the URL with an HTTP 302
Redirect after authenticating a user successfully. Unfortunately, in some
scenarios, this triggers Safari's "Protection Against First Party Bounce
Trackers". In that case, Safari clears cookies and the user is logged out.

To avoid this problem, django-sesame doesn't perform the redirect when it
detects that the browser is Safari. This relies on the ua-parser package,
which is an optional dependency. If it isn't installed, django-sesame always
redirects.
