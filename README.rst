Nice multiple choice selection and more!

See it at:

- `pypi`_
- `GitHub`_

==============  ===============  =========  ============
VERSION         DOWNLOADS        TESTS      COVERAGE
==============  ===============  =========  ============
|pip version|   |pip downloads|  |travis|   |coveralls|
==============  ===============  =========  ============

Various ways to get user input from the command-line, including selecting
an item from a long list of choices by typing to filter.


Quick Start
===========

.. code:: python

  from asker import ask
  best_choice = ask('Which one? ', choices=choices, labels=labels)


License
=======

Copyright (c) 2016 K.C.Saff (`@kcsaff`_)

Licensed under `the MIT license`_.


.. |travis| image:: https://travis-ci.org/kcsaff/getkey.png
  :target: `Travis`_
  :alt: Travis results

.. |coveralls| image:: https://coveralls.io/repos/kcsaff/getkey/badge.png
  :target: `Coveralls`_
  :alt: Coveralls results_

.. |pip version| image:: https://img.shields.io/pypi/dd/asker.svg
    :target: https://pypi.python.org/pypi/asker
    :alt: Latest PyPI version

.. |pip downloads| image:: https://img.shields.io/pypi/v/asker.svg
    :target: https://pypi.python.org/pypi/asker
    :alt: Number of PyPI downloads

.. _pypi: https://pypi.python.org/pypi/asker
.. _GitHub: https://github.com/kcsaff/asker
.. _Travis: https://travis-ci.org/kcsaff/asker
.. _Coveralls: https://coveralls.io/r/kcsaff/asker
.. _@kcsaff: https://twitter.com/kcsaff

.. _the MIT license: http://opensource.org/licenses/MIT
