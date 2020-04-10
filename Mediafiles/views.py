from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveDestroyAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.pagination import LimitOffsetPagination
from Mediafiles.models import ImageFiles
from Mediafiles.serializers import ImageFilesMetaSerializer, ImageFilesSerializer
from Mediafiles.perimissions import WriteOnlyBySuperuser, AddNewImagePermission


class AddImageView(CreateAPIView):
    """
    Добавление изображения
    """
    permission_classes = (AddNewImagePermission, )
    parser_classes = (MultiPartParser, )
    serializer_class = ImageFilesSerializer


class ImageView(RetrieveDestroyAPIView):
    """
    Показ и удаление изображения по айди
    """
    permission_classes = (WriteOnlyBySuperuser, )
    serializer_class = ImageFilesMetaSerializer

    def get_queryset(self):
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        return ImageFiles.objects.with_deleted() if with_deleted \
            else ImageFiles.objects.all()

    def perform_destroy(self, instance: ImageFiles):
        instance.soft_delete()


class TypedImagesView(ListAPIView):
    """
    Список изображений для object_type и object_id
    """
    serializer_class = ImageFilesMetaSerializer
    pagination_class = LimitOffsetPagination
    object_type_kwarg = 'object_type'
    object_id_kwarg = 'object_id'

    def get_queryset(self):
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        all_ = ImageFiles.objects.with_deleted() if with_deleted \
            else ImageFiles.objects.all()
        return all_.filter(object_id=self.kwargs[self.object_id_kwarg],
                           object_type=self.kwargs[self.object_type_kwarg])

    def get(self, request, *args, **kwargs):
        response = super().get(request, args, kwargs)
        if response.status_code != 200:
            return response
        if self.kwargs[self.object_type_kwarg] not in [x[0] for x in ImageFiles.OBJECT_TYPE_CHOICES]:
            response.status_code = 404
            return response
        with_deleted = self.request.query_params.get('with_deleted', 'False')
        with_deleted = with_deleted.lower() == 'true'
        all_ = ImageFiles.objects.with_deleted() if with_deleted else ImageFiles.objects.all()
        if not all_.filter(object_type=self.kwargs[self.object_type_kwarg],
                           object_id=self.kwargs[self.object_id_kwarg]).exists():
            response.status_code = 404
            return response
        return response
