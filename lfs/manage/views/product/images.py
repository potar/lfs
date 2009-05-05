# django imports
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils import simplejson

# lfs.imports
from lfs.caching.utils import lfs_get_object_or_404
from lfs.catalog.models import Image
from lfs.catalog.models import Product
from lfs.core.signals import product_changed
from lfs.core.utils import LazyEncoder

@permission_required("manage_shop", login_url="/login/")
def manage_images(request, product_id, template_name="manage/product/images.html"):
    """
    """
    product = lfs_get_object_or_404(Product, pk=product_id)

    return render_to_string(template_name, RequestContext(request, {
        "product" : product,
    }))
    
# Actions
@permission_required("manage_shop", login_url="/login/")
def add_image(request, product_id):
    """Adds an image to product with passed product_id.
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    if request.method == "POST":
        for file_content in request.FILES.values():
            image = Image(content=product, title=file_content.name)
            image.image.save(file_content.name, file_content, save=True)
    
    # Refresh positions
    for i, image in enumerate(product.images.all()):
        image.position = i+1
        image.save()
    
    product_changed.send(product, request=request)    
    return HttpResponse(manage_images(request, product_id))

@permission_required("manage_shop", login_url="/login/")    
def update_images(request, product_id):
    """Saves/deletes images with given ids (passed by request body).
    """
    product = lfs_get_object_or_404(Product, pk=product_id)
    
    action = request.POST.get("action")
    if action == "delete":
        message = _(u"Images has been deleted.")
        for key in request.POST.keys():
            if key.startswith("delete-"):                
                try:
                    id = key.split("-")[1]
                    image = Image.objects.get(pk=id).delete()
                except (IndexError, ObjectDoesNotExist):
                    pass

    elif action == "update":
        message = _(u"Images has been updated.")
        if product.is_variant():
            if request.POST.get("active_images"):
                product.active_images = True
            else:
                product.active_images = False
            product.save()
            
        for key, value in request.POST.items():
            if key.startswith("title-"):
                id = key.split("-")[1]
                try:
                    image = Image.objects.get(pk=id)
                except ObjectDoesNotExist:
                    pass
                else:
                    image.title = value
                    image.save()
                
            elif key.startswith("position-"):
                try:
                    id = key.split("-")[1]
                    image = Image.objects.get(pk=id)
                except (IndexError, ObjectDoesNotExist):
                    pass
                else:                    
                    image.position = value            
                    image.save()
    
    # Refresh positions    
    for i, image in enumerate(product.images.all()):
        image.position = i+1
        image.save()
    
    product_changed.send(product, request=request)
    
    result = simplejson.dumps({
        "images" : manage_images(request, product_id),
        "message" : message,
    }, cls = LazyEncoder)
    
    return HttpResponse(result)