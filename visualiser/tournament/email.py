# Diplomacy Tournament Visualiser
# Copyright (C) 2014, 2016, 2019 Chris Brand
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

"""
Email-related functions for the Diplomacy Tournament Visualiser.
"""

from django.conf import settings
from django.core import mail
from django.core.mail import send_mail, EmailMessage

def send_board_call(the_round):
    """Send an email to all players in the round with the board calls"""
    # TODO Translation is complex, because we don't want to use the language of the
    # person who triggered seding the email but of the person it's going to
    # and right now we send one email to all the players
    subject = 'Board call for %(tourney)s Round %(round)d' % {'tourney': the_round.tournament,
                                                              'round': the_round.number()}
    email_from = settings.EMAIL_HOST_USER
    # We want to include all the boards in the message,
    # with each player's board at the top of their message
    # Start off with a list of (description, player_email) 2-tuples, one per board
    games = []
    for g in the_round.game_set.all():
        game_text = 'Board %(game)s:\n' % {'game': g.name}
        recipients = []
        for gp in g.gameplayer_set.order_by('power'):
            game_text += '%(power)s: %(player)s\n' % {'power': gp.power,
                                                      'player': gp.player}
            if gp.player.email:
                recipients.append(gp.player.email)
        games.append((game_text, recipients))
    # Put together the common body of the message
    all_games = 'The full round:\n' + '\n'.join([g[0] for g in games])
    # Create one message per game
    messages = []
    for game_text, recipients in games:
        msg_text = 'Your game:\n' + game_text + '\n' + all_games
        if recipients:
            email = EmailMessage(subject=subject,
                                 body=msg_text,
                                 from_email=email_from,
                                 to=[email_from,],
                                 bcc=recipients)
            messages.append(email)
    if messages:
        mail.get_connection().send_messages(messages)

PREFS_EMAIL = """
Hi,
You're receiving this because you are registered for the %(tourney)s Diplomacy tournament.
The tournament is using player preferences to assign Great Powers.
To enter or update your preferences, go to the following web page:
%(url)s
Note 1: this address is unique to you - if you share it with anyone, they will be able to change your preferences!
Note 2: you will get a "Page Not Found" error before the tournament starts.

Enter your preferences as a simple list of power letters, e.g. "FTERGAI".
The first power listed is your first preference, the second is your second choice, and so on.
If you enter fewer than 7 powers, any omitted powers will be prioritised equal last.
You can change your preference list at any time.
The list at the time of board call for each round is the one that will be used for that round.
"""

def send_prefs_email(tournamentplayer, force=False):
    """
    Email the URL to enter preferences to the TournamentPlayer.
    Won't send an email unless the Tournament.power_assignment is PREFERENCES.
    Unless force is True, will only send the email if one hasn't already been sent.
    Note that if force is True, any previous URL will no longer be valid.
    """
    t = tournamentplayer.tournament
    addr = tournamentplayer.player.email
    # Bail if preferences aren't needed for the Tournament
    if not t.powers_assigned_from_prefs():
        return
    # Can't do anything unless we have an email address for the player
    if not addr:
        return
    # Don't send again, unless told to
    if tournamentplayer.uuid_str and not force:
        return
    # Create the email and send it
    msg_body = PREFS_EMAIL % {'tourney': t,
                              'url': tournamentplayer.get_prefs_url()}
    send_mail('Specify power preferences for %s' % t,
              msg_body,
              settings.EMAIL_HOST_USER,
              [addr,])