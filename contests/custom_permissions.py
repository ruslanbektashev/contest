import rules


@rules.predicate
def is_leader(user, objects):
    return objects['course'].leaders.filter(id=user.id).exists()


@rules.predicate
def add_contest(user, objects):
    return "/contest/create/" in objects['request'].path


@rules.predicate
def update_contest(user, objects):
    return "/contest/update" in objects['request'].path


@rules.predicate
def delete_contest(user, objects):
    return "/contest/delete" in objects['request'].path


@rules.predicate
def add_problem(user, objects):
    return "/problem/create/" in objects['request'].path


@rules.predicate
def update_problem(user, objects):
    return f"/problem/{objects['problem'].id}/update" in objects['request']


@rules.predicate
def delete_problem(user, objects):
    return f"/problem/{objects['problem'].id}/delete" in objects['request']


@rules.predicate
def start_course(user, objects):
    return f"/course/{objects['course'].id}/start/" in objects['request'].path


@rules.predicate
def update_course(user, objects):
    return f"/course/{objects['course'].id}/update" in objects['request'].path


@rules.predicate
def finish_course(user, objects):
    return f"/course/{objects['course'].id}/finish/" in objects['request'].path


@rules.predicate
def mark_attendance(user, objects):
    return "/attendance/mark" in objects['request'].path


@rules.predicate
def credit_report(user, objects):
    return "/credit/report" in objects['request'].path


@rules.predicate
def credit_update(user, objects):
    return "credit" in objects['request'].path and "update" in objects['request'].path


@rules.predicate
def view_assignment_table(user, objects):
    return "/assignment/table" in objects['request'].path


@rules.predicate
def distribute_problems(user, objects):
    return "assignment/create" in objects['request'].path or "assignment/randomize" in objects['request'].path


@rules.predicate
def view_submission_list(user, objects):
    return "/submission/list" in objects['request'].path


@rules.predicate
def update_subproblem(user, objects):
    return "/subpoblem/update" in objects['request'].path


@rules.predicate
def delete_subproblem(user, objects):
    return "subproblem/delete" in objects['request'].path


rules.add_perm("Update course", (is_leader & update_course))
rules.add_perm('Add contest', (is_leader & add_contest))
rules.add_perm('Update contest', (is_leader & update_contest))
rules.add_perm('Delete contest', (is_leader & delete_contest))
rules.add_perm('Add problem', (is_leader & add_problem))
rules.add_perm('Update problem', (is_leader & update_problem))
rules.add_perm('Delete problem', (is_leader & delete_problem))
rules.add_perm('Start course', (is_leader & start_course))
rules.add_perm('Finish course', (is_leader & finish_course))
rules.add_perm('Mark attendance', (is_leader & mark_attendance))
rules.add_perm('Distribute problems', (is_leader & distribute_problems))
rules.add_perm('View assignment table', (is_leader & view_assignment_table))
rules.add_perm('View submission list', (is_leader & view_submission_list))
rules.add_perm('Update credit', (is_leader & credit_update))
rules.add_perm('Credit report', (is_leader & credit_report))
rules.add_perm('Update subproblem', (is_leader & update_subproblem))
rules.add_perm('Delete subproblem', (is_leader & delete_subproblem))

LABELS = {'Update course': "Изменять курс",
          'Add contest': "Создавать раздел",
          'Update contest': "Изменять раздел",
          'Delete contest': "Удалять раздел",
          'Add problem': "Добавлять задачу",
          'Update problem': "Изменять задачу",
          'Delete problem': "Удалять задачу",
          'Start course': "Начинать курс",
          'Finish course': "Завершать курс",
          'Mark attendance': "Отмечать посещаемость",
          'View assignment table': "Видеть таблицу заданий ",
          'View submission list': "Видеть посылки",
          'Credit report': "Создавать ведомость",
          'Update credit': "Изменять оценки",
          'Distribute problems': "Распределять задачи",
          'Update subproblem': "Изменять подзадачи",
          'Delete subproblem': "Удалять подзадачи"}


def ru(permission_name):
    return LABELS[permission_name]