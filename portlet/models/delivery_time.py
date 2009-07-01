# django imports
from django import forms
from django.template.loader import render_to_string

# portlets imports
from portlets.models import Portlet

# shipping imports
import lfs.shipping.utils

class DeliveryTimePortlet(Portlet):
    """A portlet to display delivery time.
    """
    class Meta:
        app_label = 'portlet'

    def __unicode__(self):
        return "%s" % self.id

    def render(self, context):
        """Renders the portlet as html.
        """
        request = context.get("request")
        product = context.get("product")

        if product is None:
            d = {
                "display" : False,
            }
        else:
            info = lfs.shipping.utils.get_delivery_time(request, product)
            d = {
                "display" : True,
                "title" : self.title,
                "deliverable" : info["deliverable"],
                "delivery_time" : info["delivery_time"],
                "MEDIA_URL" : context.get("MEDIA_URL"),
            }

        return render_to_string("portlets/delivery_time.html", d)

    def form(self, **kwargs):
        """
        """
        return DeliveryTimeForm(instance=self, **kwargs)

class DeliveryTimeForm(forms.ModelForm):
    """
    """
    class Meta:
        model = DeliveryTimePortlet