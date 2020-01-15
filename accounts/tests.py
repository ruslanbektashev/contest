from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account, make_activities, Activity, Announcement


class AccountViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    accounts_num = 5
    accounts = []

    @classmethod
    def setUpTestData(cls):
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.objects.create(user=student)
        for i in range(1, cls.accounts_num + 1):
            user = User.objects.create_user(cls.student + '_%s' % i, 'student_%s@localhost' % i, cls.student + '_%s' % i)
            account = Account.objects.create(user=user)
            cls.accounts.append(account)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/accounts/account/{}/'.format(self.accounts[0].pk)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_ownership(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/account/{}/'.format(self.accounts[0].pk))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_owner(self):
        self.client.login(username=self.accounts[0].user.username, password=self.accounts[0].user.username)
        resp = self.client.get('/accounts/account/{}/'.format(self.accounts[0].pk))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/account/{}/'.format(self.accounts[0].pk))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:account-detail', kwargs={'pk': self.accounts[0].pk}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/accounts/account/create/set'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/account/create/set')
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/account/create/set')
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:account-create-set'))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/accounts/account/{}/update'.format(self.accounts[0].pk)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/account/{}/update'.format(self.accounts[0].pk))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_owner(self):
        self.client.login(username=self.accounts[0].user.username, password=self.accounts[0].user.username)
        resp = self.client.get('/accounts/account/{}/update'.format(self.accounts[0].pk))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/account/{}/update'.format(self.accounts[0].pk))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:account-update', kwargs={'pk': self.accounts[0].pk}))
        self.assertEqual(resp.status_code, 200)

    """==================================================== List ===================================================="""

    def test_list_view_requires_login(self):
        url = '/accounts/account/list'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/account/list')
        self.assertEqual(resp.status_code, 403)

    def test_list_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/account/list')
        self.assertEqual(resp.status_code, 200)

    def test_list_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:account-list'))
        self.assertEqual(resp.status_code, 200)

    """================================================ Credentials ================================================="""

    def test_credentials_view_requires_login(self):
        url = '/accounts/account/credentials'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_credentials_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/account/credentials')
        self.assertEqual(resp.status_code, 403)

    def test_credentials_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/account/credentials')
        self.assertEqual(resp.status_code, 200)

    def test_credentials_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:account-credentials'))
        self.assertEqual(resp.status_code, 200)


class ActivityViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    activities_num = 5

    @classmethod
    def setUpTestData(cls):
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.objects.create(user=student)
        new_activities = []
        for i in range(1, cls.activities_num + 1):
            new_activities += make_activities(admin, student, "Test Activity %s" % i)
        Activity.objects.bulk_create(new_activities)

    """==================================================== List ===================================================="""

    def test_list_view_requires_login(self):
        url = '/accounts/activity/list'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/activity/list')
        self.assertEqual(resp.status_code, 200)

    def test_list_view_contains_all_activities(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/activity/list')
        self.assertEqual(len(resp.context['activities']), self.activities_num)

    def test_list_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:activity-list'))
        self.assertEqual(resp.status_code, 200)


class AnnouncementViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    announcements_num = 5
    announcements = []

    @classmethod
    def setUpTestData(cls):
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.objects.create(user=student)
        for i in range(1, cls.announcements_num + 1):
            announcement = Announcement.objects.create(owner=admin, title="Test Announcement %s" % i,
                                                       text="Test Text %s" % i)
            cls.announcements.append(announcement)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/accounts/announcement/{}/'.format(self.announcements[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/announcement/{}/'.format(self.announcements[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/announcement/{}/'.format(self.announcements[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:announcement-detail', kwargs={'pk': self.announcements[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/accounts/announcement/create'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/announcement/create')
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/announcement/create')
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:announcement-create'))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/accounts/announcement/{}/update'.format(self.announcements[0].pk)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/announcement/{}/update'.format(self.announcements[0].pk))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/announcement/{}/update'.format(self.announcements[0].pk))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:announcement-update', kwargs={'pk': self.announcements[0].pk}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/accounts/announcement/{}/delete'.format(self.announcements[0].pk)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/accounts/announcement/{}/delete'.format(self.announcements[0].pk))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/announcement/{}/delete'.format(self.announcements[0].pk))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:announcement-delete', kwargs={'pk': self.announcements[0].pk}))
        self.assertEqual(resp.status_code, 200)

    """==================================================== List ===================================================="""

    def test_list_view_requires_login(self):
        url = '/accounts/announcement/list'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/announcement/list')
        self.assertEqual(resp.status_code, 200)

    def test_list_view_contains_all_announcements(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/accounts/announcement/list')
        self.assertEqual(len(resp.context['announcements']), self.announcements_num)

    def test_list_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('accounts:announcement-list'))
        self.assertEqual(resp.status_code, 200)
