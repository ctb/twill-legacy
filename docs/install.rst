.. _install:

================
Installing twill
================

The recommended way to install twill is to use pip_::

   pip install twill

You can also install it directly from the distribution tar.gz file
by unpacking the .tar.gz file and running::

   python setup.py install



Troubleshooting your installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The first and only thing you should do before creating an issue_ on the
`GitHub project page`_ is to see if you have the twill package installed
correctly::

   $ python
   >>> import twill.shell
   >>> twill.shell.main()

(This should drop you into the twill shell irrespective of whether 'twill'
is on your path.)  **If this works**, twill is installed correctly and you
just need to adjust your path (see above for examples). If you still
need help, or the above code doesn't work, please copy and paste the results
of entering the above code into your e-mail to the list -- thanks!

Upgrading twill
~~~~~~~~~~~~~~~

If you don't want to download a new tar.gz file, you can use
pip to upgrade twill. To get the latest release, use::

   pip install -U twill

To download the latest development release (which is usually pretty
stable) use::

   pip install -U https://github.com/twill-tools/twill/archive/master.zip

.. _pip: https://docs.python.org/3/installing/index.html
.. _issue: https://github.com/twill-tools/twill/issues
.. _GitHub project page: https://github.com/twill-tools/twill

