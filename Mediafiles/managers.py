from django.db.models import Manager


class ImageFileManager(Manager):
    """
    ORM-менеджер изображений
    """
    def get_queryset(self):
        return super().get_queryset().filter(deleted_flg=False)

    def with_deleted(self):
        return super().get_queryset()
