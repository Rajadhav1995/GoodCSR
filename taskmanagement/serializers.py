from rest_framework import serializers
from models import *
from budgetmanagement.models import SuperCategory


class TaskSerializer(serializers.ModelSerializer):
    expected_start_date = serializers.DateTimeField()
    expected_end_date = serializers.DateTimeField()
    active = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'name', 'expected_start_date', 'expected_end_date', 'start_date', 'end_date', 'active', 'status',
                  'actual_start_date', 'actual_end_date', 'activity', 'task_dependency', 'assigned_to')

    def get_active(self, obj):
        return obj.get_active_display()

    def get_status(self, obj):
        return obj.get_status_display()


class ActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    class Meta:
        model = Activity

    def get_activity_type(self, obj):
        return obj.get_activity_type_display()

    def get_status(self, obj):
        return obj.get_status_display()

    def get_active(self, obj):
        return obj.get_active_display()


class MilestoneSerializer(serializers.ModelSerializer):
    active = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Milestone

    def get_active(self, obj):
        return obj.get_active_display()

    def get_status(self, obj):
        return obj.get_status_display()


class SuperCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperCategory
