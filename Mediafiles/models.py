from django.db import models
from django.core.validators import validate_image_file_extension


def directory_path(instance, filename):
    return f'{instance.object_type}/{filename}' \
        if instance.object_type != instance.PLACE_TYPE \
        else f'{instance.object_type}/{instance.object_id}/{filename}'


class ImageFiles(models.Model):
    """
    Модель для изображений
    """
    PLACE_TYPE, GPIN_TYPE, PPIN_TYPE, ACH_TYPE, USER_TYPE = \
        'place', 'gpin', 'ppin', 'achievement', 'user'
    OBJECT_TYPE_CHOICES = (
        (PLACE_TYPE, PLACE_TYPE),
        (GPIN_TYPE, GPIN_TYPE),
        (PPIN_TYPE, PPIN_TYPE),
        (ACH_TYPE, ACH_TYPE),
        (USER_TYPE, USER_TYPE),
    )

    image = models.ImageField(upload_to=directory_path, blank=False, null=True,
                              validators=[validate_image_file_extension])
    object_id = models.PositiveIntegerField(null=False, blank=False)
    object_type = models.CharField(choices=OBJECT_TYPE_CHOICES, max_length=32)
    created_by = models.PositiveIntegerField(null=False, blank=False)
    created_dt = models.DateTimeField(auto_now_add=True)
    deleted_flg = models.BooleanField(default=False)

    @property
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None

    @property
    def image_name(self):
        if self.image and hasattr(self.image, 'name'):
            return self.image.name
        return None

    def update_image(self, file_contents, filename):
        self.image.delete(save=False)
        self.image.save(filename, file_contents)
        self.save()

    def __str__(self):
        return self.image_name or 'Empty image'
