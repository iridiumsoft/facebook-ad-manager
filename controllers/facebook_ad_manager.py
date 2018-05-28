import os
from flask import Blueprint, request, g, jsonify
from controllers.auth import login_required

from db import db

from controllers.facebook.create import FBAdCreator

api = Blueprint('api', __name__, url_prefix='/fb/')


@api.route('create-campaign')
# @login_required
def create_new_campaign():
    ad = None
    ad_creative = None
    ad_set = None

    fb_ad_manager = FBAdCreator({
        'name': 'TEST',
        'title': 'TEST',
        'text': 'TEST',
        'link': 'http://iridiummarketing.com/',
        'image_path': '~/Desktop/ss.png',
        'fb_ad_account': os.getenv('FACEBOOK_TEST_AD_ACCOUNT'),
        'access_token': os.getenv('FACEBOOK_ACCESS_TOKEN'),
        'from': '05/27/2018 12:00:00',
        'to': '06/27/2018 12:00:00',
        'locations': {'countries': ['US']},
        'interests': [{'id': '6003217093576', 'name': 'Insurance'}],
        'budget_time': 'Daily',
        'total_budget': 5000,
        'bid': 100
    })
    
    campaign_id, error = fb_ad_manager.create_campaign()
    if error is None:
        targeting = fb_ad_manager.define_target()
        ad_set, error = fb_ad_manager.define_budget(campaign_id, targeting)
        if error is None:
            ad_creative, error = fb_ad_manager.ad_creative()
            if error is None and ad_set is not None and ad_creative is not None:
                ad, error = fb_ad_manager.create_ad(ad_set['id'], ad_creative['id'])
                if error is not None:
                    print('error in create_ad', error)
        else:
            print('error in define_budget', error)
    else:
        print('error in create_campaign', error)

    if error is not None:
        return "Error : " + str(error)
    else:
        data = {
            # "user": g.user['user_name'],
            "campaign": campaign_id,
            "ad": ad['id'],
            "ad_set": ad_set['id'],
            "ad_creative": ad_creative['id'],
        }
        db.fb_ad_managers.insert(data)
        print(data)

    return "Done"
