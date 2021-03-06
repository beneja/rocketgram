# Copyright (C) 2015-2019 by Vd.
# This file is part of RocketGram, the modern Telegram bot framework.
# RocketGram is released under the MIT License (see LICENSE).


from ..errors import RocketgramError


class TooManyButtonsError(RocketgramError):
    pass


class NotEnoughButtonsError(RocketgramError):
    pass
