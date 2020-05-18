from io import BytesIO
from PIL import Image
from rest_framework import serializers
from Mediafiles.models import ImageFiles
from django.core.validators import validate_image_file_extension
from ApiRequesters.Auth.AuthRequester import AuthRequester
from ApiRequesters.exceptions import BaseApiRequestError
from ApiRequesters.utils import get_token_from_request


class ImageFilesMetaSerializer(serializers.ModelSerializer):
    """
    Сериализатор мета-инфы о изображении
    """
    image_url = serializers.CharField(read_only=True)
    object_id = serializers.IntegerField(min_value=1, required=True, allow_null=False)
    object_type = serializers.ChoiceField(choices=ImageFiles.OBJECT_TYPE_CHOICES, required=True,
                                          allow_null=False)
    created_by = serializers.IntegerField(min_value=1, required=False, allow_null=True, default=True)
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

    def validate_created_by(self, value):
        if value:
            return value
        r = AuthRequester()
        token = get_token_from_request(self.context['request'])
        try:
            _, auth_json = r.get_user_info(token)
            return auth_json['id']
        except BaseApiRequestError:
            raise serializers.ValidationError('Не получается получить юзера по токену, попробуйте позже')


def image_validator(value):
    CORRECT_FORMATS = ['jpg', 'jpeg', 'png', 'heic', 'gif']
    filename_splitted = value.name.split('.')
    if len(filename_splitted) < 2:
        raise serializers.ValidationError('Wrong image extension')
    if filename_splitted[-1].lower() not in CORRECT_FORMATS:
        raise serializers.ValidationError('Wrong image extension')


class ImageFilesSerializer(ImageFilesMetaSerializer):
    """
    Сериализатор изображения с метой
    """
    image = serializers.ImageField(required=True, allow_null=False, write_only=True,
                                   validators=[image_validator])

    class Meta(ImageFilesMetaSerializer.Meta):
        fields = ImageFilesMetaSerializer.Meta.fields + [
            'image',
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        MAX_SIZE = (500, 500) \
            if attrs['object_type'] not in (ImageFiles.PPIN_TYPE, ImageFiles.GPIN_TYPE) \
            else (32, 32)
        value = attrs['image']
        try:
            img = Image.open(value.file)
        except:
            raise serializers.ValidationError('Error while opening image')
        width, height = img.size
        if width <= MAX_SIZE[0] and height <= MAX_SIZE[1]:
            return value
        try:
            img.thumbnail(MAX_SIZE)
            img_bytes = BytesIO()
            img.save(img_bytes, format=img.format)
            value.file = img_bytes
            value.size = img_bytes.getbuffer().nbytes
        except:
            raise serializers.ValidationError('Error while compressing image')
        attrs['image'] = value
        return attrs

    def create(self, validated_data):
        if validated_data['object_type'] == ImageFiles.PLACE_TYPE:
            new = ImageFiles.objects.create(**validated_data)
            return new
        try:
            img = ImageFiles.objects.get(object_id=validated_data['object_id'], object_type=validated_data['object_type'])
        except ImageFiles.DoesNotExist:
            new = ImageFiles.objects.create(**validated_data)
            return new
        img.update_image(validated_data['image'].file, validated_data['image'].name)
        return img

