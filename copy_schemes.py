import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from myapp.models import Scheme, KERALA_DISTRICTS_CHOICES

def duplicate_schemes():
    # Fetch the original baseline schemes (currently in Thiruvananthapuram)
    base_schemes = list(Scheme.objects.filter(district='Thiruvananthapuram'))
    
    # Do this only if Thiruvananthapuram has schemes
    if not base_schemes:
        print("No baseline schemes found in Thiruvananthapuram to copy.")
        return

    # To avoid double copying if script is run again, check if Kollam has schemes
    if Scheme.objects.filter(district='Kollam').exists():
        print("Districts already populated. Aborting to prevent duplicates.")
        return

    # Loop through each district, skipping Thiruvananthapuram since it already has them
    districts = [d[0] for d in KERALA_DISTRICTS_CHOICES if d[0] != 'Thiruvananthapuram']
    
    total_copies = 0
    for district in districts:
        for scheme in base_schemes:
            # Create a clone of the scheme for this district
            Scheme.objects.create(
                district=district,
                title=scheme.title,
                description=scheme.description,
                eligibility=scheme.eligibility,
                benefits=scheme.benefits,
                documents=scheme.documents,
                procedures=scheme.procedures
            )
            total_copies += 1
            
    print(f"Successfully copied {len(base_schemes)} schemes across 13 districts. Total new schemes: {total_copies}")

if __name__ == "__main__":
    duplicate_schemes()
