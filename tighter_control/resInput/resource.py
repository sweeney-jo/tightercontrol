from import_export import resources
from .models import Input

class InputResource(resources.ModelResource):
    class Meta:
        model = Input
