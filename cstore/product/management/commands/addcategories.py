from django.core.management.base import BaseCommand
from product.models import Category

class Command(BaseCommand):
    help = 'Adds default categories and subcategories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'title': 'Electronics',
                'description': 'Explore top deals on electronics in Pakistan. Find a wide range of smartphones, laptops, and home appliances on Channab, the largest B2C and B2B online marketplace.',
                'subcategories': [
                    {'title': 'Smartphones', 'description': 'Discover the latest smartphones on Channab...'}
                ],
            },
            {
                'title': 'Fashion',
                'description': 'Discover the latest trends in fashion and get inspired by our new collections. Find your style on Channab, the go-to online fashion destination in Pakistan.',
                'subcategories': [
                    {'title': 'Clothing', 'description': 'Find a variety of clothing options for men, women, and children on Channab...'}
                ],
            },
            # You can add more main categories with their respective subcategories here
        ]

        for category_data in categories:
            # Create main category
            main_category, created = Category.objects.get_or_create(
                title=category_data['title'],
                defaults={'description': category_data['description']}
            )
            
            # Create subcategories for each main category
            for subcategory_data in category_data['subcategories']:
                Category.objects.get_or_create(
                    title=subcategory_data['title'],
                    defaults={
                        'description': subcategory_data['description'],
                        'parent': main_category
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully added categories and subcategories'))
