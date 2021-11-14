from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from accounts.models import Account, Faculty
from contests.models import Course, Credit, Contest, Problem, SubmissionPattern, IOTest, UTTest, FNTest, Assignment, Submission

"""===================================================== Course ====================================================="""


class CourseViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    courses = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin, faculty=faculty)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.objects.create(user=student, faculty=faculty)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            cls.courses.append(course)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/course/{}/'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get(reverse('contests:course-detail', kwargs={'pk': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/course/create'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/create')
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/create')
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:course-create'))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/course/{}/update'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/update'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/{}/update'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:course-update', kwargs={'pk': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/course/{}/delete'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/delete'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/{}/delete'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:course-delete', kwargs={'pk': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)

    """==================================================== List ===================================================="""

    def test_list_view_requires_login(self):
        url = '/course/list'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_contains_all_items(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/list')
        self.assertEqual(len(resp.context['courses']), self.courses_num)


"""===================================================== Credit ====================================================="""


class CreditViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    courses = []
    credits = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            credit = Credit.objects.create(owner=admin, user=student, course=course)
            cls.credits.append(credit)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/credit/{}/update'.format(self.credits[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/credit/{}/update'.format(self.credits[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/credit/{}/update'.format(self.credits[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:credit-update', kwargs={'pk': self.credits[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/credit/{}/delete'.format(self.credits[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/credit/{}/delete'.format(self.credits[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/credit/{}/delete'.format(self.credits[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:credit-delete', kwargs={'pk': self.credits[0].id}))
        self.assertEqual(resp.status_code, 200)


"""===================================================== Contest ===================================================="""


class ContestViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    courses = []
    contests = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin, faculty=faculty)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.objects.create(user=student, faculty=faculty)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            cls.courses.append(course)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            cls.contests.append(contest)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/contest/{}/'.format(self.contests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/contest/{}/'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get(reverse('contests:contest-detail', kwargs={'pk': self.contests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/course/{}/contest/create'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/contest/create'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/{}/contest/create'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:contest-create', kwargs={'course_id': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/contest/{}/update'.format(self.contests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/contest/{}/update'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/contest/{}/update'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:contest-update', kwargs={'pk': self.contests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/contest/{}/delete'.format(self.contests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/contest/{}/delete'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/contest/{}/delete'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:contest-delete', kwargs={'pk': self.contests[0].id}))
        self.assertEqual(resp.status_code, 200)


"""===================================================== Problem ===================================================="""


class ProblemViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    contests = []
    problems = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin, faculty=faculty)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.objects.create(user=student, faculty=faculty)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            cls.contests.append(contest)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/problem/{}/'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get(reverse('contests:problem-detail', kwargs={'pk': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/contest/{}/problem/create/Program'.format(self.contests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/contest/{}/problem/create/Program'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/contest/{}/problem/create/Program'.format(self.contests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:problem-create', kwargs={'contest_id': self.contests[0].id,
                                                                          'type': 'Program'}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/problem/{}/update'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/update'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/update'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:problem-update', kwargs={'pk': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/problem/{}/delete'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/delete'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/delete'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:problem-delete', kwargs={'pk': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)


"""=============================================== SubmissionPattern ================================================"""


class SubmissionPatternViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    problems = []
    submission_patterns = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        User.objects.create_user(cls.student, 'student@localhost', cls.student)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)
            submission_pattern = SubmissionPattern.objects.create(owner=admin, title="Test SubmissionPattern %s" % i,
                                                                  description="Test Description %s" % i)
            submission_pattern.problems.add(problem)
            cls.submission_patterns.append(submission_pattern)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/submission/pattern/{}/'.format(self.submission_patterns[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/submission/pattern/{}/'.format(self.submission_patterns[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/submission/pattern/{}/'.format(self.submission_patterns[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-pattern-detail', kwargs={'pk': self.submission_patterns[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/problem/{}/submission/pattern/create'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/submission/pattern/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/submission/pattern/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-pattern-create', kwargs={'problem_id': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/submission/pattern/{}/update'.format(self.submission_patterns[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/submission/pattern/{}/update'.format(self.submission_patterns[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/submission/pattern/{}/update'.format(self.submission_patterns[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-pattern-update', kwargs={'pk': self.submission_patterns[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/submission/pattern/{}/delete'.format(self.submission_patterns[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/submission/pattern/{}/delete'.format(self.submission_patterns[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/submission/pattern/{}/delete'.format(self.submission_patterns[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-pattern-delete', kwargs={'pk': self.submission_patterns[0].id}))
        self.assertEqual(resp.status_code, 200)


"""===================================================== IOTest ====================================================="""


class IOTestViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    problems = []
    iotests = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        User.objects.create_user(cls.student, 'student@localhost', cls.student)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)
            iotest = IOTest.objects.create(owner=admin, problem=problem, title="Test IOTest %s" % i,
                                           input="Test Input %s" % i, output="Test Output %s" % i)
            cls.iotests.append(iotest)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/iotest/{}/'.format(self.iotests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/iotest/{}/'.format(self.iotests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/iotest/{}/'.format(self.iotests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:iotest-detail', kwargs={'pk': self.iotests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/problem/{}/iotest/create'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/iotest/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/iotest/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:iotest-create', kwargs={'problem_id': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/iotest/{}/update'.format(self.iotests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/iotest/{}/update'.format(self.iotests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/iotest/{}/update'.format(self.iotests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:iotest-update', kwargs={'pk': self.iotests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/iotest/{}/delete'.format(self.iotests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/iotest/{}/delete'.format(self.iotests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/iotest/{}/delete'.format(self.iotests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:iotest-delete', kwargs={'pk': self.iotests[0].id}))
        self.assertEqual(resp.status_code, 200)


"""===================================================== UTTest ====================================================="""


class UTTestViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    problems = []
    uttests = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        User.objects.create_user(cls.student, 'student@localhost', cls.student)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)
            uttest = UTTest.objects.create(owner=admin, problem=problem, title="Test UTTest %s" % i)
            cls.uttests.append(uttest)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/uttest/{}/'.format(self.uttests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/uttest/{}/'.format(self.uttests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/uttest/{}/'.format(self.uttests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:uttest-detail', kwargs={'pk': self.uttests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/problem/{}/uttest/create'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/uttest/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/uttest/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:uttest-create', kwargs={'problem_id': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/uttest/{}/update'.format(self.uttests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/uttest/{}/update'.format(self.uttests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/uttest/{}/update'.format(self.uttests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:uttest-update', kwargs={'pk': self.uttests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/uttest/{}/delete'.format(self.uttests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/uttest/{}/delete'.format(self.uttests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/uttest/{}/delete'.format(self.uttests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:uttest-delete', kwargs={'pk': self.uttests[0].id}))
        self.assertEqual(resp.status_code, 200)


"""===================================================== FNTest ====================================================="""


class FNTestViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    problems = []
    fntests = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        User.objects.create_user(cls.student, 'student@localhost', cls.student)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)
            fntest = FNTest.objects.create(owner=admin, title="Test FNTest %s" % i, handler="Test Handler %s" % i)
            fntest.problems.add(problem)
            cls.fntests.append(fntest)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/fntest/{}/'.format(self.fntests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/fntest/{}/'.format(self.fntests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/fntest/{}/'.format(self.fntests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:fntest-detail', kwargs={'pk': self.fntests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/problem/{}/fntest/create'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/fntest/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/fntest/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:fntest-create', kwargs={'problem_id': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/fntest/{}/update'.format(self.fntests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/fntest/{}/update'.format(self.fntests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/fntest/{}/update'.format(self.fntests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:fntest-update', kwargs={'pk': self.fntests[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/fntest/{}/delete'.format(self.fntests[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/fntest/{}/delete'.format(self.fntests[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/fntest/{}/delete'.format(self.fntests[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:fntest-delete', kwargs={'pk': self.fntests[0].id}))
        self.assertEqual(resp.status_code, 200)


"""=================================================== Assignment ==================================================="""


class AssignmentViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    courses_num = 8
    courses = []
    problems = []
    assignments = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin, faculty=faculty)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.students.create(user=student, faculty=faculty)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            cls.courses.append(course)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)
            assignment = Assignment.objects.create(owner=admin, user=student, problem=problem)
            cls.assignments.append(assignment)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/assignment/{}/'.format(self.assignments[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/assignment/{}/'.format(self.assignments[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-detail', kwargs={'pk': self.assignments[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/course/{}/assignment/create'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/assignment/create'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/{}/assignment/create'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-create', kwargs={'course_id': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=============================================== CreateRandomSet =============================================="""

    def test_create_random_set_view_requires_login(self):
        url = '/course/{}/assignment/randomize'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_random_set_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/assignment/randomize'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_random_set_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/{}/assignment/randomize'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_random_set_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-randomize', kwargs={'course_id': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Update ==================================================="""

    def test_update_view_requires_login(self):
        url = '/assignment/{}/update'.format(self.assignments[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_update_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/assignment/{}/update'.format(self.assignments[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_update_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/assignment/{}/update'.format(self.assignments[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_update_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-update', kwargs={'pk': self.assignments[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/assignment/{}/delete'.format(self.assignments[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/assignment/{}/delete'.format(self.assignments[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/assignment/{}/delete'.format(self.assignments[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-delete', kwargs={'pk': self.assignments[0].id}))
        self.assertEqual(resp.status_code, 200)

    """==================================================== List ===================================================="""

    def test_list_view_requires_login(self):
        url = '/assignment/list'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/assignment/list')
        self.assertEqual(resp.status_code, 200)

    def test_list_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-list'))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Table ===================================================="""

    def test_table_view_requires_login(self):
        url = '/course/{}/assignment/table'.format(self.courses[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_table_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/course/{}/assignment/table'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_table_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/course/{}/assignment/table'.format(self.courses[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_table_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:assignment-table', kwargs={'course_id': self.courses[0].id}))
        self.assertEqual(resp.status_code, 200)


"""=================================================== Submission ==================================================="""


class SubmissionViewsTest(TestCase):
    admin = 'admin'
    student = 'student'
    other_student = 'other_student'
    courses_num = 8
    courses = []
    problems = []
    submissions = []

    @classmethod
    def setUpTestData(cls):
        faculty = Faculty.objects.create(name="Test Fac")
        admin = User.objects.create_superuser(cls.admin, 'admin@localhost', cls.admin)
        Account.objects.create(user=admin, faculty=faculty)
        student = User.objects.create_user(cls.student, 'student@localhost', cls.student)
        Account.students.create(user=student, faculty=faculty)
        User.objects.create_user(cls.other_student, 'other_student@localhost', cls.other_student)
        for i in range(1, cls.courses_num + 1):
            course = Course.objects.create(owner=admin, faculty=faculty, title_official="Test Course %s" % i,
                                           description="Test Description %s" % i, level=i)
            cls.courses.append(course)
            contest = Contest.objects.create(owner=admin, course=course, title="Test Contest %s" % i,
                                             description="Test Description %s" % i)
            problem = Problem.objects.create(owner=admin, contest=contest, title="Test Problem %s" % i,
                                             description="Test Description %s" % i)
            cls.problems.append(problem)
            submission = Submission.objects.create(owner=student, problem=problem)
            cls.submissions.append(submission)

    """=================================================== Detail ==================================================="""

    def test_detail_view_requires_login(self):
        url = '/submission/{}/'.format(self.submissions[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_detail_view_requires_ownership(self):
        self.client.login(username=self.other_student, password=self.other_student)
        resp = self.client.get('/submission/{}/'.format(self.submissions[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_detail_view_accessible_by_owner(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/submission/{}/'.format(self.submissions[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/submission/{}/'.format(self.submissions[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-detail', kwargs={'pk': self.submissions[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Create ==================================================="""

    def test_create_view_requires_login(self):
        url = '/problem/{}/submission/create'.format(self.problems[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_create_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/problem/{}/submission/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_create_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/problem/{}/submission/create'.format(self.problems[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_create_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-create', kwargs={'problem_id': self.problems[0].id}))
        self.assertEqual(resp.status_code, 200)

    """=================================================== Delete ==================================================="""

    def test_delete_view_requires_login(self):
        url = '/submission/{}/delete'.format(self.submissions[0].id)
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_delete_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/submission/{}/delete'.format(self.submissions[0].id))
        self.assertEqual(resp.status_code, 403)

    def test_delete_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/submission/{}/delete'.format(self.submissions[0].id))
        self.assertEqual(resp.status_code, 200)

    def test_delete_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-delete', kwargs={'pk': self.submissions[0].id}))
        self.assertEqual(resp.status_code, 200)

    """==================================================== List ===================================================="""

    def test_list_view_requires_login(self):
        url = '/submission/list'
        resp = self.client.get(url)
        self.assertRedirects(resp, settings.LOGIN_URL + '?next=' + url)

    def test_list_view_requires_permission(self):
        self.client.login(username=self.student, password=self.student)
        resp = self.client.get('/submission/list')
        self.assertEqual(resp.status_code, 403)

    def test_list_view_accessible_by_url(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get('/submission/list')
        self.assertEqual(resp.status_code, 200)

    def test_list_view_accessible_by_name(self):
        self.client.login(username=self.admin, password=self.admin)
        resp = self.client.get(reverse('contests:submission-list'))
        self.assertEqual(resp.status_code, 200)
