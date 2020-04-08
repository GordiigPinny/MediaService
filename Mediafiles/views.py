from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveDestroyAPIView, RetrieveAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import LimitOffsetPagination
from Mediafiles.models import ImageFiles
from Mediafiles.serializers import ImageFilesMetaSerializer, ImageFilesSerializer


class AddImageView(CreateAPIView):
    """
    Добавление изображения
    """
    parser_classes = (MultiPartParser, )
    serializer_class = ImageFilesSerializer


class ImageView(RetrieveDestroyAPIView):
    """
    Показ и удаление изображения по айди
    """
    serializer_class = ImageFilesSerializer

    def get_queryset(self):
        with_deleted = self.request.data.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return ImageFiles.objects.with_deleted() if with_deleted \
            else ImageFiles.objects.all()

    def perform_destroy(self, instance: ImageFiles):
        instance.soft_delete()


class ImageMetaView(RetrieveAPIView):
    """
    Получение мета-инфы по изображению
    """
    serializer_class = ImageFilesMetaSerializer

    def get_queryset(self):
        with_deleted = self.request.data.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return ImageFiles.objects.with_deleted() if with_deleted \
            else ImageFiles.objects.all()


class TypedImagesView(ListAPIView):
    """
    Список изображений для object_type и object_id
    """
    serializer_class = ImageFilesSerializer
    pagination_class = LimitOffsetPagination
    object_type_kwarg = 'object_type'
    object_id_kwarg = 'object_id'

    def get_queryset(self):
        with_deleted = self.request.data.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        all_ = ImageFiles.objects.with_deleted() if with_deleted \
            else ImageFiles.objects.all()
        return all_.filter(object_id=self.request.kwargs[self.object_id_kwarg],
                           object_type=self.request.kwargs[self.object_type_kwarg])
