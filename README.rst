=================================
ti -- A silly simple time tracker
=================================

``ti`` is a small command line time-tracking application.
Simple basic usage looks like this::

    $ ti on my-project
    $ ti fin

You can also give it human-readable times::

    $ ti on my-project 30mins ago

``ti`` sports many other cool features. Read along to discover.

Wat?
====

``ti`` is a simple command line time tracker. It has been completely rewritten
in Python (originally a bash script) and has (almost) complete test coverage. It
is inspired by `timed <http://adeel.github.com/timed>`_, which is a nice project
that you should check out if you don't like ``ti``. ``ti`` also takes
inspiration from the simplicity of `t <http://stevelosh.com/projects/t/>`_.

If a time-tracking tool makes me think for more than 3-5 seconds, I lose my line
of thought and forget what I was doing. This is why I created ``ti``. With
``ti``, you'll be as fast as you can type, which you should be good with anyway.

The most important part about ``ti`` is that it provides just a few commands to
manage your time-tracking and then gets out of your way.

All data is saved in a JSON file ,``~/.ti-sheet``. (This can be changed using the
``$SHEET_FILE``  environment variable.) The JSON is easy to access and can be
processed into other more stylized documents. Some ideas:

- Read your JSON file to generate beautiful HTML reports.
- Build monthly statistics based on tags or tasks.
- Read your currently working project and display it in your terminal prompt.
  Maybe even with the number of hours you've been working.

It's *your* data.

Oh and by the way, the source is a fairly small Python script, so if you know
Python, you may want to skim over it to get a better feel of how it works.

*Note*: If you have used the previous bash version of ``ti``, which was horribly
tied up to only work on Linux, you might notice the lack of plugins in this
Python version. I am not really missing them, so I might not add them. If anyone
has any interesting use cases for it, I'm willing to consider.

Usage
=====

Here's the minimal usage style::

    $ ti on my-project
    Start working on my-project.

    $ ti status
    You have been working on my-project for less than a minute.

    $ ti fin
    So you stopped working on my-project.

``on`` and ``fin`` can take a time (format described further down) at which to
apply the action::

    $ ti on another-project 2 hours ago
    Start working on another-project.

    $ ti s
    You have been working on another-project for about 2 hours.

    $ ti fin 30 minutes ago
    So you stopped working on another-project.

Also illustrating in the previous example is short aliases of all commands,
their first letter. Like, ``s`` for ``status``, ``o`` for ``on``,
``f`` for ``fin``, etc.

Put brief notes on what you've been doing::

    $ ti note waiting for Napoleon to take over the world
    $ ti n another simple note for demo purposes

Tag your activities for fun and profit::

    $ ti tag imp

Get a log of all activities with the ``log`` (or ``l``) command::

    $ ti log

Command reference
=================

Run ``ti -h`` (or ``--help`` or ``help`` or just ``h``)
to get a short command summary of commands.

``on``
------

- Short: ``o``
- Syntax: ``ti (o|on) <name> [<time>...]``

Start tracking time for the project/activity given by `<name>`. For example::

    ti on conquest

tells ``ti`` to start tracking for the activity ``conquest`` *now*.
You can optionally specify a relative time in the past like so::

    ti on conquest 10mins ago

The format of the time is detailed further below.

``fin``
-------

- Short: ``f``
- Syntax: ``ti (f|fin) [<time>...]``

End tracking for the current activity *now*. Just like with ``on`` command
above, you can give an optional time to the past. Example::

    ti fin 10mins ago

tells ``ti`` that you finished working on the current activity at, well, 10
minutes ago.

``status``
----------

- Short: ``s``
- Syntax: ``ti (s|status)``

Gives short human-readable message on the current status, i.e., whether anything
is being tracked currently or not. Example::

    $ ti on conqering-the-world
    Start working on conqering-the-world.
    $ ti status
    You have been working on `conqering-the-world` for less than a minute.

``tag``
-------

- Short: ``t``
- Syntax: ``ti (t|tag) <tag>...``

This command adds the given tags to the current activity. Tags are not currently
used within the ``ti`` time tracker, but they will be saved in the JSON data
file. You may use them for whatever purposes you like.

For example, if you have a script to generate a HTML report from your ``ti``
data, you could tag some activities with a tag like ``red`` or ``important`` so
that activity will appear in red in the final HTML report.

Use it like::

    ti tag red for-joe

adds the tags ``red`` and ``for-joe`` to the current activitiy. You can specify
any number of tags.

Tags are currently for your purpose. Use them as you see fit.

``note``
--------

- Short: ``n``
- Syntax: ``ti (n|note) <note-text>...``

This command adds a note on the current activity. Again, like tags, this has no
significance with the time tracking aspect of ``ti``. This is for your own
recording purposes and for the scripts your write to process your ``ti`` data.

Use it like::

    ti note Discuss this with the other team.

adds the note ``Discuss this with the other team.`` to the current activity.

``log``
-------

- Short: ``l1``
- Syntax: ``ti (l|log) [today]``

Gives a table like representation of all activities and total time spent on each
of them.

Time format
===========

Currently only the following are recognized. If there is something that is not
handled, but should be, please open an issue about it or a pull request
(function in question is ``parse_time``)

- *n* seconds ago can be written as:
    - *n* seconds ago
    - *n* second ago
    - *n* secs ago
    - *n* sec ago
    - *n* s ago
    - ``a`` in place of *n* in all above cases, to mean 1 second.
    - E.g., ``10s ago``, ``a sec ago`` ``25 seconds ago``, ``25seconds ago``.

- *n* minutes ago can be written as:
    - *n* minutes ago
    - *n* minute ago
    - *n* mins ago
    - *n* min ago
    - ``a`` in place of *n* in all above cases, to mean 1 minute.
    - E.g., ``5mins ago``, ``a minute ago``, ``10 minutes ago``.

- *n* hours ago can be written as:
    - *n* hours ago
    - *n* hour ago
    - *n* hrs ago
    - *n* hr ago
    - ``a`` or ``an`` in place of *n* in all above cases, to mean 1 hour.
    - E.g., ``an hour ago``, ``an hr ago``, ``2hrs ago``.

- *n* days ago can be written as:
    - *n* days ago
    - *n* ds ago
    - ``a`` in place of *n* in all above cases, to mean 1 day.
    - E.g., ``a day ago``, ``2ds ago``.

Where *n* is an arbitrary number and any number of spaces between *n* and the
time unit are allowed (including zero spaces).

Status
======

The project is in beta. If you find any bug or have any feedback, please do open
`a GitHub issue <https://github.com/tbekolay/ti/issues>`_.


Gimme!
======

You can download ``ti`` `from the source on
GitHub <https://raw.github.com/tbekolay/ti/master/bin/ti>`_.

- Put it somewhere in your ``$PATH`` and make sure it has executable permissions.
- Install ``pyyaml`` using the command ``pip install --user pyyaml``.
- Install ``colorama`` using the command ``pip install --user colorama``.

After that, ``ti`` should be working fine.

Also, visit the `project page on GitHub <https://github.com/tbekolay/ti>`_ for
any further details.

Who?
====

Originally created and fed by Shrikant Sharat
(`@sharat87 <https://twitter.com/#!sharat87>`_).
Now forked and maintained by Trevor Bekolay
(`@tbekolay <https://github.com/tbekolay>`_) and friends on GitHub.

License
=======

`MIT License <http://mitl.sharats.me>`_.
