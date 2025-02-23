import json
import time

from flask import Flask, request, make_response

from db import database
from new_pages import new_pages, get_map_pool
import api
from user import User
import create_action

app = Flask(__name__)

@app.route('/api/actions')
def actions():
    return api.action_list()

@app.route('/api/add_user', methods=['POST'])
def add_user():
    return api.add_user(request.json, request.remote_addr)

@app.route('/api/ranked_list/<pool_id>')
def ranked_list_api(pool_id):
    return api.ranked_list(pool_id)

@app.route('/api/ranked_list/<pool_id>/<page>')
def ranked_list_page_api(pool_id, page):
    count = 30
    page = int(page)
    return api.ranked_list(pool_id, offset=page * count)

@app.route('/api/ranked_list_detailed/<pool_id>/<int:page>')
def ranked_list_detailed_api(pool_id, page):
    count = 30
    if request.args.get('per_page'):
        count = min(100, int(request.args.get('per_page')))

    return api.ranked_list_detailed(pool_id, page, count=count)

@app.route('/api/map_pools')
def map_pools_api():
    return api.ranked_lists()

@app.route('/api/announcement')
def announcement_api():
    return api.get_announcement()

@app.route('/api/map_pools_detailed')
def map_pools_detailed_api():
    return api.get_map_pools_detailed()

@app.route('/api/leaderboard/<leaderboard_id>/info')
def leaderboard_info_api(leaderboard_id):
    return api.get_leaderboard_info(leaderboard_id)

@app.route('/api/leaderboard/<leaderboard_id>/scores')
def leaderboard_score_first_api(leaderboard_id):
    return api.get_leaderboard_scores(leaderboard_id, offset=0, count=30)

@app.route('/api/leaderboard/<leaderboard_id>/scores/<page>')
def leaderboard_scores_api(leaderboard_id, page):
    page = int(page)
    count = 30
    return api.get_leaderboard_scores(leaderboard_id, offset=page * count, count=count)

@app.route('/api/leaderboard/<leaderboard_id>/scores_extended/<page>')
def leaderboard_scores_extended_api(leaderboard_id, page):
    page = int(page)

    count = 10
    if request.args.get('per_page'):
        count = min(100, int(request.args.get('per_page')))

    return api.get_leaderboard_scores_extended(leaderboard_id, offset=page * count, count=count)

@app.route('/api/leaderboard/<leaderboard_id>/nearby_scores/<user>')
def laderboard_scores_nearby_api(leaderboard_id, user):
    user = int(user)
    return api.get_leaderboard_scores_nearby(leaderboard_id, user)

@app.route('/api/leaderboard/<leaderboard_id>/friends', methods=['POST'])
def leaderboard_scores_friends_api(leaderboard_id):
    return api.leaderboard_scores_friends(leaderboard_id, request.json['friends'])

@app.route('/api/tools/mass_ss_to_hitbloq', methods=['POST'])
def mass_ss_to_hitbloq_id():
    return api.mass_ss_to_hitbloq_id(request.json['ids'])

@app.route('/api/tools/ss_to_hitbloq/<ss_id>')
def ss_to_hitbloq_id(ss_id):
    return api.ss_to_hitbloq_id(ss_id)

@app.route('/api/tools/ss_registered/<ss_id>')
def ss_registered(ss_id):
    return api.ss_registered(ss_id)

@app.route('/api/users/<user_id>')
def user_basic_api(user_id):
    user_id = int(user_id)
    return api.user_basic_api(user_id)

@app.route('/api/player_rank/<pool_id>/<user>')
def player_rank_api(pool_id, user):
    user = int(user)
    return api.player_rank_api(pool_id, user)

@app.route('/api/ladder/<pool_id>/players/<int:page>')
def ranked_ladder_api(pool_id, page):
    per_page = 10
    if request.args.get('per_page'):
        per_page = min(100, int(request.args.get('per_page')))

    search = request.args.get('search')

    return api.ranked_ladder(pool_id, page, players_per_page=per_page, search=search)

@app.route('/api/ladder/<pool_id>/nearby_players/<int:user_id>')
def ranked_ladder_nearby_api(pool_id, user_id):
    return api.ranked_ladder_nearby(pool_id, user_id)

@app.route('/api/ladder/<pool_id>/friends', methods=['POST'])
def ranked_ladder_friends_api(pool_id):
    return api.ranked_ladder_friends(pool_id, request.json['friends'])

@app.route('/api/user/<int:user_id>/scores')
def user_api(user_id):
    sort_mode = 'cr'
    page = 0
    if request.args.get('sort'):
        sort_mode = request.args.get('sort')
    if request.args.get('page'):
        page = int(request.args.get('page'))
    return api.get_user_scores(user_id, get_map_pool(), sort_mode=sort_mode, page=page)

@app.route('/api/update_user/<int:user_id>')
def update_user(user_id):
    print('received user update request for', user_id)
    last_refresh = database.db['users'].find_one({'_id': user_id})['last_manual_refresh']
    if time.time() - last_refresh > 60:
        action_id = create_action.update_user(user_id, queue_id=1)
        database.db['users'].update_one({'_id': user_id}, {'$set': {'last_manual_refresh': time.time()}})
        return json.dumps({'time': time.time(), 'id': action_id, 'error': None})
    else:
        return json.dumps({'time': last_refresh, 'id': None, 'error': 'refreshed too quickly'})

@app.route('/api/action_status/<action_id>')
def action_id_status(action_id):
    return api.action_id_status(action_id)

@app.route('/api/get_template/<template_id>')
def get_template(template_id):
    return api.get_template(template_id)

@app.route('/api/event')
def get_current_event():
    return api.get_current_event()

@app.route('/')
def new_home():
    html = new_pages['home']()
    return html

@app.route('/about')
def new_about():
    html = new_pages['about']()
    return html

@app.route('/map_pools')
def new_map_pools():
    html = new_pages['map_pools']()
    return html

@app.route('/ladder/<ladder>')
def new_ladder(ladder):
    html = new_pages['ladder'](ladder)
    return html

@app.route('/leaderboard/<leaderboard_id>')
def new_leaderboard(leaderboard_id):
    html = new_pages['leaderboard'](leaderboard_id)
    return html

@app.route('/user/<int:user_id>')
def new_user(user_id):
    html = new_pages['user'](user_id)
    return html

@app.route('/ranked_list/<pool_id>')
def new_ranked_list(pool_id):
    html = new_pages['ranked_list'](pool_id)
    return html

@app.route('/add_user')
def new_add_user():
    html = new_pages['add_user']()
    return html

@app.route('/actions')
def new_actions():
    html = new_pages['actions']()
    return html

if __name__ == "__main__":
    app.run()
