# serializers are class which take an object
# turn i tinto Json object and then we can return it
from rest_framework.serializers import ModelSerializer
from base.models import Room



class roomSerializer(ModelSerializer):
    class Meta:
        model = Room

        fields = '__all__'