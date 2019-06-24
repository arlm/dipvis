# Diplomacy Tournament Visualiser
# Copyright (C) 2019 Chris Brand
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

import uuid
from urllib.parse import urlencode

from django.contrib.auth.models import Permission, User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from tournament.diplomacy import GameSet, GreatPower
from tournament.models import Tournament, TournamentPlayer, SeederBias
from tournament.models import Round, RoundPlayer, Game, GamePlayer
from tournament.models import CentreCount, DrawProposal
from tournament.models import R_SCORING_SYSTEMS, T_SCORING_SYSTEMS
from tournament.models import G_SCORING_SYSTEMS
from tournament.players import Player

@override_settings(HOSTNAME='example.com')
@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TournamentViewTests(TestCase):
    fixtures = ['game_sets.json']

    @classmethod
    def setUpTestData(cls):
        # Easy access to all the GreatPowers
        cls.austria = GreatPower.objects.get(abbreviation='A')
        cls.england = GreatPower.objects.get(abbreviation='E')
        cls.france = GreatPower.objects.get(abbreviation='F')
        cls.germany = GreatPower.objects.get(abbreviation='G')
        cls.italy = GreatPower.objects.get(abbreviation='I')
        cls.russia = GreatPower.objects.get(abbreviation='R')
        cls.turkey = GreatPower.objects.get(abbreviation='T')

        # A regular user with no special permissions or ownership
        cls.USERNAME1 = 'regular'
        cls.PWORD1 = 'CleverPassword'
        u1 = User.objects.create_user(username=cls.USERNAME1, password=cls.PWORD1)
        u1.save()

        # A superuser
        cls.USERNAME2 = 'superuser'
        cls.PWORD2 = 'L33tPw0rd'
        u2 = User.objects.create_user(username=cls.USERNAME2,
                                      password=cls.PWORD2,
                                      is_superuser=True)
        u2.save()

        # A user who is a manager of a tournament (t2)
        # We give managers the appropriate permissions
        cls.USERNAME3 = 'manager'
        cls.PWORD3 = 'MyPassword'
        cls.u3 = User.objects.create_user(username=cls.USERNAME3,
                                          password=cls.PWORD3)
        perm = Permission.objects.get(name='Can change round player')
        cls.u3.user_permissions.add(perm)
        perm = Permission.objects.get(name='Can add preference')
        cls.u3.user_permissions.add(perm)
        perm = Permission.objects.get(name='Can add seeder bias')
        cls.u3.user_permissions.add(perm)
        cls.u3.save()

        # Some Players
        cls.p1 = Player.objects.create(first_name='Angela',
                                       last_name='Ampersand',
                                       email='a.ampersand@example.com')
        cls.p2 = Player.objects.create(first_name='Bobby',
                                       last_name='Bandersnatch')
        p3 = Player.objects.create(first_name='Cassandra',
                                   last_name='Cucumber')
        p4 = Player.objects.create(first_name='Derek',
                                   last_name='Dromedary')
        p5 = Player.objects.create(first_name='Ethel',
                                   last_name='Elephant')
        p6 = Player.objects.create(first_name='Frank',
                                   last_name='Frankfurter')
        p7 = Player.objects.create(first_name='Georgette',
                                   last_name='Grape')
        p8 = Player.objects.create(first_name='Harry',
                                   last_name='Heffalump')
        p9 = Player.objects.create(first_name='Iris',
                                   last_name='Ignoramus')
        p10 = Player.objects.create(first_name='Jake',
                                    last_name='Jalopy')
        # Player that is also u3 (manager of t2)
        cls.p11 = Player.objects.create(first_name='Kathryn',
                                        last_name='Krispy',
                                        user = cls.u3)

        now = timezone.now()
        # Published Tournament, so it's visible to all
        # Ongoing, one round
        cls.t1 = Tournament.objects.create(name='t1',
                                           start_date=now,
                                           end_date=now,
                                           round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                           tournament_scoring_system=T_SCORING_SYSTEMS[0].name,
                                           draw_secrecy=Tournament.SECRET,
                                           is_published=True)
        Round.objects.create(tournament=cls.t1,
                             start=cls.t1.start_date,
                             scoring_system=G_SCORING_SYSTEMS[0].name,
                             dias=True)
        # Pre-generate a UUID for player prefs
        cls.tp11 = TournamentPlayer.objects.create(player=cls.p1,
                                                   tournament=cls.t1,
                                                   uuid_str=str(uuid.uuid4()))
        tp = TournamentPlayer.objects.create(player=p3,
                                             tournament=cls.t1)

        # Unpublished Tournament, with a manager (u3)
        cls.t2 = Tournament.objects.create(name='t2',
                                           start_date=now,
                                           end_date=now,
                                           round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                           tournament_scoring_system=T_SCORING_SYSTEMS[0].name,
                                           draw_secrecy=Tournament.SECRET,
                                           power_assignment=Tournament.PREFERENCES,
                                           is_published=False)
        cls.r21 = Round.objects.create(tournament=cls.t2,
                                       start=cls.t2.start_date,
                                       scoring_system=G_SCORING_SYSTEMS[0].name,
                                       dias=False)
        g21 = Game.objects.create(name='Game1',
                                  the_round=cls.r21,
                                  started_at=cls.r21.start,
                                  the_set=GameSet.objects.first(),
                                  is_finished=False,
                                  is_top_board=True)
        tp = TournamentPlayer.objects.create(player=cls.p1,
                                             tournament=cls.t2)
        # Explicitly call save() to generate a UUID
        tp.save()
        tp = TournamentPlayer.objects.create(player=p3,
                                             tournament=cls.t2)
        tp = TournamentPlayer.objects.create(player=p4,
                                             tournament=cls.t2)
        tp = TournamentPlayer.objects.create(player=p5,
                                             tournament=cls.t2)
        tp = TournamentPlayer.objects.create(player=p6,
                                             tournament=cls.t2)
        tp = TournamentPlayer.objects.create(player=p7,
                                             tournament=cls.t2)
        tp = TournamentPlayer.objects.create(player=p8,
                                             tournament=cls.t2)
        cls.tp29 = TournamentPlayer.objects.create(player=p9,
                                                   tournament=cls.t2)
        tp = TournamentPlayer.objects.create(player=p10,
                                             tournament=cls.t2)
        RoundPlayer.objects.create(player=cls.p1, the_round=cls.r21)
        RoundPlayer.objects.create(player=p3, the_round=cls.r21)
        RoundPlayer.objects.create(player=p4, the_round=cls.r21)
        RoundPlayer.objects.create(player=p5, the_round=cls.r21)
        RoundPlayer.objects.create(player=p6, the_round=cls.r21)
        RoundPlayer.objects.create(player=p7, the_round=cls.r21)
        RoundPlayer.objects.create(player=p8, the_round=cls.r21)
        RoundPlayer.objects.create(player=p9, the_round=cls.r21)
        RoundPlayer.objects.create(player=p10, the_round=cls.r21)
        GamePlayer.objects.create(player=cls.p1, game=g21, power=cls.austria)
        GamePlayer.objects.create(player=p3, game=g21, power=cls.england)
        GamePlayer.objects.create(player=p4, game=g21, power=cls.france)
        GamePlayer.objects.create(player=p5, game=g21, power=cls.germany)
        GamePlayer.objects.create(player=p6, game=g21, power=cls.italy)
        GamePlayer.objects.create(player=p7, game=g21, power=cls.russia)
        GamePlayer.objects.create(player=p8, game=g21, power=cls.turkey)
        CentreCount.objects.create(power=cls.austria, game=g21, year=1901, count=0)
        CentreCount.objects.create(power=cls.england, game=g21, year=1901, count=4)
        CentreCount.objects.create(power=cls.france, game=g21, year=1901, count=5)
        CentreCount.objects.create(power=cls.germany, game=g21, year=1901, count=5)
        CentreCount.objects.create(power=cls.italy, game=g21, year=1901, count=6)
        CentreCount.objects.create(power=cls.russia, game=g21, year=1901, count=7)
        CentreCount.objects.create(power=cls.turkey, game=g21, year=1901, count=5)
        cls.t2.managers.add(cls.u3)

        # Unpublished Tournament, without a manager
        cls.t3 = Tournament.objects.create(name='t3',
                                           start_date=now,
                                           end_date=now,
                                           round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                           tournament_scoring_system=T_SCORING_SYSTEMS[0].name,
                                           draw_secrecy=Tournament.SECRET,
                                           is_published=False)

        # Published Tournament, without a manager, but not editable
        # One round, tournament complete
        cls.t4 = Tournament.objects.create(name='t4',
                                           start_date=now,
                                           end_date=now,
                                           round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                           tournament_scoring_system=T_SCORING_SYSTEMS[0].name,
                                           draw_secrecy=Tournament.SECRET,
                                           is_published=True,
                                           editable=False)
        cls.r41 = Round.objects.create(tournament=cls.t4,
                                       start=cls.t4.start_date,
                                       scoring_system=G_SCORING_SYSTEMS[0].name,
                                       dias=False)
        g41 = Game.objects.create(name='Game1',
                                  the_round=cls.r41,
                                  started_at=cls.r41.start,
                                  the_set=GameSet.objects.first(),
                                  is_finished=True)
        g42 = Game.objects.create(name='Game2',
                                  the_round=cls.r41,
                                  started_at=cls.r41.start,
                                  the_set=GameSet.objects.first(),
                                  is_finished=True)
        tp = TournamentPlayer.objects.create(player=cls.p1,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p3,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p4,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p5,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p6,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p7,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p8,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p9,
                                             tournament=cls.t4)
        tp = TournamentPlayer.objects.create(player=p10,
                                             tournament=cls.t4)
        RoundPlayer.objects.create(player=cls.p1, the_round=cls.r41)
        RoundPlayer.objects.create(player=p3, the_round=cls.r41)
        RoundPlayer.objects.create(player=p4, the_round=cls.r41)
        RoundPlayer.objects.create(player=p5, the_round=cls.r41)
        RoundPlayer.objects.create(player=p6, the_round=cls.r41)
        RoundPlayer.objects.create(player=p7, the_round=cls.r41)
        RoundPlayer.objects.create(player=p8, the_round=cls.r41)
        RoundPlayer.objects.create(player=p9, the_round=cls.r41)
        RoundPlayer.objects.create(player=p10, the_round=cls.r41)
        GamePlayer.objects.create(player=cls.p1, game=g41, power=cls.austria)
        GamePlayer.objects.create(player=p3, game=g41, power=cls.england)
        GamePlayer.objects.create(player=p4, game=g41, power=cls.france)
        GamePlayer.objects.create(player=p5, game=g41, power=cls.germany)
        GamePlayer.objects.create(player=p6, game=g41, power=cls.italy)
        GamePlayer.objects.create(player=p7, game=g41, power=cls.russia)
        GamePlayer.objects.create(player=p8, game=g41, power=cls.turkey)
        GamePlayer.objects.create(player=p10, game=g42, power=cls.austria)
        GamePlayer.objects.create(player=p9, game=g42, power=cls.england)
        GamePlayer.objects.create(player=p8, game=g42, power=cls.france)
        GamePlayer.objects.create(player=p7, game=g42, power=cls.germany)
        GamePlayer.objects.create(player=p6, game=g42, power=cls.italy)
        GamePlayer.objects.create(player=p5, game=g42, power=cls.russia)
        GamePlayer.objects.create(player=p4, game=g42, power=cls.turkey)
        # Add CentreCounts for g41. Draw vote passed. A power on 1 SC, a power eliminated
        CentreCount.objects.create(power=cls.austria, game=g41, year=1901, count=0)
        CentreCount.objects.create(power=cls.england, game=g41, year=1901, count=4)
        CentreCount.objects.create(power=cls.france, game=g41, year=1901, count=5)
        CentreCount.objects.create(power=cls.germany, game=g41, year=1901, count=5)
        CentreCount.objects.create(power=cls.italy, game=g41, year=1901, count=6)
        CentreCount.objects.create(power=cls.russia, game=g41, year=1901, count=7)
        CentreCount.objects.create(power=cls.turkey, game=g41, year=1901, count=5)
        CentreCount.objects.create(power=cls.austria, game=g41, year=1902, count=0)
        CentreCount.objects.create(power=cls.england, game=g41, year=1902, count=7)
        CentreCount.objects.create(power=cls.france, game=g41, year=1902, count=8)
        CentreCount.objects.create(power=cls.germany, game=g41, year=1902, count=1)
        CentreCount.objects.create(power=cls.italy, game=g41, year=1902, count=5)
        CentreCount.objects.create(power=cls.russia, game=g41, year=1902, count=8)
        CentreCount.objects.create(power=cls.turkey, game=g41, year=1902, count=5)
        DrawProposal.objects.create(game=g41,
                                    year=1903,
                                    season='S',
                                    passed=True,
                                    proposer=cls.france,
                                    power_1=cls.england,
                                    power_2=cls.france,
                                    power_3=cls.italy,
                                    power_4=cls.russia,
                                    power_5=cls.turkey)
        # Add CentreCounts for g42 - solo for Russia. Austria eliminated
        CentreCount.objects.create(power=cls.austria, game=g42, year=1901, count=4)
        CentreCount.objects.create(power=cls.england, game=g42, year=1901, count=4)
        CentreCount.objects.create(power=cls.france, game=g42, year=1901, count=5)
        CentreCount.objects.create(power=cls.germany, game=g42, year=1901, count=5)
        CentreCount.objects.create(power=cls.italy, game=g42, year=1901, count=4)
        CentreCount.objects.create(power=cls.russia, game=g42, year=1901, count=8)
        CentreCount.objects.create(power=cls.turkey, game=g42, year=1901, count=4)
        CentreCount.objects.create(power=cls.austria, game=g42, year=1902, count=2)
        CentreCount.objects.create(power=cls.england, game=g42, year=1902, count=3)
        CentreCount.objects.create(power=cls.france, game=g42, year=1902, count=5)
        CentreCount.objects.create(power=cls.germany, game=g42, year=1902, count=4)
        CentreCount.objects.create(power=cls.italy, game=g42, year=1902, count=4)
        CentreCount.objects.create(power=cls.russia, game=g42, year=1902, count=13)
        CentreCount.objects.create(power=cls.turkey, game=g42, year=1902, count=3)
        CentreCount.objects.create(power=cls.austria, game=g42, year=1903, count=0)
        CentreCount.objects.create(power=cls.england, game=g42, year=1903, count=2)
        CentreCount.objects.create(power=cls.france, game=g42, year=1903, count=5)
        CentreCount.objects.create(power=cls.germany, game=g42, year=1903, count=3)
        CentreCount.objects.create(power=cls.italy, game=g42, year=1903, count=4)
        CentreCount.objects.create(power=cls.russia, game=g42, year=1903, count=19)
        CentreCount.objects.create(power=cls.turkey, game=g42, year=1903, count=1)

        # Hopefully this isn't the pk for any Tournament
        cls.INVALID_T_PK = 99999

        # Published Tournament, so it's visible to all
        # Ongoing, one round that has started
        cls.t5 = Tournament.objects.create(name='t1',
                                           start_date=now,
                                           end_date=now,
                                           round_scoring_system=R_SCORING_SYSTEMS[0].name,
                                           tournament_scoring_system=T_SCORING_SYSTEMS[0].name,
                                           draw_secrecy=Tournament.SECRET,
                                           is_published=True)
        cls.r51 = Round.objects.create(tournament=cls.t5,
                                       start=cls.t5.start_date,
                                       scoring_system=G_SCORING_SYSTEMS[0].name,
                                       dias=True)
        # Pre-generate a UUID for player prefs
        cls.tp51 = TournamentPlayer.objects.create(player=cls.p1,
                                                   tournament=cls.t5,
                                                   uuid_str=str(uuid.uuid4()))
        tp = TournamentPlayer.objects.create(player=p3,
                                             tournament=cls.t5)
        Game.objects.create(name='Game1',
                            the_round=cls.r51,
                            started_at=cls.r51.start,
                            the_set=GameSet.objects.first(),
                            is_finished=False)

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Check that we get the right tournaments listed
        self.assertIn(b't1', response.content) # Published
        self.assertNotIn(b't2', response.content) # Unpublished
        self.assertNotIn(b't3', response.content) # Unpublished
        self.assertIn(b't4', response.content) # Published

    def test_index_superuser(self):
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Check that we get the right tournaments listed
        self.assertIn(b't1', response.content) # Published
        self.assertIn(b't2', response.content) # Unpublished
        self.assertIn(b't3', response.content) # Unpublished
        self.assertIn(b't4', response.content) # Published

    def test_index_manager(self):
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Check that we get the right tournaments listed
        self.assertIn(b't1', response.content) # Published
        self.assertIn(b't2', response.content) # Unpublished, manager
        self.assertNotIn(b't3', response.content) # Unpublished
        self.assertIn(b't4', response.content) # Published

    def test_detail_invalid_tournament(self):
        response = self.client.get(reverse('tournament_detail', args=(self.INVALID_T_PK,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_manager_wrong_tournament(self):
        # A manager can't see an unpublished tournament that isn't theirs
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('tournament_detail', args=(self.t3.pk,)))
        self.assertEqual(response.status_code, 404)

    def test_detail(self):
        # Don't have to be logged in to see a published tournament
        response = self.client.get(reverse('tournament_detail', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_detail_regular_user(self):
        # Any user can see a published tournament
        self.client.login(username=self.USERNAME1, password=self.PWORD1)
        response = self.client.get(reverse('tournament_detail', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_detail_superuser(self):
        # A superuser can see any tournament
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('tournament_detail', args=(self.t3.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_detail_manager(self):
        # A manager see their unpublished tournament
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('tournament_detail', args=(self.t2.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_framesets(self):
        response = self.client.get(reverse('framesets', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_frameset_3x3(self):
        response = self.client.get(reverse('frameset_3x3', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_frameset_top_board(self):
        response = self.client.get(reverse('frameset_top_board', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_frameset_2x2(self):
        response = self.client.get(reverse('frameset_2x2', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_frameset_1x1(self):
        response = self.client.get(reverse('frameset_1x1', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_views(self):
        response = self.client.get(reverse('tournament_views', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_overview(self):
        response = self.client.get(reverse('tournament_overview', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_overview2(self):
        response = self.client.get(reverse('tournament_overview_2', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_overview3(self):
        response = self.client.get(reverse('tournament_overview_3', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_scores(self):
        # Scores page for an in-progress Tournament
        response = self.client.get(reverse('tournament_scores', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Current Scores', response.content)

    def test_scores_completed(self):
        # Scores page for a completed Tournament
        response = self.client.get(reverse('tournament_scores', args=(self.t4.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Final Scores', response.content)

    def test_scores_refresh(self):
        response = self.client.get(reverse('tournament_scores_refresh', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_game_results(self):
        response = self.client.get(reverse('tournament_game_results', args=(self.t4.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_game_results_ongoing(self):
        # Ongoing tournament
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('tournament_game_results', args=(self.t2.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_best_countries(self):
        response = self.client.get(reverse('tournament_best_countries', args=(self.t4.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_best_countries_refresh(self):
        response = self.client.get(reverse('tournament_best_countries_refresh', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_enter_scores_not_logged_in(self):
        response = self.client.get(reverse('enter_scores', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_enter_scores_regular_user(self):
        # A regular user can't enter scores for any old tournament
        self.client.login(username=self.USERNAME1, password=self.PWORD1)
        response = self.client.get(reverse('enter_scores', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_enter_scores_manager_wrong_tournament(self):
        # A manager can't enter scores for a tournament that isn't theirs
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('enter_scores', args=(self.t3.pk,)))
        self.assertEqual(response.status_code, 404)

    def test_enter_scores_archived(self):
        # Nobody can enter scores for an archived tournament
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('enter_scores', args=(self.t4.pk,)))
        self.assertEqual(response.status_code, 404)

    def test_enter_scores_superuser(self):
        # A superuser can enter scores for any tournament
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('enter_scores', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_enter_scores_manager(self):
        # A manager can enter scores for their tournament
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('enter_scores', args=(self.t2.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_current_round(self):
        response = self.client.get(reverse('tournament_round', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_current_round_completed(self):
        # "Current round" for a tournament that has ended
        response = self.client.get(reverse('tournament_round', args=(self.t4.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_game_image_not_logged_in(self):
        response = self.client.get(reverse('add_game_image', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_news(self):
        response = self.client.get(reverse('tournament_news', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_news_ticker(self):
        response = self.client.get(reverse('tournament_news_ticker', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_background(self):
        response = self.client.get(reverse('tournament_background', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_ticker(self):
        response = self.client.get(reverse('tournament_ticker', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_background_ticker(self):
        response = self.client.get(reverse('tournament_background_ticker', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<meta http-equiv="refresh"', response.content)

    def test_rounds(self):
        response = self.client.get(reverse('round_index', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_enter_prefs_not_logged_in(self):
        response = self.client.get(reverse('enter_prefs', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_enter_prefs_manager(self):
        # A manager can enter preferences for players in their Tournament
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('enter_prefs', args=(self.t2.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_enter_prefs(self):
        # A manager can enter preferences for players in their Tournament
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        data = urlencode({'form-TOTAL_FORMS': '9',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 9,
                          'form-0-prefs': 'FART',
                          'form-1-prefs': 'FART',
                          'form-2-prefs': 'FART',
                          'form-3-prefs': 'FART',
                          'form-4-prefs': 'FART',
                          'form-5-prefs': 'FART',
                          'form-6-prefs': 'FART',
                          'form-7-prefs': 'FART',
                          'form-8-prefs': 'FART'})
        response = self.client.post(reverse('enter_prefs', args=(self.t2.pk,)),
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect to the tournament_detail page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('tournament_detail', args=(self.t2.pk,)))
        # ... and the preferences should have been set
        for tp in self.t2.tournamentplayer_set.all():
            self.assertEqual(tp.prefs_string(), 'FART')
        # Clean up
        for tp in self.t2.tournamentplayer_set.all():
            tp.preference_set.all().delete()

    def test_upload_prefs_not_logged_in(self):
        response = self.client.get(reverse('upload_prefs', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_prefs_csv(self):
        response = self.client.get(reverse('prefs_csv', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_player_prefs(self):
        response = self.client.get(reverse('player_prefs', args=(self.t1.pk, self.tp11.uuid_str)))
        self.assertEqual(response.status_code, 200)

    def test_player_prefs_invalid_uuid(self):
        # Should get a 404 error if the UUID doesn't correspond to a TournamentPlayer
        response = self.client.get(reverse('player_prefs', args=(self.t1.pk, uuid.uuid4())))
        self.assertEqual(response.status_code, 404)

    def test_player_prefs_too_late(self):
        # Should get a 404 error if the final round has started
        response = self.client.get(reverse('player_prefs', args=(self.t5.pk, self.tp51.uuid_str)))
        self.assertEqual(response.status_code, 404)

    def test_player_prefs_post(self):
        url = reverse('player_prefs', args=(self.t1.pk, self.tp11.uuid_str))
        data = urlencode({'prefs': 'FART'})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect back to the same page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the preferences should have been set
        self.assertEqual(self.tp11.prefs_string(), 'FART')
        # Clean up
        self.tp11.preference_set.all().delete()

    def test_tournament_players(self):
        response = self.client.get(reverse('tournament_players', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_tournament_players_editable_prefs(self):
        # A tournament that can be edited, that uses preferences for power assignment
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('tournament_players', args=(self.t2.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_tournament_players_editable_no_prefs(self):
        # A tournament that can be edited, that doesn't use preferences for power assignment
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('tournament_players', args=(self.t3.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_tournament_players_archived(self):
        # A tournament that the user could edit, except that it's been set to not editable
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('tournament_players', args=(self.t4.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_tournament_players_unregister_from_editable(self):
        # A tournament that can be edited
        # Add a TournamentPlayer and RoundPlayer just for this test
        self.assertFalse(self.t2.tournamentplayer_set.filter(player=self.p2).exists())
        tp = TournamentPlayer.objects.create(player=self.p2,
                                             tournament=self.t2)
        self.assertTrue(self.t2.tournamentplayer_set.filter(player=self.p2).exists())
        RoundPlayer.objects.create(player=self.p2,
                                   the_round=self.t2.round_numbered(1))
        self.assertTrue(self.t2.round_numbered(1).roundplayer_set.filter(player=self.p2).exists())
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        url = reverse('tournament_players', args=(self.t2.pk,))
        data = urlencode({'unregister_%d' % tp.pk: 'Unregister player',
                          'form-TOTAL_FORMS': '4',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 0})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect back to the same page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the TournamentPlayer and RoundPlayer should no longer exist
        self.assertFalse(self.t2.tournamentplayer_set.filter(player=self.p2).exists())
        self.assertFalse(self.t2.round_numbered(1).roundplayer_set.filter(player=self.p2).exists())

    def test_tournament_players_unregister_from_archived(self):
        # A tournament that the user could edit, except that it's been set to not editable
        # Use an existing TournamentPlayer
        tp = self.t4.tournamentplayer_set.get(player=self.p1)
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        url = reverse('tournament_players', args=(self.t4.pk,))
        data = urlencode({'unregister_%d' % tp.pk: 'Unregister player',
                          'form-TOTAL_FORMS': '4',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 0})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # We shouldn't be allowed to change an uneditable Tournament
        self.assertEqual(response.status_code, 404)
        # ... and the TournamentPlayer should still exist
        self.assertTrue(self.t4.tournamentplayer_set.filter(player=self.p1).exists())

    def test_tournament_players_register_player(self):
        # Use the form to register a Player
        self.assertFalse(self.t2.tournamentplayer_set.filter(player=self.p2).exists())
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        url = reverse('tournament_players', args=(self.t2.pk,))
        data = urlencode({'form-TOTAL_FORMS': '4',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 0,
                          'form-1-player': str(self.p2.pk)})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect back to the same page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the TournamentPlayer should have been added
        tp_qs = self.t2.tournamentplayer_set.filter(player=self.p2)
        self.assertTrue(tp_qs.exists())
        # new TournamentPlayer should not be unranked
        tp = tp_qs.get()
        self.assertFalse(tp.unranked)
        # Clean up
        tp_qs.delete()

    def test_tournament_players_register_registered_player(self):
        # Use the form to register a Player who is already registered
        self.assertTrue(self.t2.tournamentplayer_set.filter(player=self.p1).exists())
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        url = reverse('tournament_players', args=(self.t2.pk,))
        data = urlencode({'form-TOTAL_FORMS': '4',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 0,
                          'form-1-player': str(self.p1.pk)})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect back to the same page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)

    def test_tournament_players_resend_prefs_email(self):
        # Use the form to re-send the preferences email to a Player
        tp = self.t2.tournamentplayer_set.get(player=self.p1)
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        url = reverse('tournament_players', args=(self.t2.pk,))
        data = urlencode({'prefs_%d' % tp.pk: 'Send prefs email',
                          'form-TOTAL_FORMS': '4',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 0})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect back to the same page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the email should be sent
        self.assertEqual(len(mail.outbox), 1)

    def test_tournament_players_flag_as_unranked(self):
        # Adding a manager as a TournamentPlayer should flag them as unranked
        self.assertFalse(self.t2.tournamentplayer_set.filter(player=self.p11).exists())
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        url = reverse('tournament_players', args=(self.t2.pk,))
        data = urlencode({'form-TOTAL_FORMS': '4',
                          'form-MAX_NUM_FORMS': '1000',
                          'form-INITIAL_FORMS': 0,
                          'form-1-player': str(self.p11.pk)})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # It should redirect back to the same page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the TournamentPlayer should have been added
        tp_qs = self.t2.tournamentplayer_set.filter(player=self.p11)
        self.assertTrue(tp_qs.exists())
        # new TournamentPlayer should be unranked
        tp = tp_qs.get()
        self.assertTrue(tp.unranked)
        # Clean up
        tp_qs.delete()

    def test_seeder_bias_not_logged_in(self):
        response = self.client.get(reverse('seeder_bias', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_seeder_bias_missing_perm(self):
        self.client.login(username=self.USERNAME3, password=self.PWORD3)
        response = self.client.get(reverse('seeder_bias', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_seeder_bias(self):
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        response = self.client.get(reverse('seeder_bias', args=(self.t1.pk,)))
        self.assertEqual(response.status_code, 200)

    def test_seeder_bias_add(self):
        self.assertEqual(SeederBias.objects.filter(player1__tournament=self.t2).count(), 0)
        # TODO Should be able to use USERNAME3 and PASSWORD3 here, but it fails the permission check
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        # Pick two suitable TournamentPlayers
        tp1 = self.t2.tournamentplayer_set.first()
        tp2 = self.t2.tournamentplayer_set.last()
        url = reverse('seeder_bias', args=(self.t2.pk,))
        data = urlencode({'player1': str(tp1.pk),
                          'player2': str(tp2.pk),
                          'weight': '4'})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # it should redirect back to the same URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the SeederBias should be created
        sb_qs = SeederBias.objects.filter(player1__tournament=self.t2)
        self.assertEqual(sb_qs.count(), 1)
        sb = sb_qs.get()
        self.assertEqual(sb.player1, tp1)
        self.assertEqual(sb.player2, tp2)
        self.assertEqual(sb.weight, 4)
        # Clean up
        sb.delete()

    def test_seeder_bias_remove(self):
        # Add two SeederBias objects just for this test
        sb1 = SeederBias.objects.create(player1=self.t2.tournamentplayer_set.first(),
                                        player2=self.t2.tournamentplayer_set.last(),
                                        weight=5)
        sb2 = SeederBias.objects.create(player1=self.t2.tournamentplayer_set.first(),
                                        player2=self.tp29,
                                        weight=3)
        self.assertEqual(SeederBias.objects.filter(player1__tournament=self.t2).count(), 2)
        # TODO Should be able to use USERNAME3 and PASSWORD3 here, but it fails the permission check
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        url = reverse('seeder_bias', args=(self.t2.pk,))
        data = urlencode({'delete_%d' % sb2.pk: 'Remove Bias'})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        # it should redirect back to the same URL
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, url)
        # ... and the SeederBias should be deleted
        self.assertEqual(SeederBias.objects.filter(player1__tournament=self.t2).count(), 1)
        self.assertFalse(SeederBias.objects.filter(pk=sb2.pk).exists())
        # Clean up
        sb1.delete()

    def test_seeder_bias_archived(self):
        # Try to add SeederBias to an archived Tournament
        self.client.login(username=self.USERNAME2, password=self.PWORD2)
        # Pick two suitable TournamentPlayers
        tp1 = self.t4.tournamentplayer_set.first()
        tp2 = self.t4.tournamentplayer_set.last()
        url = reverse('seeder_bias', args=(self.t4.pk,))
        data = urlencode({'player1': str(tp1.pk),
                          'player2': str(tp2.pk),
                          'weight': '4'})
        response = self.client.post(url,
                                    data,
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, 404)
