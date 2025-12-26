from django.test import TestCase

# Create your tests here.
from core_app import views as SupplyView

SupplyView.supply_chain('boto3')
