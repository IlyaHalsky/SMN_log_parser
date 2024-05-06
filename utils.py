from termcolor import colored


def green(text):
    return colored(text, 'green')


def red(text):
    return colored(text, 'red')


def yellow(text):
    return colored(text, 'yellow')


def blue(text):
    return colored(text, 'blue')


def cyan(text):
    return colored(text, 'cyan')


def magenta(text):
    return colored(text, 'magenta')


def light_red(text):
    return colored(text, 'light_red')


def light_green(text):
    return colored(text, 'light_green')


def light_yellow(text):
    return colored(text, 'light_yellow')


def light_blue(text):
    return colored(text, 'light_blue')


def light_magenta(text):
    return colored(text, 'light_magenta')


def light_cyan(text):
    return colored(text, 'light_cyan')


def grey(text):
    return colored(text, 'grey')


def on_green(text):
    return colored(text, on_color='on_green')


def on_red(text):
    return colored(text, on_color='on_red')


def on_yellow(text):
    return colored(text, on_color='on_yellow')


color_palette = {
    0: green,
    1: red,
    2: yellow,
    3: blue,
    4: magenta,
    5: cyan,
    6: light_red,
    7: light_green,
    8: light_yellow,
    9: light_blue,
    10: light_magenta,
    11: light_cyan,
    12: grey,
    13: on_green
}


def colorize(text, color: int):
    return color_palette[color](text)
