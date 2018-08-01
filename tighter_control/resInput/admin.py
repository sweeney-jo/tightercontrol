from django.contrib import admin

from import_export.admin import ImportExportModelAdmin

from .models import Input

@admin.register(Input)
class InputAdmin(ImportExportModelAdmin):
    pass