from django.urls import path

from .api.v1.views import ShiftCountApi, MachineUtilization,BeltAverage

urlpatterns = [
    path('api/v1/shift_count/', ShiftCountApi.as_view(), name='shift'),
    path('api/v1/machine/', MachineUtilization.as_view(), name='machine'),
    path('api/v1/belt/', BeltAverage.as_view(), name='belt'),
]
