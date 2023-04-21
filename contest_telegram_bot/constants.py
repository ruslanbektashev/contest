from emoji import emojize

login_btn_text = emojize(":locked_with_key: Войти")
logout_btn_text = emojize(":left_arrow: Выйти из системы")
help_btn_text = emojize(":books: Помощь")
courses_emoji = emojize(":books:")
contest_emoji = emojize(":open_book:")
problem_emoji = emojize(":clipboard:")
bot_settings_emoji = emojize(":hammer_and_wrench:")
user_settings_emoji = emojize(":gear:")
send_emoji = emojize(':up_arrow:')
down_arrow_emoji = emojize(':down_arrow:')
selection_emoji = emojize(':blue_square:')

checked_emoji = emojize(':check_mark_button:')
unchecked_emoji = emojize(':green_square:')
cross_emoji = emojize(":cross_mark:")

comments_emoji = emojize(':speech_balloon:')
users_emoji = emojize(":bust_in_silhouette:")
problems_emoji = emojize(":bar_chart:")

hourglass_emoji = emojize(":hourglass_done:")

submission_status_emojis = {
    'OK': emojize(":green_circle:"),
    'PS': emojize(":green_circle:"),
    'TF': emojize(":yellow_circle:"),
    'TR': emojize(":yellow_circle:"),
    'WA': emojize(":yellow_circle:"),
    'NA': emojize(":yellow_circle:"),
    'TL': emojize(":red_circle:"),
    'ML': emojize(":red_circle:"),
    'CL': emojize(":red_circle:"),
    'FE': emojize(":red_circle:"),
    'SF': emojize(":red_circle:"),
    'RE': emojize(":red_circle:"),
    'CE': emojize(":red_circle:"),
    'UE': emojize(":red_circle:"),
    'PE': emojize(":red_circle:"),
    'EX': emojize(":red_circle:"),
    'EV': emojize(":blue_circle:"),
    'UN': emojize(":white_circle:"),
}
marks_emojis = {
    True: checked_emoji,
    False: cross_emoji,
}
