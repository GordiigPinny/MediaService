from rest_framework import serializers
from Mediafiles.models import ImageFiles
from django.core.validators import validate_image_file_extension


class ImageFilesMetaSerializer(serializers.ModelSerializer):
    """
    Сериализатор мета-инфы о изображении
    """
    image_url = serializers.CharField(read_only=True)
    object_id = serializers.IntegerField(min_value=1, required=True, allow_null=False)
    object_type = serializers.ChoiceField(choices=ImageFiles.OBJECT_TYPE_CHOICES, required=True,
                                          allow_null=False)
    created_by = serializers.IntegerField(min_value=1, required=True, allow_null=False)
    created_dt = serializers.DateTimeField(read_only=True)
    deleted_flg = serializers.BooleanField(read_only=True)

    class Meta:
        model = ImageFiles
        fields = [
            'id',
            'object_id',
            'object_type',
            'created_by',
            'created_dt',
            'deleted_flg',
            'image_url',
        ]


class ImageFilesSerializer(ImageFilesMetaSerializer):
    """
    Сериализатор изображения с метой
    """
    image = serializers.ImageField(required=True, allow_null=False, write_only=True,
                                   validators=[validate_image_file_extension])

    class Meta(ImageFilesMetaSerializer.Meta):
        fields = ImageFilesMetaSerializer.Meta.fields + [
            'image',
        ]

    def create(self, validated_data):
        new = ImageFiles.objects.create(**validated_data)
        return new
