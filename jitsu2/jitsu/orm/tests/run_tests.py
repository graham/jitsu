import unittest
import os

import jitsu.orm.tests

more_tests = ['.',
              'sqlite/']

for j in more_tests:
    for i in os.listdir(jitsu.orm.tests.__path__[0] + '/' + j):
        if i.startswith('test_') and i.endswith('.py'):
            print('execing', i)
            execfile(jitsu.orm.tests.__path__[0]+'/'+j+'/'+i)


if __name__ == '__main__':
    unittest.main()
        