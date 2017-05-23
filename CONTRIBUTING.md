# Contributing

Hello! Thank you for choosing to help contribute to one of the Cloudreach OpenSource projects. There are many ways you can contribute and help is always welcome.  We simply ask that you follow the following contribution policies.

- [Submit a Bug Report](#submit_a_bug_report)
- [Enhancement Proposal](#enhancement_proposal)
- [Contributing Code](#contributing_code)

## Submit a Bug Report

Note: DO NOT include your credentials in ANY code examples, descriptions, or media you make public.

Before submitting a bug, please check our [issues page](https://github.com/cloudreach/aws-lambda-es-cleanup/issues) to see if it's already been reported.

When reporting a bug, fill out the required template, and please include as much detail as possible as it helps us resolve issues faster.

## Enhancement Proposal

Enhancement proposals should:

* Use a descriptive title.
* Provide a step-by-step description of the suggested enhancement.
* Provide specific examples to demonstrate the steps.
* Describe the current behaviour and explain which behaviour you expected to see instead.
* Keep the scope as narrow as possible, to make it easier to implement.

Remember that this is a volunteer-driven project, and that contributions are welcome.

## Contributing Code

Contributions should be made in response to a particular GitHub Issue. We find it easier to review code if we've already discussed what it should do, and assessed if it fits with the wider codebase.

A good pull request:

* Is clear.
* Works across all supported version of Python.
* Complies with the existing codebase style ([flake8](http://flake8.pycqa.org/en/latest/), [pylint](https://www.pylint.org/)).
* Includes [docstrings](https://www.python.org/dev/peps/pep-0257/) and comments for unintuitive sections of code.
* Includes documentation for new features.
* Is appropriately licensed (Apache 2.0).



# Get Started

* Clone the repository locally:

```bash
    $ git clone git@github.com:cloudreach/aws-lambda-es-cleanup.git
```

* Install your local copy into a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/). Assuming you have virtualenv installed, this is how you set up your fork for local development:

```bash
    $ cd aws-lambda-es-cleanup/
    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt
    $ pip install -e .
```

* Create a branch for local development:

```bash
    $ git checkout -b branch-<GitHub issue number>
```

* Make sure the changes comply with the pull request guidelines in the section on [Contributing Code](#contributing_code).

* Commit your changes:

```bash
    $ git add .
    $ git commit
```

* Commit messages should follow [these guidelines](https://github.com/erlang/otp/wiki/Writing-good-commit-messages).

* Push your branch to GitHub:

```bash
    $ git push origin <description of pull request>
```

* Submit a pull request through the GitHub website.


Credits
-------

This document took inspiration from the CONTRIBUTING files of the [Atom](https://github.com/atom/atom/blob/abccce6ee9079fdaefdecb018e72ea64000e52ef/CONTRIBUTING.md) and [Boto3](https://github.com/boto/boto3/blob/e85febf46a819d901956f349afef0b0eaa4d906d/CONTRIBUTING.rst) projects.