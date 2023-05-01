from emoji import emojize

login_btn_text = emojize(":locked_with_key: Войти")
logout_btn_text = emojize(":left_arrow: Выйти из системы")
help_btn_text = emojize(":books: Помощь")
courses_emoji = emojize(":books:")
contest_emoji = emojize(":open_book:")
problem_emoji = emojize(":clipboard:")
bot_settings_emoji = emojize(":hammer_and_wrench:")
user_settings_emoji = emojize(":gear:")

back_emoji = emojize(':left_arrow:')
send_emoji = emojize(':up_arrow:')
down_arrow_emoji = emojize(':down_arrow:')

plus_emoji = emojize(':plus:')

info_emoji = emojize(":information:")

selection_emoji = emojize(':blue_square:')

checked_emoji = emojize(':check_mark_button:')
unchecked_emoji = emojize(':green_square:')
cross_emoji = emojize(":cross_mark:")

filled_progress_emoji = emojize(':green_square:')
empty_progress_emoji = emojize(":white_large_square:")

comments_emoji = emojize(':speech_balloon:')
little_white_square_emoji = emojize(':white_small_square:')

users_emoji = emojize(":bust_in_silhouette:")
problems_emoji = emojize(":bar_chart:")
loudspeaker_emoji = emojize(":loudspeaker:")

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
check_emojis = {
    True: checked_emoji,
    False: unchecked_emoji,
}
drop_down_list_emojis = {
    1: emojize(':downwards_button:'),
    0: emojize(':play_button:')
}
