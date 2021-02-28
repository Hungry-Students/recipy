ReciPy
======

ReciPy is a federated recipe management platform written in
[Python](https://www.python.org/) and using
[Django](https://www.djangoproject.com/).
Collect recipes from all over the web, share them with everyone!

Features
--------

- Add to your cookbook recipes from various website
  ([marmiton.org](https://www.marmiton.org/),
  [cuisine libre](https://cuisine-libre.fr/) or
  [Miam miam](https://miam.twal.org/))
- Search your cookbook for specific recipes: only soups, with potatoes,
  vegetarian...

### Features to be added

- Follow any user, even from another instance
- Search among all the cookbooks you are following and allow your users to do
  the same!

Installing
----------

### Running the site locally

Before running the site, you may setup a [Python virtual
environment](https://docs.python.org/3/tutorial/venv.html)

    python3 -m venv .env
    source .env/bin/activate

To run the site locally, simply type

    make start

License
-------

Portions of project Recipy are copyright (C) 2020 [TWal](https://twal.org/) for
project [miam](https://github.com/TWal/miam).
All other copyright for project Recipy is (C) 2020-2021 Axel Kugelman & Jules
Saget.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along
with this program.
If not, see <https://www.gnu.org/licenses/>
