from rest_framework import serializers


class SimpleCountStatsSerializer(serializers.Serializer):
    drivers = serializers.IntegerField()
    clients = serializers.IntegerField()
    suppliers = serializers.IntegerField()
    transports = serializers.IntegerField()
    products = serializers.IntegerField()
    orders = serializers.IntegerField()


class ProductTypeUnitStatsSerializer(serializers.Serializer):
    type = serializers.CharField(allow_blank=True)
    unit = serializers.CharField(allow_blank=True)
    income = serializers.FloatField()
    outcoming = serializers.FloatField()
    total = serializers.FloatField()


class IncomeProductTypeUnitStatsSerializer(serializers.Serializer):
    type = serializers.CharField(allow_blank=True)
    unit = serializers.CharField(allow_blank=True)
    income = serializers.FloatField()


class IncomeProductStatsSerializer(serializers.Serializer):
    product = serializers.CharField()
    income = serializers.FloatField()
    breakdown = IncomeProductTypeUnitStatsSerializer(many=True)


class ProductStatsSerializer(serializers.Serializer):
    product = serializers.CharField()
    income = serializers.FloatField()
    outcoming = serializers.FloatField()
    total = serializers.FloatField()
    breakdown = ProductTypeUnitStatsSerializer(many=True)


class SupplierIncomeProductStatsSerializer(serializers.Serializer):
    supplier = serializers.CharField()
    total = serializers.FloatField()
    products = IncomeProductStatsSerializer(many=True)


class OrderStatusStatsSerializer(serializers.Serializer):
    new = serializers.IntegerField()
    on_way = serializers.IntegerField()
    arrived = serializers.IntegerField()
    unloading = serializers.IntegerField()
    completed = serializers.IntegerField()
    rejected = serializers.IntegerField()
    total = serializers.IntegerField()


class StatusDurationSerializer(serializers.Serializer):
    new = serializers.SerializerMethodField()
    on_way = serializers.SerializerMethodField()
    arrived = serializers.SerializerMethodField()
    unloading = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    rejected = serializers.SerializerMethodField()
    total = serializers.IntegerField()

    def _format_duration(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        if not seconds or seconds < 0:
            return "00:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_new(self, obj):
        return self._format_duration(obj.get('new', 0))

    def get_on_way(self, obj):
        return self._format_duration(obj.get('on_way', 0))

    def get_arrived(self, obj):
        return self._format_duration(obj.get('arrived', 0))

    def get_unloading(self, obj):
        return self._format_duration(obj.get('unloading', 0))

    def get_completed(self, obj):
        return self._format_duration(obj.get('completed', 0))

    def get_rejected(self, obj):
        return self._format_duration(obj.get('rejected', 0))


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
    new = serializers.SerializerMethodField()
    in_progress = serializers.SerializerMethodField()
    paused = serializers.SerializerMethodField()
    completed = serializers.SerializerMethodField()
    expired = serializers.SerializerMethodField()
    rejected = serializers.SerializerMethodField()
    total = serializers.IntegerField()

    def _format_duration(self, seconds):
        """Convert seconds to HH:MM:SS format"""
        if not seconds or seconds < 0:
            return "00:00:00"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def get_new(self, obj):
        return self._format_duration(obj.get('new', 0))

    def get_in_progress(self, obj):
        return self._format_duration(obj.get('in_progress', 0))

    def get_paused(self, obj):
        return self._format_duration(obj.get('paused', 0))

    def get_completed(self, obj):
        return self._format_duration(obj.get('completed', 0))

    def get_expired(self, obj):
        return self._format_duration(obj.get('expired', 0))

    def get_rejected(self, obj):
        return self._format_duration(obj.get('rejected', 0))


class ExcavatorOrderStatsSerializer(serializers.Serializer):
    status_counts = ExcavatorOrderStatusStatsSerializer()
    status_durations = ExcavatorStatusDurationSerializer()
