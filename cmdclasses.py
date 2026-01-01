# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Licensed under AGPLv3
#
# Copyright (c) 2025 Joseph Kroesche
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""cmdclasses - Import all command classes so they can be easily referenced.

Any class that implements a command is added here in the form of:

``` py
from mycommand import MyCommand
```

This allows the class `MyCommand` to be referenced directly. It makes the `add`
command possible so that the user can type the class name.
"""

from ledrange import LedRange
from ledrandom import LedRandom, LedRandomOG
from ledmeter import LedMeter
from ledturn import LedTurn
from ledbrake import LedBrake, LedBrakeHard
