# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Circulation bundles."""

from __future__ import unicode_literals

from invenio_assets import NpmBundle, RequireJSFilter
from invenio_theme.bundles import js as _js


js_ill = NpmBundle(
    "js/circulation_ill_init.js",
    output="gen/circulation_ill.%(version)s.js",
    filters=RequireJSFilter(exclude=[_js.contents[1]]),
    npm={},
)

css = NpmBundle(
    # "css/other/cal-heatmap.css",
    # "css/circulation/user.css",
    # "vendors/jquery-ui/themes/redmond/jquery-ui.css",
    # "vendors/typeahead.js-bootstrap3.less/typeahead.css",
    "css/ill/ill.css",
    "css/other/awesomplete.css",
    "css/circulation/circ_id_complete.css",
    output="gen/circulation_ill.css",
)
