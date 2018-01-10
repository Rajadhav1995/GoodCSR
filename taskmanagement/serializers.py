from rest_framework import serializers
from models import *
from budgetmanagement.models import SuperCategory
from projectmanagement.models import Project
import pytz

class TaskSerializer(serializers.ModelSerializer):
    expected_start_date = serializers.DateTimeField()
    expected_end_date = serializers.DateTimeField()
    active = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    actual_start_date = serializers.SerializerMethodField()
    actual_end_date = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'name', 'expected_start_date', 'expected_end_date', 'start_date', 'end_date', 'active', 'status',
                  'actual_start_date', 'actual_end_date', 'activity', 'task_dependency', 'assigned_to','task_progress','slug')

    def get_active(self, obj):
        return obj.get_active_display()

    def get_status(self, obj):
        return obj.get_status_display()
    
    def get_start_date(self,obj):
        return obj.start_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
    
    def get_end_date(self,obj):
        return obj.end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
        
    def get_actual_start_date(self,obj):
        if obj.actual_start_date:
            date = obj.actual_start_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
            return date
       
    def get_actual_end_date(self,obj):
        if obj.actual_end_date:
            date = obj.actual_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))
            return date
#    def get_actual_end_date(self,obj):
#        return obj.actual_end_date.replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata'))


class ActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    active = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = '__all__'

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
        fields = '__all__'

    def get_active(self, obj):
        return obj.get_active_display()

    def get_status(self, obj):
        return obj.get_status_display()


class SuperCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = SuperCategory
        fields = '__all__'
        
        

class ProjectSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Project
        fields = ('id','name','slug','start_date','end_date')
