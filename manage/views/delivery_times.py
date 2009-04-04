# python imports
import urllib

# django imports
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

# lfs imports
import lfs.core.utils
from lfs.catalog.models import DeliveryTime

class DeliveryTimeForm(ModelForm):
    """Form to edit a delivery time.
    """
    class Meta:
        model = DeliveryTime

@permission_required("manage_shop", login_url="/login/")
def manage_delivery_times(request):
    """Dispatches to the first delivery time or to the form to add a delivery
    time (if there is no delivery time yet).
    """
    try:
        delivery_time = DeliveryTime.objects.all()[0]
        url = reverse("lfs_manage_delivery_time", kwargs={"id": delivery_time.id})
    except IndexError:
        url = reverse("lfs_add_delivery_time")
    
    return HttpResponseRedirect(url)

@permission_required("manage_shop", login_url="/login/")
def manage_delivery_time(request, id, template_name="manage/delivery_times/base.html"):
    """Provides a form to edit the delivery time with the passed id.
    """
    delivery_time = get_object_or_404(DeliveryTime, pk=id)
    if request.method == "POST":
        form = DeliveryTimeForm(instance=delivery_time, data=request.POST, files=request.FILES)
        if form.is_valid():
            new_delivery_time = form.save()
            return lfs.core.utils.set_message_cookie(
                url = reverse("lfs_manage_delivery_time", kwargs={"id" : id}),
                msg = u"Delivery time has been saved.",
            )            
    else:
        form = DeliveryTimeForm(instance=delivery_time)
    
    return render_to_response(template_name, RequestContext(request, {
        "delivery_time" : delivery_time,
        "delivery_times" : DeliveryTime.objects.all(),
        "form" : form,
        "current_id" : int(id),
    }))

@permission_required("manage_shop", login_url="/login/")    
def add_delivery_time(request, template_name="manage/delivery_times/add.html"):
    """Provides a form to add a new delivery time.
    """
    if request.method == "POST":
        form = DeliveryTimeForm(data=request.POST)
        if form.is_valid():
            delivery_time = form.save()

            return lfs.core.utils.set_message_cookie(
                url = reverse("lfs_manage_delivery_time", kwargs={"id" : delivery_time.id}),
                msg = u"Delivery time has been added.",
            )            

    else:
        form = DeliveryTimeForm()

    return render_to_response(template_name, RequestContext(request, {
        "form" : form,
        "delivery_times" : DeliveryTime.objects.all(),        
    }))

@permission_required("manage_shop", login_url="/login/")
def delete_delivery_time(request, id):
    """Deletes the delivery time with passed id.
    """
    delivery_time = get_object_or_404(DeliveryTime, pk=id)
    delivery_time.delete()

    return lfs.core.utils.set_message_cookie(
        url = reverse("lfs_manage_delivery_times"),
        msg = u"Delivery time has been deleted.",
    )            