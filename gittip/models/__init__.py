# We don't use these two yet, but for testing to work we need them here.
# (If we don't import them then they aren't registered with gittip.orm.db
# .metadata, and thus aren't cleaned up properly during teardown.)

from gittip.models.absorption import Absorption
from gittip.models.deletion import Deletion


# The rest we actually use.
from gittip.models.elsewhere import Elsewhere
from gittip.models.exchange import Exchange
from gittip.models.participant import Participant
from gittip.models.payday import Payday
from gittip.models.tip import Tip
from gittip.models.transfer import Transfer
from gittip.models.user import User

all = [Elsewhere, Exchange, Participant, Payday, Tip, Transfer, User]
