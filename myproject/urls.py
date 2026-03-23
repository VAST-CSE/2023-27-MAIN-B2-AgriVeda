"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp.models import KERALA_DISTRICTS_CHOICES, Scheme
from myapp.admin import SchemeAdmin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')),
]

class DistrictAdminSite(admin.AdminSite):
    def __init__(self, name, district_name, district_id):
        super().__init__(name=name)
        self.site_header = f"{district_name} District Administration"
        self.site_title = f"{district_name} Portal"
        self.index_title = f"Manage {district_name} Schemes"
        self.district_id = district_id

    def has_permission(self, request):
        has_perm = super().has_permission(request)
        if not has_perm:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.userprofile.district == self.district_id
        except Exception:
            return False

class DistrictSchemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    exclude = ('district',) # Hide the district field from the form completely

    def get_queryset(self, request):
        # Strictly show only schemes for THIS admin site's district
        qs = super().get_queryset(request)
        return qs.filter(district=self.admin_site.district_id)

    def save_model(self, request, obj, form, change):
        # Automatically assign the scheme to the site's district
        obj.district = self.admin_site.district_id
        super().save_model(request, obj, form, change)

# Generate dedicated admin portals for every single district dynamically
for district_id, district_name in KERALA_DISTRICTS_CHOICES:
    admin_name = f"admin_{district_id.lower()}"
    site = DistrictAdminSite(name=admin_name, district_name=district_name, district_id=district_id)
    # Register with the customized, district-locked Scheme Admin
    site.register(Scheme, DistrictSchemeAdmin)
    urlpatterns.append(path(f"{admin_name}/", site.urls))
