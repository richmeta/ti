# coding: utf-8
from colorama import Fore


def red(_str, use_color=True):
    if use_color:
        return Fore.RED + _str + Fore.RESET
    else:
        return _str


def green(_str, use_color=True):
    if use_color:
        return Fore.GREEN + _str + Fore.RESET
    else:
        return _str


def yellow(_str, use_color=True):
    if use_color:
        return Fore.YELLOW + _str + Fore.RESET
    else:
        return _str


def blue(_str, use_color=True):
    if use_color:
        return Fore.BLUE + _str + Fore.RESET
    else:
        return _str
