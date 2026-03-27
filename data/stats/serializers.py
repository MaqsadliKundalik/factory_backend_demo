from rest_framework import serializers


class SimpleCountStatsSerializer(serializers.Serializer):
    drivers = serializers.IntegerField()
    clients = serializers.IntegerField()
    suppliers = serializers.IntegerField()
    transports = serializers.IntegerField()
    products = serializers.IntegerField()
    orders = serializers.IntegerField()


class IncomeProductStatsSerializer(serializers.Serializer):
    product = serializers.CharField()
    income = serializers.IntegerField()


class SupplierIncomeProductStatsSerializer(serializers.Serializer):
    supplier = serializers.CharField()
    total = serializers.FloatField()
    products = IncomeProductStatsSerializer(many=True)


class OutcomingProductStatsSerializer(serializers.Serializer):
    product = serializers.CharField()
    outcoming = serializers.IntegerField()


class OrderStatusStatsSerializer(serializers.Serializer):
    new = serializers.IntegerField()
    on_way = serializers.IntegerField()
    arrived = serializers.IntegerField()
    unloading = serializers.IntegerField()
    completed = serializers.IntegerField()
    rejected = serializers.IntegerField()
    total = serializers.IntegerField()


class StatusDurationSerializer(serializers.Serializer):
    new = serializers.FloatField()
    on_way = serializers.FloatField()
    arrived = serializers.FloatField()
    unloading = serializers.FloatField()
    completed = serializers.FloatField()
    rejected = serializers.FloatField()
    total = serializers.IntegerField()


class OrderStatsSerializer(serializers.Serializer):
    status_counts = OrderStatusStatsSerializer()
    status_durations = StatusDurationSerializer()


class ExcavatorOrderStatusStatsSerializer(serializers.Serializer):
    new = serializers.IntegerField()
    paused = serializers.IntegerField()
    completed = serializers.IntegerField()
    expired = serializers.IntegerField()
    rejected = serializers.IntegerField()
    total = serializers.IntegerField()


class ExcavatorStatusDurationSerializer(serializers.Serializer):
    new = serializers.FloatField()
    paused = serializers.FloatField()
    completed = serializers.FloatField()
    expired = serializers.FloatField()
    rejected = serializers.FloatField()
    total = serializers.IntegerField()


class ExcavatorOrderStatsSerializer(serializers.Serializer):
    status_counts = ExcavatorOrderStatusStatsSerializer()
    status_durations = ExcavatorStatusDurationSerializer()
