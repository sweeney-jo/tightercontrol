from django.shortcuts import render
from .resource import InputResource
from tablib import Dataset

def simple_upload(request):
    if request.method == 'POST':
        input_resource = InputResource()
        dataset = Dataset()
        new_inputs = request.FILES['myfile']

        imported_data = dataset.load(new_inputs.read())
        result = input_resource.import_data(dataset, dry_run=True)  # Test the data import

        if not result.has_errors():
            input_resource.import_data(dataset, dry_run=False)  # Actually import now

    return render(request, 'resInput/import.html')
