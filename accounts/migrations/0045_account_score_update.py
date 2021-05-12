from statistics import mean
from django.db import migrations


def update_scores(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    Submission = apps.get_model('contests', 'Submission')

    for account in Account.objects.filter(score__isnull=True):
        credit_scores = account.user.credit_set.exclude(score=0).values_list('score', flat=True)
        avg_credit_score = round(mean(credit_scores)) if credit_scores else 0

        solved_problem_ids = Submission.objects.filter(owner=account.user, status='OK').values_list('problem', flat=True).distinct().order_by()
        submissions_to_success_counts = []
        for problem_id in solved_problem_ids:
            problem_submissions = Submission.objects.filter(owner=account.user, problem=problem_id)
            first_success_submission = problem_submissions.filter(status='OK').order_by('date_created')[0]
            submissions_to_success_count = problem_submissions.filter(date_created__lte=first_success_submission.date_created).count()
            submissions_to_success_counts.append(submissions_to_success_count)
        avg_submissions_to_success_count = round(mean(submissions_to_success_counts)) if submissions_to_success_counts else 0

        credits_score = round(avg_credit_score / 5, 1) if 2 < avg_credit_score < 6 else 0
        submissions_score = round(1 - (avg_submissions_to_success_count - 1) / 10, 1) if 0 < avg_submissions_to_success_count < 11 else 0
        account.score = round((credits_score + submissions_score) / 2 * 100)
        account.save()


def delete_scores(apps, schema_editor):
    Account = apps.get_model('accounts', 'Account')
    Account.objects.filter(score__isnull=False).update(score=None)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0044_account_score'),
    ]

    operations = [
        migrations.RunPython(update_scores, delete_scores)
    ]
