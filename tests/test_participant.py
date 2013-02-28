from __future__ import unicode_literals
import datetime
from decimal import Decimal

from aspen.utils import utcnow
from nose.tools import assert_raises, assert_equals

from gittip.models import Absorption, Deletion, User, Tip
from gittip.orm import db
from gittip.participant import Participant, NeedConfirmation
from gittip.testing import Harness, looks_random
from gittip.elsewhere.twitter import TwitterAccount

# TODO: Test that accounts elsewhere are not considered claimed by default


class StubAccount(object):
    def __init__(self, platform, user_id):
        self.platform = platform
        self.user_id = user_id


class TestNeedConfirmation(Harness):
    def test_need_confirmation1(self):
        assert not NeedConfirmation(False, False, False)

    def test_need_confirmation2(self):
        assert NeedConfirmation(False, False, True)

    def test_need_confirmation3(self):
        assert not NeedConfirmation(False, True, False)

    def test_need_confirmation4(self):
        assert NeedConfirmation(False, True, True)

    def test_need_confirmation5(self):
        assert NeedConfirmation(True, False, False)

    def test_need_confirmation6(self):
        assert NeedConfirmation(True, False, True)

    def test_need_confirmation7(self):
        assert NeedConfirmation(True, True, False)

    def test_need_confirmation8(self):
        assert NeedConfirmation(True, True, True)


class TestAbsorptions(Harness):
    # TODO: These tests should probably be moved to absorptions tests
    def setUp(self):
        super(Harness, self).setUp()
        now = utcnow()
        hour_ago = now - datetime.timedelta(hours=1)
        for pid in ['alice', 'bob', 'carl']:
            self.make_participant(pid, claimed_time=hour_ago,
                                  last_bill_result='')
        deadbeef = TwitterAccount('1', {'screen_name': 'deadbeef'})
        self.deadbeef_original_pid = deadbeef.participant_id

        Participant('carl').set_tip_to('bob', '1.00')
        Participant('alice').set_tip_to(self.deadbeef_original_pid, '1.00')
        Participant('bob').take_over(deadbeef, have_confirmation=True)

    def test_participant_can_be_instantiated(self):
        expected = Participant
        actual = Participant(None).__class__
        assert actual is expected, actual

    def test_bob_has_two_dollars_in_tips(self):
        expected = Decimal('2.00')
        actual = Participant('bob').get_dollars_receiving()
        assert_equals(actual, expected)

    def test_alice_gives_to_bob_now(self):
        expected = Decimal('1.00')
        actual = Participant('alice').get_tip_to('bob')
        assert_equals(actual, expected)

    def test_deadbeef_is_archived(self):
        actual = Absorption.query\
                           .filter_by(absorbed_by='bob',
                                      absorbed_was=self.deadbeef_original_pid)\
                           .count()
        expected = 1
        assert_equals(actual, expected)

    def test_alice_doesnt_gives_to_deadbeef_anymore(self):
        expected = Decimal('0.00')
        actual = Participant('alice').get_tip_to(self.deadbeef_original_pid)
        assert actual == expected, actual

    def test_alice_doesnt_give_to_whatever_deadbeef_was_archived_as_either(self):
        expected = Decimal('0.00')
        actual = Participant('alice').get_tip_to(self.deadbeef_original_pid)
        assert actual == expected, actual

    def test_attempts_to_change_archived_deadbeef_fail(self):
        participant = Participant(self.deadbeef_original_pid)
        with assert_raises(AssertionError):
            participant.change_id('zombeef')

    def test_there_is_no_more_deadbeef(self):
        actual = Participant('deadbeef').get_details()
        assert actual is None, actual


