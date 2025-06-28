from django.contrib import admin
from .models import VisitReason, IndividualSignIn, EventSignIn

# Register your models here.
admin.site.register(VisitReason)
admin.site.register(IndividualSignIn)
admin.site.register(EventSignIn)
