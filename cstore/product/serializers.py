from companies.models import CompanyProfile
from rest_framework import serializers
from .models import Customer

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'mobile', 'name', 'store', 'email', 'created_at', 'updated_at', 'opening_balance']

    def validate_store(self, value):
        try:
            return CompanyProfile.objects.get(pk=value)
        except CompanyProfile.DoesNotExist:
            raise serializers.ValidationError("This store does not exist.")
    
    def validate(self, data):
        # Custom validation for unique mobile number and email within a store
        if Customer.objects.filter(store=data['store'], mobile=data['mobile']).exists():
            raise serializers.ValidationError("A customer with this mobile number already exists in this store.")
        if data['email'] and Customer.objects.filter(store=data['store'], email=data['email']).exists():
            raise serializers.ValidationError("A customer with this email already exists in this store.")
        return data
