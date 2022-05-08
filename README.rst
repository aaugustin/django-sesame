.. image:: logo/horizontal.svg
   :width: 400px
   :alt: django-sesame

django-sesame provides frictionless authentication with "Magic Links" for
your Django project.

It generates URLs containing authentication tokens such as:
https://example.com/?sesame=zxST9d0XT9xgfYLvoa9e2myN

Then it authenticates users based on tokens found in URLs.

Use cases
=========

Known use cases for django-sesame include:

1. Login by email, an increasingly attractive option on mobile where
   typing passwords is uncomfortable. This technique is prominently
   deployed by Slack.

   If you're doing this, you should define a small ``SESAME_MAX_AGE``, perhaps
   10 minutes.

2. Authenticated links, typically if you're generating a report offline, then
   emailing a link to access it when it's ready. An authenticated link works
   even if the user isn't logged in on the device where they're opening it.

   Likewise, you should configure an appropriate ``SESAME_MAX_AGE``, probably
   no more than a few days.

   Since emails may be forwarded, authenticated links shouldn't log the user
   in. They should only allow access to specific views.

3. Sharing links, which are a variant of authenticated links. When a user
   shares content with a guest, you can create a phantom account for the guest
   and generate an authenticated link tied to that account.

   Email forwarding is even more likely in this context. If you're doing this,
   make sure authenticated links don't log the user in.

4. Non-critical private websites, for example for a family or club site,
   where users don't expect to manage a personal account with a password.
   Authorized users can bookmark personalized authenticated URLs.

   Here you can rely on the default settings because that's the original —
   and, admittedly, niche — use case for which django-sesame was built.