class TestDeactivation(Harness):

    def test_deactivate_returns_random_id(self):
        actual = self.make_participant('alice').deactivate()
        assert looks_random(actual), actual

    def test_deactivated_participant_is_out_of_sync(self):
        alice = self.make_participant('alice')
        alice.deactivate()
        actual = alice.id
        assert actual == 'alice', actual

    def test_deactivated_participant_has_no_session(self):
        alice = self.make_participant('alice')
        import pdb; pdb.set_trace()
        assert User.from_session_token(alice.session_token).ANON
        alice.session_token = 'foo'
        assert User.from_session_token(alice.session_token).ANON
        db.session.commit()
        assert User.from_session_token(alice.session_token).ANON
        alice.deactivate()
        assert User.from_session_token(alice.session_token).ANON

    def test_deleting_a_non_existent_user_assertion_errors(self):
        alice = Participant('alice')
        with assert_raises(AssertionError):
            alice.deactivate()

    def test_no_deactivations_to_start_with(self):
        self.make_participant('alice')
        actual = Deletion.query.filter_by().count()
        assert actual == 0, actual

    def test_deactivate_records_one_deactivation(self):
        self.make_participant('alice').deactivate()
        actual = Deletion.query.filter_by().count()
        assert actual == 1, actual

    def test_deactivation_records_deactivated_was(self):
        self.make_participant('alice').deactivate()
        actual = Deletion.query.filter_by()[0].deactivated_was
        assert actual == 'alice', actual

    def test_deactivation_records_archived_as(self):
        self.make_participant('alice').deactivate()
        actual = Deletion.query.filter_by()[0].archived_as
        assert looks_random(actual)


class TestParticipant(Harness):
    def setUp(self):
        super(Harness, self).setUp()
        now = utcnow()
        for idx, pid in enumerate(['alice', 'bob', 'carl'], start=1):
            self.make_participant(pid, claimed_time=now)
            twitter_account = TwitterAccount(idx, {'screen_name': pid})
            Participant(pid).take_over(twitter_account)

    def test_cant_take_over_claimed_participant_without_confirmation(self):
        bob_twitter = StubAccount('twitter', '2')
        with assert_raises(NeedConfirmation):
            Participant('alice').take_over(bob_twitter)

    def test_taking_over_yourself_sets_all_to_zero(self):
        bob_twitter = StubAccount('twitter', '2')
        Participant('alice').set_tip_to('bob', '1.00')
        Participant('alice').take_over(bob_twitter, have_confirmation=True)
        expected = Decimal('0.00')
        actual = Participant('alice').get_dollars_giving()
        assert_equals(actual, expected)

    def test_alice_ends_up_tipping_bob_two_dollars(self):
        carl_twitter = StubAccount('twitter', '3')
        Participant('alice').set_tip_to('bob', '1.00')
        Participant('alice').set_tip_to('carl', '1.00')
        Participant('bob').take_over(carl_twitter, have_confirmation=True)
        expected = Decimal('2.00')
        actual = Participant('alice').get_tip_to('bob')
        assert_equals(actual, expected)

    def test_bob_ends_up_tipping_alice_two_dollars(self):
        carl_twitter = StubAccount('twitter', '3')
        Participant('bob').set_tip_to('alice', '1.00')
        Participant('carl').set_tip_to('alice', '1.00')
        Participant('bob').take_over(carl_twitter, have_confirmation=True)
        expected = Decimal('2.00')
        actual = Participant('bob').get_tip_to('alice')
        assert_equals(actual, expected)

    def test_ctime_comes_from_the_older_tip(self):
        carl_twitter = StubAccount('twitter', '3')
        Participant('alice').set_tip_to('bob', '1.00')
        Participant('alice').set_tip_to('carl', '1.00')
        Participant('bob').take_over(carl_twitter, have_confirmation=True)

        tips = Tip.query.all()
        first, second = tips[0], tips[1]

        # sanity checks (these don't count :)
        assert len(tips) == 4
        assert first.tipper, first.tippee == ('alice', 'bob')
        assert second.tipper, second.tippee == ('alice', 'carl')

        expected = first.ctime
        actual = Tip.query.first().ctime
        assert_equals(actual, expected)

    def test_connecting_unknown_account_fails(self):
        unknown_account = StubAccount('github', 'jim')
        with assert_raises(AssertionError):
            Participant('bob').take_over(unknown_account)

