from shutil import rmtree
from django.conf import settings
from TestUtils.models import BaseTestCase, APIClient
from Mediafiles.models import ImageFiles


class AddImageViewTestCase(BaseTestCase):
    """
    Тесты для добавления картинки
    """
    def setUp(self):
        super().setUp()
        self.path = self.url_prefix + 'images/'
        self.data_201_user = {
            'object_id': 1,
            'object_type': ImageFiles.USER_TYPE,
            'created_by': self.user.id,
            'image': open('TestUtils/testcat.jpg', 'rb'),
        }
        self.data_201_place = {
            'object_id': 1,
            'object_type': ImageFiles.PLACE_TYPE,
            'created_by': self.user.id,
            'image': open('TestUtils/testcat.jpg', 'rb'),
        }
        self.data_201_pin = {
            'object_id': 1,
            'object_type': ImageFiles.PPIN_TYPE,
            'created_by': self.user.id,
            'image': open('TestUtils/testcat.jpg', 'rb'),
        }
        self.data_201_user = {
            'object_id': 1,
            'object_type': ImageFiles.USER_TYPE,
            'created_by': self.user.id,
            'image': open('TestUtils/testcat.jpg', 'rb'),
        }
        self.data_201_no_created_by = {
            'object_id': 1,
            'object_type': ImageFiles.USER_TYPE,
            'image': open('TestUtils/testcat.jpg', 'rb'),
        }
        self.data_400_1 = {
            'object_id': 1,
        }
        self.data_400_2 = {
            'object_id': 1,
            'object_type': 'Nope',
            'created_by': self.user.id,
            'image': open('TestUtils/testcat.jpg', 'rb'),
        }
        self.data_400_3 = {
            'object_id': 1,
            'object_type': ImageFiles.USER_TYPE,
            'created_by': self.user.id,
            'image': open('TestUtils/testfile.txt', 'rb'),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        rmtree(settings.MEDIA_ROOT + '/test/', ignore_errors=True)

    def testPost201_OK(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_user)
        self.assertEqual(response.status_code, 201, msg='Wrong status code')
        resp_json = response.json()
        self.fields_test(resp_json, ['id', 'object_id', 'object_type', 'created_by', 'image_url', 'created_dt',
                                     'deleted_flg'], allow_extra_fields=False)

    def testPost201_NoCreatedBy(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_no_created_by)
        self.assertEqual(response.status_code, 201, msg='Wrong status code')
        resp_json = response.json()
        self.fields_test(resp_json, ['id', 'object_id', 'object_type', 'created_by', 'image_url', 'created_dt',
                                     'deleted_flg'], allow_extra_fields=False)

    def testPost201_Place(self):
        client = APIClient()
        self.token.set_role(self.token.ROLES.MODERATOR)
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_place)
        self.assertEqual(response.status_code, 201, msg='Wrong status code')

    def testPost201_Pin(self):
        client = APIClient()
        self.token.set_role(self.token.ROLES.SUPERUSER)
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_pin)
        self.assertEqual(response.status_code, 201, msg='Wrong status code')

    def testPost201_ChangeAvatar(self):
        client = APIClient()
        self.token.set_role(self.token.ROLES.USER)
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_user)
        self.assertEqual(response.status_code, 201, msg='Wrong status code')
        self.data_201_user['image'] = open('TestUtils/testcat.jpg', 'rb')
        response = client.post(path=self.path, data=self.data_201_user)
        self.assertEqual(response.status_code, 201, msg='Wrong status code')


    def testPost401_403_PlaceNotModerator(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_place)
        self.assertTrue(response.status_code in [401, 403], msg='Wrong status code')

    def testPost401_403_PinNotSuperuser(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_201_pin)
        self.assertTrue(response.status_code in [401, 403], msg='Wrong status code')

    def testPost400_WrongJSON(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_400_1)
        self.assertEqual(response.status_code, 400, msg='Wrong status code')

    def testPost400_WrongObjectType(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_400_2)
        self.assertEqual(response.status_code, 400, msg='Wrong status code')

    def testPost400_NotAnImage(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=self.token.token)
        response = client.post(path=self.path, data=self.data_400_3)
        self.assertEqual(response.status_code, 400, msg='Wrong status code')


class ImageViewTestCase(BaseTestCase):
    """
    Тесты для /images/<pk>/
    """
    def setUp(self):
        super().setUp()
        self.image = ImageFiles.objects.create(image='TestUtils/testcat.jpg', object_type=ImageFiles.PLACE_TYPE,
                                               object_id=1, created_by=self.user.id)
        self.path = self.url_prefix + f'images/{self.image.id}/'
        self.path_404 = self.url_prefix + f'images/{self.image.id + 10000}/'

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.assertEqual(response['id'], self.image.id, msg='Response has wrong instance')

    def testGet200_WithDeleted(self):
        self.image.soft_delete()
        _ = self.get_response_and_check_status(url=self.path + '?with_deleted=True')

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404, expected_status_code=404)

    def testGet404_NoDeletedQueryParam(self):
        self.image.soft_delete()
        _ = self.get_response_and_check_status(url=self.path, expected_status_code=404)

    def testDelete204_OK(self):
        self.token.set_role(self.token.ROLES.SUPERUSER)
        _ = self.delete_response_and_check_status(url=self.path)

    def testDelete401_403_NotSuperuser(self):
        _ = self.delete_response_and_check_status(url=self.path, expected_status_code=[401, 403])

    def testDelete404_WrongId(self):
        self.token.set_role(self.token.ROLES.SUPERUSER)
        _ = self.delete_response_and_check_status(url=self.path_404, expected_status_code=404)


class TypedImageViewTestCase(BaseTestCase):
    """
    Тесты для /images/<object_type>/<object_id>/
    """
    def setUp(self):
        super().setUp()
        self.image = ImageFiles.objects.create(image='TestUtils/testcat.jpg', object_type=ImageFiles.PLACE_TYPE,
                                               object_id=1, created_by=self.user.id)
        self.path = self.url_prefix + f'images/{self.image.object_type}/{self.image.object_id}/'
        self.path_404_1 = self.url_prefix + f'images/nope/{self.image.object_id}/'
        self.path_404_2 = self.url_prefix + f'images/{ImageFiles.USER_TYPE}/{self.image.object_id}/'

    def testGet200_OK(self):
        response = self.get_response_and_check_status(url=self.path)
        self.list_test(response, ImageFiles)

    def testGet404_WrongType(self):
        _ = self.get_response_and_check_status(url=self.path_404_1, expected_status_code=404)

    def testGet404_WrongId(self):
        _ = self.get_response_and_check_status(url=self.path_404_2, expected_status_code=404)