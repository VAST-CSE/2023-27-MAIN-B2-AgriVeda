from django.contrib import admin
from .models import Scheme, UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'district')
    search_fields = ('user__username', 'district')

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('title', 'district', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'district')
    list_filter = ('district',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        # If user has a district profile, only show their district's schemes
        try:
            if request.user.userprofile.district:
                return qs.filter(district=request.user.userprofile.district)
        except UserProfile.DoesNotExist:
            pass
            
        return qs.none() # If they are staff but have no district and are not superuser, they see nothing

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "district" and not request.user.is_superuser:
            try:
                # Force the district to be the user's assigned district
                user_district = request.user.userprofile.district
                if user_district:
                    kwargs['choices'] = ((user_district, user_district),)
            except UserProfile.DoesNotExist:
                pass
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            try:
                user_district = request.user.userprofile.district
                if user_district:
                    obj.district = user_district
            except UserProfile.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
