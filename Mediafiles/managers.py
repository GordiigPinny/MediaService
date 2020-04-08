from django.db.models import Manager


class ImageFileManager(Manager):
    """
    ORM-менеджер изображений
    """
    def get_queryset(self):
        super().filter(deleted_flg=False)

    def with_deleted(self):
        super().get_queryset()
