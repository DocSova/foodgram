import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient

class Command(BaseCommand):

    def handle(self, *args, **options):
        with open("data/ingredients.csv", "r", encoding="utf-8") as file:
            csv_reader = csv.reader(file, delimiter=",")
            ingredients_array = []

            for row in csv_reader:
                name, measurement_unit = row

                if name:
                    ingredient = Ingredient(name=name, measurement_unit=measurement_unit)
                    ingredients_to_create.append(ingredient)
            Ingredient.objects.bulk_create(ingredients_to_create)
