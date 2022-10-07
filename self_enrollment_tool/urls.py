from django.urls import path, re_path

from self_enrollment_tool import views

urlpatterns = [
    path('', views.index, name='index'),
    path('lookup/', views.lookup, name='lookup'),
    path('enable/(?P<course_instance_id>\d+)$', views.enable,  name='enable'),
    path('enroll/(?P<course_instance_id>\d+)$', views.enroll, name='enroll'),

]
