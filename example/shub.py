#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

if __name__ == '__main__':
    import autopath

import argparse

from example.exceptions import SemHubException
from hub.Hub import Hub
from slu.da import DialogueAct, DialogueActNBList
from slu.exceptions import DialogueActException, DialogueActItemException
from dm.common import dm_factory, get_dm_type
from utils.config import Config

'''
本程序，使用文本的方式测试DM
输入是DA
输出是DA
'''

# python 3 兼容
unicode = str
raw_input = input


class SemHub(Hub):
    """
      SemHub builds a text based testing environment for the dialogue manager components.

      It reads dialogue acts from the standard input and passes it to the selected dialogue manager.
      The output is the form dialogue acts.
    """
    hub_type = "Hub"

    def __init__(self, cfg):
        super(SemHub, self).__init__(cfg)

        dm_type = get_dm_type(cfg)
        print(dm_type)
        self.dm = dm_factory(dm_type, cfg)
        self.dm.new_dialogue()

    def parse_input_da(self, l):
        """Converts a text including a dialogue act and its probability into a dialogue act instance and float probability.

        The input text must have the following form:
            [prob] the dialogue act

        """
        print("Your Input Text is: %s" % l)
        ri = l.find(" ")  # 空格对应的index

        prob = 1.0

        if ri != -1:  # 有空格
            da = l[ri + 1:]

            try:
                prob = float(l[:ri])
            except:
                # I cannot convert the first part of the input as a float
                # Therefore, assume that all the input is a DA
                da = l
        else:
            da = l
        print("DA: %s, Prob: %.2f" % (da, prob))

        try:
            da = DialogueAct(da)
        except (DialogueActException, DialogueActItemException):
            raise SemHubException("Invalid dialogue act: s")

        return prob, da

    def output_da(self, da):
        """Prints the system dialogue act to the output."""
        print("System DA:", unicode(da))
        print()

    def input_da_nblist(self):
        """Reads an N-best list of dialogue acts from the input.

        :rtype : confusion network
        """

        self.init_readline()

        nblist = DialogueActNBList()
        i = 1
        while i < 100:
            l = raw_input("User DA %d: " % i)
            print("The type of your input is: %s" % type(l))
            if len(l) == 1 and l.startswith("."):
                print()
                break

            try:
                prob, da = self.parse_input_da(l)
            except SemHubException as e:
                print(e)
                continue

            nblist.add(prob, da)

            i += 1

        nblist.merge()
        nblist.scale()

        return nblist.get_confnet()

    def run(self):
        """Controls the dialogue manager."""
        try:
            '''
            self.cfg['Logging']['system_logger'].info("""Enter the first user dialogue act. You can enter multiple dialogue acts to create an N-best list.
            The probability for each dialogue act must be be provided before the the dialogue act itself.
            When finished, the entry can be terminated by a period ".".

            For example:

              System DA 1: 0.6 hello()
              System DA 2: 0.4 hello()&inform(type="bar")
              System DA 3: .
            """)
            '''
            while True:
                '''
                self.cfg['Logging']['session_logger'].turn("system")
                '''
                self.dm.log_state()
                sys_da = self.dm.da_out()
                self.output_da(sys_da)

                nblist = self.input_da_nblist()
                print("The type of nblist is %s" % type(nblist))
                self.dm.da_in(nblist)

                # print "#102", nblist
        except:
            '''
            self.cfg['Logging']['system_logger'].exception('Uncaught exception in SHUB process.')
            '''
            raise


#########################################################################
#########################################################################

if __name__ == '__main__':
    print("Start...")
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""
        SemHub is a text based testing environment for the dialogue manager components.

        It reads dialogue acts from the standard input and passes it to the selected dialogue manager.
        The output is the form dialogue acts.

        The program reads the default config in the resources directory ('../resources/default.cfg') config
        in the current directory.

        In addition, it reads all config file passed as an argument of a '-c'.
        The additional config files overwrites any default or previous values.;

      """)

    parser.add_argument('-c', "--configs", nargs='+',
                        help='additional configuration files')
    args = parser.parse_args()
    cfg = Config.load_configs(args.configs)

    #########################################################################
    #########################################################################

    shub = SemHub(cfg)

    shub.run()
