# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Benjamin Bertrand
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
# USA.
# http://www.gnu.org/copyleft/gpl.html

import sys
from xbmcswift2 import xbmcgui, xbmc
from collections import deque
from SimpleDownloader import SimpleDownloader
import resources.lib.scraper as scraper
from config import plugin

URLAPI = 'https://api.arretsurimages.net'
URLPLAY = 'http://v42.arretsurimages.net'

URLEMISSION = 'http://www.arretsurimages.net/toutes-les-emissions.php?id=%d&'
# URLAPI = /api/public/contents?aggregates[content_type_slug][post-pop]=1&sort=[%22last_version_at%22,%22DESC%22]

# [dans-le-text]
# if ['associated_video']['provider'] == 'dailymotion':
#   dailymotion_link = ['associated_video']['reference_url']

# do the same with vimeo ?

CONTENT_TYPE = {

}
GRENIER_TYPE = {
}

URL = {'fiveLast': 'http://www.arretsurimages.net/emissions.php?',
       'arretSurImages': URLEMISSION % 1,
       'ligneJaune': URLEMISSION % 2,
       'dansLeTexte': URLEMISSION % 3,
       'auxSources': URLEMISSION % 4,
       'auProchainEpisode': URLEMISSION % 5,
       '14h42': URLEMISSION % 6,
       'CPQJ': URLEMISSION % 7,
      }

#TODO: implement that
SORTMETHOD = ['date_publication', 'nb_vues', 'nb_comments']
STREAMS = ['stream_h264_hq_url', 'stream_h264_url']


def login():
    """Login or exit if it fails"""
    # Only available with a subscription
    # Check if username and password have been set
    username = plugin.get_setting('username', unicode)
    password = plugin.get_setting('password', unicode)
    if not username or not password:
        debug('wait what ?')
        xbmcgui.Dialog().ok(plugin.get_string(30050), plugin.get_string(30051), plugin.get_string(30052))
        sys.exit(0)
    if not scraper.login(username, password):
        xbmcgui.Dialog().ok(plugin.get_string(30050), plugin.get_string(30053))
        sys.exit(0)


def log(msg, level=xbmc.LOGNOTICE):
    xbmc.log('ASI scraper: %s' % msg.encode('utf-8'), level)


def debug(msg):
    log(msg, xbmc.LOGDEBUG)


@plugin.route('/')
def index():
    """Default view"""
    items = [
        {'label': plugin.get_string(30010), 'path': plugin.url_for('emissions')},
        {'label': plugin.get_string(30011), 'path': plugin.url_for('grenier')},
        {'label': plugin.get_string(30012), 'path': plugin.url_for('settings')}
    ]
    return plugin.finish(items)


@plugin.route('/emissions/')
def emissions():
    login()
    items = [
        {'label': plugin.get_string(30010),
         'path': plugin.url_for('show_programs', label='arretSurImages', page='1', category='emissions'),
         },
        {'label': plugin.get_string(30014), # list empty
         'path': plugin.url_for('show_programs', label='post-ppop', page='1', category='emissions'),
         },
        {'label': plugin.get_string(30015), # KO
         'path': plugin.url_for('show_programs', label='classe-tele', page='1', category='emissions'),
         },
        {'label': plugin.get_string(30016), # list empty
         'path': plugin.url_for('show_programs', label='archive-tele', page='1', category='emissions'),
         }
    ]
    return plugin.finish(items)


@plugin.route('/grenier/')
def grenier():
    """Display the available programs categories"""
    login()
    items = [
        {'label': '@rrêt sur images',
         'path': plugin.url_for('show_programs', label='arretSurImages', page='1', category='grenier'),
         'info': {'Plot':plugin.get_string(30031)},
         },
        {'label': 'D@ns le texte',# KO
         'path': plugin.url_for('show_programs', label='dans-le-texte', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30033)},
         },
        {'label': 'Tenk',  # list OK
         'path': plugin.url_for('show_programs', label='tenk-arret-sur-images', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30038)},
         },
        {'label': 'Sur le terrain',  # KO
         'path': plugin.url_for('show_programs', label='sur-le-terrain', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30039)},
         },
        {'label': '14:42', # KO
         'path': plugin.url_for('show_programs', label='14h42', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30036)},
         },
        {'label': "C'est p@s qu'un jeu", # list OK
         'path': plugin.url_for('show_programs', label='cest-pas-quun-jeu', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30037)},
         },
        {'label': '@ux sources', # list OK
         'path': plugin.url_for('show_programs', label='aux-sources', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30034)},
         },
        {'label': '@u Prochain Episode', # KO
         'path': plugin.url_for('show_programs', label='au-prochain-episode', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30035)},
         },
        {'label': 'Ligne j@une', # list OK
         'path': plugin.url_for('show_programs', label='ligne-jaune', page='1', category='grenier'),
         'info': {'Plot': plugin.get_string(30032)},
         }
    ]
    return plugin.finish(items)


