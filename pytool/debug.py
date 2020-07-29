# coding=utf-8
"""
debug tools
"""
from __future__ import print_function
import pprint
import inspect

class Debug:
    debug_str_prefix = '-' * 30
    debug_str_suffix = '-' * 30
    debug_str_prefix1 = '*' * 30
    debug_str_suffix1 = '*' * 30
    debug_str_prefix2 = ''
    debug_str_suffix2 = ''

    def print(self, var, prefix='-'*30, suffix='-'*30):
        if __debug__:
            # prefix = self.debug_str_prefix1
            # suffix = self.debug_str_suffix1
            print('\n%s%s%s:\n %s' % (prefix, Debug.retrieve_name(var), suffix, var))

    def pprint(self, var, prefix='-'*30, suffix='-'*30):
        if __debug__:
            # prefix = self.debug_str_prefix1
            # suffix = self.debug_str_suffix1
            print('\n%s%s%s:\n ' % (prefix, Debug.retrieve_name(var), suffix))
            pprint.pprint(var)

    @staticmethod
    def retrieve_name(var):
        """
        Gets the name of var. Does it from the out most frame inner-wards.
        :param var: variable to get name from.
        :return: string
        """
        for fi in reversed(inspect.stack()):
            # print(fi)
            # print(dir(fi))
            names = [var_name for var_name, var_val in fi.frame.f_locals.items() if var_val is var]
            if len(names) > 0:
                return names[0]

debugger = Debug()
