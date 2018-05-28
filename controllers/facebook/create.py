import datetime, time, os

from facebookads.adobjects.adaccount import AdAccount
from facebookads.adobjects.campaign import Campaign
from facebookads.api import FacebookAdsApi
from facebookads.adobjects.targeting import Targeting
from facebookads.adobjects.adset import AdSet
from facebookads.adobjects.adcreative import AdCreative
from facebookads.adobjects.adcreativeobjectstoryspec import AdCreativeObjectStorySpec
from facebookads.adobjects.adimage import AdImage
from facebookads.adobjects.adcreativelinkdata import AdCreativeLinkData

# Facebook Ad Api
access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
app_secret = os.getenv("FACEBOOK_APP_SECRETE")
app_id = os.getenv("FACEBOOK_APP_ID")


class FBAdCreator:
    post = {}
    ad_account_id = None
    
    def __init__(self, post):
        self.ad_account_id = "act_" + post["fb_ad_account"]
        self.post = post
        FacebookAdsApi.init(app_id=app_id, app_secret=app_secret, access_token=post["access_token"], api_version="v3.0")

    def create_campaign(self):
        error = None
        fields = []
        params = {
            'name': self.post["name"],
            'objective': 'LINK_CLICKS',
            'status': 'PAUSED',
        }
        id = 0
        try:
            result = AdAccount(self.ad_account_id).create_campaign(
                fields=fields,
                params=params,
            )
            id = result['id']
        except Exception as err:
            error = err

        return id, error

    def define_target(self):
        return {
            Targeting.Field.geo_locations: self.post['locations'],
            Targeting.Field.interests: self.post['interests'],
            Targeting.Field.publisher_platforms: ['facebook']
        }

    def define_budget(self, campaign_id, targeting):

        start_time = time.mktime(datetime.datetime.strptime(self.post['from'], "%m/%d/%Y %H:%M:%S").timetuple())
        end_time = time.mktime(datetime.datetime.strptime(self.post['to'], "%m/%d/%Y %H:%M:%S").timetuple())
        adset = AdSet(parent_id=self.ad_account_id)

        adset_params = {
            AdSet.Field.name: self.post['name'] + ' Ad Set',
            AdSet.Field.campaign_id: campaign_id,
            AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
            AdSet.Field.optimization_goal: AdSet.OptimizationGoal.reach,
            AdSet.Field.bid_amount: self.post['bid'],  # TODO:: What is this?
            AdSet.Field.targeting: targeting,
            AdSet.Field.start_time: start_time,
            AdSet.Field.end_time: end_time,
        }

        if self.post['budget_time'] == "Daily":
            adset_params[AdSet.Field.daily_budget] = self.post['total_budget'] * 100

        if self.post['budget_time'] == "Life Time":
            adset_params[AdSet.Field.lifetime_budget] = self.post['total_budget'] * 100

        error = None
        newAdset = None
        adset.update(adset_params)
        try:
            newAdset = adset.remote_create(params={'status': AdSet.Status.paused})
        except Exception as e:
            error = e

        return newAdset, error

    def hash_image(self):
        image = AdImage(parent_id=self.ad_account_id)
        image[AdImage.Field.filename] = self.post['image_path']
        image.remote_create()
        return image[AdImage.Field.hash]

    def ad_creative(self):
        creative = None
        error = None
        try:
            link_data = AdCreativeLinkData()
            link_data[AdCreativeLinkData.Field.message] = self.post['title']
            link_data[AdCreativeLinkData.Field.link] = self.post['link']
            link_data[AdCreativeLinkData.Field.caption] = self.post['link']

            object_story_spec = AdCreativeObjectStorySpec()
            object_story_spec[AdCreativeObjectStorySpec.Field.page_id] = os.getenv("FACEBOOK_PAGE_ID")
            object_story_spec[AdCreativeObjectStorySpec.Field.link_data] = link_data

            creative = AdCreative(parent_id=self.ad_account_id)
            creative[AdCreative.Field.name] = 'AdCreative for ' + self.post['name']
            creative[AdCreative.Field.object_story_spec] = object_story_spec
            creative.remote_create()

        except Exception as err:
            error = err

        return creative, error

    def create_ad(self, adset_id, ad_creative_id):
        ad, error = None, None
        fields = []

        params = {
            'name': self.post['name'] + ' Ad',
            'adset_id': adset_id,
            'creative': {'creative_id': ad_creative_id},
            'status': 'PAUSED',
        }
        try:
            ad = AdAccount(self.ad_account_id, self.ad_account_id, ).create_ad(
                fields=fields,
                params=params,
            )
        except Exception as e:
            error = e
        return ad, error