@plugin.route('/settings/')
def settings():
    """Open the addon settings"""
    plugin.open_settings()


@plugin.route('/labels/<label>/<page>/<category>/')
def show_programs(label, page, category):
    """Display the list of programs"""
    # sortMethod = SORTMETHOD[plugin.get_setting('sortMethod', int)]
    programs = scraper.Programs(label, category)
    entries = programs.get_programs()
    items = [{'label': program['title'],
              'path': plugin.url_for('play_program', url=program['url']),
              'thumbnail': program['thumb'],
              'is_playable': True,
              'context_menu': [(plugin.get_string(30180),
                                'XBMC.RunPlugin(%s)' %
                                plugin.url_for('download_program',
                                               url=program['url']))],
              } for program in entries]

    # # Add navigation items (Previous / Next) if needed
    # nav_items = programs.get_nav_items()
    # page = int(page)
    # if nav_items['next']:
    #     next_page = str(page + 1)
    #     items.insert(0, {'label': plugin.get_string(30020),
    #                      'path': plugin.url_for('show_programs',
    #                                            label=label,
    #                                            page=next_page)})
    # if nav_items['previous']:
    #     previous_page = str(page - 1)
    #     items.insert(0, {'label': plugin.get_string(30021),
    #                      'path': plugin.url_for('show_programs',
    #                                            label=label,
    #                                            page=previous_page)})

    return plugin.finish(items, update_listing=(page != 1))


@plugin.route('/program/<url>', name='play_program', options={'mode': 'play'})
@plugin.route('/download_program/<url>', name='download_program', options={'mode': 'download'})
def get_program(url, mode):
    """Play or download the selected program"""
    debug('get_program: ' + url)
    video_url = URLPLAY + '/fichiers/' + url
    debug('playing: ' + video_url)

    return play_video(video_url)


@plugin.route('/play/<url>')
def play_video(url):
    """Play the video"""
    return plugin.set_resolved_url(url)


@plugin.route('/download/<url>/<title>')
def download_video(url, title):
    """Download the video"""
    downloader = SimpleDownloader()
    if plugin.get_setting('downloadMode', bool):
        # Ask for the path
        download_path = xbmcgui.Dialog().browse(3, plugin.get_string(30090), 'video')
    else:
        download_path = plugin.get_setting('downloadPath', unicode)
    if download_path:
        params = {'url': url, 'download_path': download_path}
        downloader.download(title, params)


@plugin.route('/parts/<url>/<name>/<icon>')
def get_program_parts(url, name, icon):
    """Display all parts of the program"""
    parts = scraper.get_program_parts(url, name, icon)
    part = parts[0]
    if 'url' in part:
        # Display the main video if available
        main_item = [{'label': part['title'],
                  'path': plugin.url_for('play_video', url=part['url']),
                  'thumbnail': part['thumb'],
                  'is_playable': True,
                  'context_menu': [(plugin.get_string(30180),
                                    'XBMC.RunPlugin(%s)' %
                                        plugin.url_for('download_video',
                                                        url=part['url'],
                                                        title=part['title']))],
                 }]
        parts = parts[1:]
    else:
        main_item = []
    # Display the remaining videos
    items = [{'label': part['title'],
              'path': plugin.url_for('play_video_id', video_id=part['video_id']),
              'thumbnail': part['thumb'],
              'is_playable': True,
              'context_menu': [(plugin.get_string(30180),
                                'XBMC.RunPlugin(%s)' %
                                    plugin.url_for('download_video_id',
                                                    video_id=part['video_id']))],
             } for part in parts]
    return plugin.finish(main_item + items)


@plugin.route('/play_video_id/<video_id>', name='play_video_id', options={'mode': 'play'})
@plugin.route('/download_video_id/<video_id>', name='download_video_id', options={'mode': 'download'})
def get_video_by_id(video_id, mode):
    """Play or download the dailymotion video"""
    streams = deque(STREAMS)
    # Order the streams depending on the quality chosen
    streams.rotate(plugin.get_setting('quality', int) * -1)
    video = scraper.get_video_by_id(video_id, streams)
    if mode == 'play':
        return plugin.set_resolved_url(video['url'])
    elif mode == 'download':
        download_video(video['url'], video['title'])


if __name__ == '__main__':
    plugin.run()
