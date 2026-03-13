from rest_framework import serializers

class SimpleCountStatsSerializer(serializers.Serializer):
    drivers = serializers.IntegerField()
    clients = serializers.IntegerField()
    suppliers = serializers.IntegerField()
    transports = serializers.IntegerField()

class IncomeProductStatsSerializer(serializers.Serializer):
    product = serializers.CharField()
    income = serializers.IntegerField()
    
class SupplierIncomeProductStatsSerializer(serializers.Serializer):
    supplier = serializers.CharField()
    products = IncomeProductStatsSerializer(many=True)

