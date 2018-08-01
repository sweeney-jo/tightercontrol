from django.shortcuts import render
from .resource import InputResource
from tablib import Dataset
from django.contrib.auth.decorators import login_required
from .models import Input
from django.contrib.auth.models import User


@login_required
def simple_upload(request):
    if request.method == 'POST':
        Input.user = request.user
        input_resource = InputResource()
        dataset = Dataset()
        new_inputs = request.FILES['myfile']

        imported_data = dataset.load(new_inputs.read()) 
        
        
        result = input_resource.import_data(dataset, dry_run=True)  # Test the data import
      
            
        if not result.has_errors():
           # Input.created_by= request.user.username
           # obj.user = request.user
           # super().save_model(request, obj, form, change)
            input_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'resInput/import.html')


