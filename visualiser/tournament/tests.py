# Diplomacy Tournament Visualiser
# Copyright (C) 2014, 2016 Chris Brand
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone

from tournament.models import *

from datetime import *

HOURS_8 = timedelta(hours=8)
HOURS_9 = timedelta(hours=9)
HOURS_10 = timedelta(hours=10)
HOURS_16 = timedelta(hours=16)
HOURS_24 = timedelta(hours=24)

class TournamentModelTests(TestCase):
    def setUp(self):
        set1 = GameSet.objects.get(name='Avalon Hill')
        set2 = GameSet.objects.get(name='Gibsons')
        s1 = G_SCORING_SYSTEMS[0].name
        now = timezone.now()
        t1 = Tournament.objects.create(name='t1',
                                       start_date=now,
                                       end_date=now,
                                       round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                       tournament_scoring_system=T_SCORING_SYSTEMS[0].name)
        t2 = Tournament.objects.create(name='t2',
                                       start_date=now,
                                       end_date=now,
                                       round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                       tournament_scoring_system=T_SCORING_SYSTEMS[0].name)
        t3 = Tournament.objects.create(name='t3',
                                       start_date=now,
                                       end_date=now,
                                       round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                       tournament_scoring_system=T_SCORING_SYSTEMS[0].name)
        r11 = Round.objects.create(tournament=t1, scoring_system=s1, dias=True, start=t1.start_date)
        r12 = Round.objects.create(tournament=t1, scoring_system=s1, dias=True, start=t1.start_date + HOURS_8)
        r13 = Round.objects.create(tournament=t1, scoring_system=s1, dias=True, start=t1.start_date + HOURS_16)
        r14 = Round.objects.create(tournament=t1, scoring_system=s1, dias=True, start=t1.start_date + HOURS_24)
        r21 = Round.objects.create(tournament=t2, scoring_system=s1, dias=False, start=t2.start_date)
        r22 = Round.objects.create(tournament=t2, scoring_system=s1, dias=False, start=t2.start_date + HOURS_8)
        r31 = Round.objects.create(tournament=t3, scoring_system=s1, dias=True, start=t3.start_date)
        r32 = Round.objects.create(tournament=t3, scoring_system=s1, dias=True, start=t3.start_date + HOURS_8)
        g11 = Game.objects.create(name='g11', started_at=r11.start, the_round=r11, the_set=set1)
        g12 = Game.objects.create(name='g12', started_at=r11.start, the_round=r11, the_set=set1)
        g13 = Game.objects.create(name='g13', started_at=r12.start, the_round=r12, is_finished=True, the_set=set1)
        g14 = Game.objects.create(name='g14', started_at=r12.start, the_round=r12, the_set=set1)
        g15 = Game.objects.create(name='g15', started_at=r13.start, the_round=r13, is_finished=True, the_set=set1)
        g16 = Game.objects.create(name='g16', started_at=r13.start, the_round=r13, is_finished=True, the_set=set1)
        g21 = Game.objects.create(name='g21', started_at=r21.start, the_round=r21, the_set=set1)
        g22 = Game.objects.create(name='g22', started_at=r22.start, the_round=r22, the_set=set1)
        g31 = Game.objects.create(name='g31', started_at=r31.start, the_round=r31, is_finished=True, the_set=set1)
        g32 = Game.objects.create(name='g32', started_at=r32.start, the_round=r32, is_finished=True, the_set=set1)
        self.austria = GreatPower.objects.get(abbreviation='A')
        self.england = GreatPower.objects.get(abbreviation='E')
        self.france = GreatPower.objects.get(abbreviation='F')
        self.germany = GreatPower.objects.get(abbreviation='G')
        self.italy = GreatPower.objects.get(abbreviation='I')
        self.russia = GreatPower.objects.get(abbreviation='R')
        self.turkey = GreatPower.objects.get(abbreviation='T')

    # GScoringSolos

    # GScoringDrawSize

    # GScoringCDiplo

    # GScoringSumOfSquares

    # RScoringBest

    # TScoringSum

    # validate_year()
    def test_validate_year_negative(self):
        self.assertRaises(ValidationError, validate_year, -1)

    def test_validate_year_1899(self):
        self.assertRaises(ValidationError, validate_year, 1899)

    def test_validate_year_1900(self):
        self.assertRaises(ValidationError, validate_year, 1900)

    def test_validate_year_1901(self):
        self.assertIsNone(validate_year(1901))

    # validate_year_including_start()
    def test_validate_year_inc_start_negative(self):
        self.assertRaises(ValidationError, validate_year_including_start, -1)

    def test_validate_year_inc_start_1899(self):
        self.assertRaises(ValidationError, validate_year_including_start, 1899)

    def test_validate_year_inc_start_1900(self):
        self.assertIsNone(validate_year_including_start(1900))

    def test_validate_year_inc_start_1901(self):
        self.assertIsNone(validate_year_including_start(1901))

    # validate_sc_count()
    def test_validate_sc_count_negative(self):
        self.assertRaises(ValidationError, validate_sc_count, -1)

    def test_validate_sc_count_0(self):
        self.assertIsNone(validate_sc_count(0))

    def test_validate_sc_count_34(self):
        self.assertIsNone(validate_sc_count(34))

    def test_validate_sc_count_35(self):
        self.assertRaises(ValidationError, validate_sc_count, 35)

    # validate_wdd_id()
    def test_validate_wdd_id_me(self):
        # 4173 is Chris Brand
        self.assertIsNone(validate_wdd_id(4173))

    def test_validate_wdd_id_1(self):
        # 1 is known to be unused
        # Note that this test will fail if the WDD can't be reached
        # (in that case, we assume the id is valid)
        self.assertRaises(ValidationError, validate_wdd_id, 1)

    # validate_game_name()
    def test_validate_game_name_spaces(self):
        self.assertRaises(ValidationError, validate_game_name, u'space name')

    def test_validate_game_name_valid(self):
        self.assertIsNone(validate_game_name(u'ok'))

    # Tournament.is_finished()
    def test_tourney_is_finished_some_rounds_over(self):
        t = Tournament.objects.get(name='t1')
        self.assertFalse(t.is_finished())

    def test_tourney_is_finished_no_rounds_over(self):
        t = Tournament.objects.get(name='t2')
        self.assertFalse(t.is_finished())

    def test_tourney_is_finished_all_rounds_over(self):
        t = Tournament.objects.get(name='t3')
        self.assertTrue(t.is_finished())

    # Tournament.round_numbered()
    def test_tourney_round_numbered_negative(self):
        t = Tournament.objects.get(name='t1')
        self.assertRaises(Round.DoesNotExist, t.round_numbered, -1)

    def test_tourney_round_numbered_3(self):
        t = Tournament.objects.get(name='t1')
        self.assertEqual(t.round_numbered(3).number(), 3)

    # Tournament.current_round()
    def test_tourney_current_round_none(self):
        # All games in t3 are finished
        t = Tournament.objects.get(name='t3')
        self.assertIsNone(t.current_round())

    def test_tourney_current_round(self):
        t = Tournament.objects.get(name='t1')
        r = t.current_round()
        # All earlier rounds should be finished
        for i in range(1, r.number()):
            self.assertTrue(t.round_numbered(i).is_finished(), 'round %d' % i)
        # This round should be unfinished
        self.assertFalse(r.is_finished())

    # Round.number()
    def test_round_number_11(self):
        t = Tournament.objects.get(name='t1')
        r11 = t.round_set.all()[0]
        self.assertEqual(r11.number(), 1)

    def test_round_number_12(self):
        t = Tournament.objects.get(name='t1')
        r12 = t.round_set.all()[1]
        self.assertEqual(r12.number(), 2)

    def test_round_number_13(self):
        t = Tournament.objects.get(name='t1')
        r13 = t.round_set.all()[2]
        self.assertEqual(r13.number(), 3)

    def test_round_number_14(self):
        t = Tournament.objects.get(name='t1')
        r14 = t.round_set.all()[3]
        self.assertEqual(r14.number(), 4)

    def test_round_number_21(self):
        t = Tournament.objects.get(name='t2')
        r21 = t.round_set.all()[0]
        self.assertEqual(r21.number(), 1)

    def test_round_number_22(self):
        t = Tournament.objects.get(name='t2')
        r22 = t.round_set.all()[1]
        self.assertEqual(r22.number(), 2)

    # Round.is_finished()
    def test_round_is_finished_no_games_over(self):
        t = Tournament.objects.get(name='t1')
        r1 = t.round_numbered(1)
        self.assertFalse(r1.is_finished())

    def test_round_is_finished_some_games_over(self):
        t = Tournament.objects.get(name='t1')
        r2 = t.round_numbered(2)
        self.assertFalse(r2.is_finished())

    def test_round_is_finished_all_games_over(self):
        t = Tournament.objects.get(name='t1')
        r3 = t.round_numbered(3)
        self.assertTrue(r3.is_finished())

    def test_round_is_finished_no_games(self):
        """
        Rounds with no games can't have started, let alone finished
        """
        t = Tournament.objects.get(name='t1')
        r4 = t.round_numbered(4)
        self.assertFalse(r4.is_finished())

    # Round.clean()
    def test_round_clean_missing_earliest_end(self):
        t = Tournament.objects.get(name='t1')
        s1 = G_SCORING_SYSTEMS[0].name
        r = Round.objects.create(tournament=t,
                                 scoring_system=s1,
                                 dias=True,
                                 start=t.start_date + HOURS_8,
                                 earliest_end_time=t.start_date + HOURS_9)
        self.assertRaises(ValidationError, r.clean)

    def test_round_clean_missing_latest_end(self):
        t = Tournament.objects.get(name='t1')
        s1 = G_SCORING_SYSTEMS[0].name
        r = Round.objects.create(tournament=t,
                                 scoring_system=s1,
                                 dias=True,
                                 start=t.start_date + HOURS_8,
                                 latest_end_time=t.start_date + HOURS_10)
        self.assertRaises(ValidationError, r.clean)

    # Game.is_dias()
    def test_game_is_dias(self):
        for g in Game.objects.all():
            self.assertEqual(g.is_dias(), g.the_round.dias)

    # Game.years_played()

    # Game.players()

    # Game.passed_draw()

    # Game.board_toppers()

    # Game.neutrals()

    # Game.final_year()

    # Game.soloer()

    # Game.result_str()

    # Game.clean()
    def test_game_clean_non_unique_name(self):
        g1 = Game.objects.get(pk=1)
        t = Tournament.objects.get(name='t1')
        r = t.round_numbered(4)
        g2 = Game.objects.create(name='g13',
                                 started_at=g1.started_at + HOURS_8,
                                 the_round=r,
                                 is_finished=False,
                                 the_set=g1.the_set)
        self.assertRaises(ValidationError, g2.clean)

    # DrawProposal.draw_size()

    # DrawProposal.powers()

    # DrawProposal.clean()
    def test_draw_proposal_clean_with_duplicates(self):
        g = Game.objects.get(pk=1)
        dp = DrawProposal(game=g, year=1910, season='F', passed=False,
                          power_1=self.austria, power_2=self.austria)
        self.assertRaises(ValidationError, dp.clean)

    def test_draw_proposal_clean_with_gap(self):
        g = Game.objects.get(pk=1)
        dp = DrawProposal(game=g, year=1910, season='F', passed=False,
                          power_1=self.austria, power_3=self.england)
        self.assertRaises(ValidationError, dp.clean)

    # RoundPlayer.clean()

    # GamePlayer.clean()

    # GameImage.turn_str()

    # GameImage.clean()

    # CentreCount.clean()

