import requests
import json
from dataclasses import dataclass
from .env_config import envs
from urllib.parse import urlencode
from typing import Optional


CONTENT_TYPE = 'application/json'

def encode_url(entity: str, action: Optional[str] = None, entity_id: Optional[str] = None, params: Optional[dict] = None) -> str:
    """
    Encode URL with query parameters.

    :param url: str
    :param params: dict
    :return: str
    """

    base_url = f'https://{envs.company_domain}.pipedrive.com/api/v1/{entity}'

    if action is None and entity_id is None:
        url = base_url
    if action is not None:
        url = f'{base_url}/{action}'
    elif entity_id is not None:
        url = f'{base_url}/{entity_id}'

    if params is None:
        params = {}

    params['api_token'] = envs.api_key
    query_string = urlencode(params)

    return f'{url}?{query_string}'


class Organization:

    def __init__(self, **kwargs):
        """
        :param id: int
        :param name: str
        :param website: str
        :param linkedin: str
        :param owner_id: int
        """

        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.owner_id = kwargs.get('owner_id', None)
        self.website = kwargs.get('website', None)
        self.linkedin = kwargs.get('linkedin', None)

    @staticmethod
    def retrieve_by(name: str) -> list['Organization']:
        """
        Retrieve organizations from Pipedrive by name.

        :param name: str
        :return: list[Organization]
        """

        params = {
            'fields': 'name',
            'term': name,
        }

        url = encode_url(entity='organizations', action='search', params=params)

        response = requests.get(url)
        response_json = response.json()

        data = response_json['data'].get('items', [])
        additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        while additional_data['pagination']['more_items_in_collection']:

            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json['data'].get('items', [])
            additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        if data:
            return [Organization(
                id=result['item']['id'], 
                name=result['item']['name'], 
                owner_id=result['item']['owner']['id'],
                website='',
                linkedin='') for result in data]
        
        return []
    
    @staticmethod
    def create(**kwargs) -> 'Organization':
        """
        Create a new organization in Pipedrive.

        :param name: str
        :param owner_id: int
        :param linkedin: str
        :param website: str
        :return: Organization
        """

        if 'name' not in kwargs:
            print('name is required')
            return None
        
        data = {
            'name': kwargs['name'],
            'owner_id': kwargs.get('owner_id', None),
            'e6b50efd95fed42b00f5b9c4a68b0e7abf935f9a': kwargs.get('linkedin', None),  # custom field
            '1b420d4868fd8f870880be6add510fc5af54f046': kwargs.get('website', None)  # custom field
        }
    
        url = encode_url(entity='organizations')

        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error creating organization - {e}')
            return None
        
        response_json = response.json()

        if response_json['success']:
            return Organization(
                id=response_json['data']['id'],
                name=response_json['data']['name'],
                owner_id=response_json['data']['owner_id']['id'] if response_json['data']['owner_id'] else None
            )
        
        return None


class Person:

    def __init__(self, **kwargs):
        """
        :param id: int
        :param name: str
        :param email: str
        :param organization_id: int
        :param owner_id: int
        :param phone: str
        :param job_title: str
        :param linkedin: str
        """

        self.id = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        self.email = kwargs.get('email', None)
        self.organization_id = kwargs.get('organization_id', None)
        self.owner_id = kwargs.get('owner_id', None)
        self.phone = kwargs.get('phone', None)
        self.job_title = kwargs.get('job_title', None)
        self.linkedin = kwargs.get('linkedin', None)

    @staticmethod
    def retrieve_by(email: str) -> list['Person']:
        """
        Retrieve persons from Pipedrive by email.
        
        :param email: str
        :return: list[Person]
        """

        params = {
            'fields': 'email',
            'term': email,
        }
    
        url = encode_url(entity='persons', action='search', params=params)

        response = requests.get(url)
        response_json = response.json()

        data = response_json['data'].get('items', [])
        additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        while additional_data['pagination']['more_items_in_collection']:

            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json['data'].get('items', [])
            additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})
        
        if data:
            return [
                Person(
                    id=result['item']['id'], 
                    name=result['item']['name'], 
                    email=result['item']['primary_email'],
                    organization_id=result['item']['organization']['id'] if result['item']['organization'] else None,
                    owner_id=result['item']['owner']['id'] if result['item']['owner'] else None,
                    phone=result['item']['phones'][0] if result['item']['phones'] else '',
                    job_title='',
                    linkedin=''
                ) 
                for result in data
            ]
        
        return []
    
    @staticmethod
    def create(**kwargs) -> 'Person':
        """
        Create a new person in Pipedrive.

        :param name: str
        :param org_id: int
        :param email: str
        :param phone: str
        :param owner_id: int
        :param job_title: str
        :param linkedin: str
        :return: Person
        """

        if 'name' not in kwargs:
            print('name is required')
            return None
        
        data = {
            'name': kwargs['name'],
            'org_id': kwargs.get('org_id', None),
            'email': kwargs.get('email', None),
            'phone': kwargs.get('phone', None),
            'owner_id': kwargs.get('owner_id', None),
            'f746ba550001ac6682ab9d4e1b8f44999217250c': kwargs.get('job_title', None),  # custom field
            '275f25452ed859a914f51cad90d349f92f1756ad': kwargs.get('linkedin', None)  # custom field
        }
    
        url = encode_url(entity='persons')

        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error creating person - {e}')
            return None

        response_json = response.json()

        if response_json['success']:
            return Person(
                id=response_json['data']['id'],
                name=response_json['data']['name'],
                email=response_json['data']['primary_email'],
                organization_id=response_json['data']['org_id'],
                owner_id=response_json['data']['owner_id']['id'] if response_json['data']['owner_id'] else None,
                phone=response_json['data']['phone'][0]['value'] if response_json['data']['phone'] else None,
                job_title=response_json['data']['f746ba550001ac6682ab9d4e1b8f44999217250c'],
                linkedin=response_json['data']['275f25452ed859a914f51cad90d349f92f1756ad']
            )
        
        return None


class Deal:
    @dataclass
    class Pipeline:
        sales = 1
        trial = 2
        cs = 3
        marketing = 4

    @dataclass
    class Stage:
        # marketing pipeline
        marketing_new_lead = 18
        marketing_mql = 19
        marketing_meeting_scheduled = 27
        marketing_sql = 20
        marketing_qualified_op = 23
        marketing_in_negotiation = 24
        marketing_trial_poc = 21
        marketing_closed = 22

        # sales pipeline
        sales_mapped = 1
        sales_prospected = 2
        sales_engaging = 26
        sales_meeting_scheduled = 3
        sales_meeting_realized = 4
        sales_qualified = 16
        sales_in_negotiation = 5
        sales_poc = 25
        sales_closed = 17

        # trial pipeline
        trial_started = 6
        trial_engaged = 7
        trial_meeting_scheduled = 8
        trial_meeting_realized = 9
        trial_closed = 10

    @dataclass
    class Owner:
        jessica = 21973448
        sophia = 21976836
        marcelo = 21976847
        bruno = 21985174

    @dataclass
    class Channel:
        none = '(None)'
        rpf = 'RPF'
        personal_network = 'Personal Network'
        event = 'Event'
        google_ads = 'Google Ads'
        linkedin_ads = 'Linkedin Ads'
        website_demo = 'Website Demo'
        outbound = 'Outbound'
        product = 'Product'
        cubo = 'Cubo'

    @dataclass
    class Tag:
        trial = 'In Trial'

    def __init__(self, **kwargs):
        """
        :param id: int
        :param title: str
        :param org_id: int
        :param person_id: int
        :param ads_id: str
        :param campaign_id: str
        :param ad_name: str
        :param stage_id: int
        :param pipeline_id: int
        :param owner_id: int
        :param channel: str
        :param ad_name: str
        :param tag: str
        """

        self.id = kwargs.get('id', None)
        self.title = kwargs.get('title', None)
        self.org_id = kwargs.get('org_id', None)
        self.person_id = kwargs.get('person_id', None)
        self.ads_id = kwargs.get('ads_id', None)
        self.campaign_id = kwargs.get('campaign_id', None)
        self.stage_id = kwargs.get('stage_id', None)
        self.pipeline_id = kwargs.get('pipeline_id', None)
        self.owner_id = kwargs.get('owner_id', None)
        self.channel = kwargs.get('channel', None)
        self.ad_name = kwargs.get('ad_name', None)
        self.tag = kwargs.get('tag', None)

    @property
    def is_meeting_scheduled_or_after(self):
        
        if self.pipeline_id == self.Pipeline.marketing:
            return self.stage_id not in [self.Stage.marketing_new_lead, self.Stage.marketing_mql]
        
        elif self.pipeline_id == self.Pipeline.sales:
            return self.stage_id not in [self.Stage.sales_mapped, self.Stage.sales_prospected, self.Stage.sales_engaging]
        
        elif self.pipeline_id == self.Pipeline.trial:
            return self.stage_id not in [self.Stage.trial_started, self.Stage.trial_engaged]

        else:
            return True

    @staticmethod
    def create(**kwargs) -> 'Deal':
        """
        Create a new deal in Pipedrive.

        :param title: str
        :param org_id: int
        :param person_id: int
        :param stage_id: int
        :param pipeline_id: int
        :param owner_id: int
        :param channel: str
        :param ads_id: str
        :param campaign_id: str
        :param ad_name: str
        :param tag: str
        :return: Deal
        """

        if 'title' not in kwargs:
            print('title is required')
            return None

        data = {
            'title': kwargs['title'],
            'org_id': kwargs.get('org_id', None),
            'person_id': kwargs.get('person_id', None),
            'stage_id': kwargs.get('stage_id', None),
            'pipeline_id': kwargs.get('pipeline_id', None),
            'user_id': kwargs.get('owner_id', None),
            'channel': kwargs.get('channel', None),
            '67e90727a702feaee708eb4be15c896f1e4d125e': kwargs.get('ads_id', None),  # custom field
            '90ee914e411f8e76eda8b270c576fa20ce945af6': kwargs.get('campaign_id', None),  # custom field
            'cb5af1d8630657fc3ab4bb01c243f993141df2e7': kwargs.get('ad_name', None),  # custom field
            '70a34135774fbab2a37608d3d4c5da3be9dfa10a': kwargs.get('tag', None)  # custom field
        }

        url = encode_url(entity='deals')

        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error creating deal - {e}')
            return None

        response_json = response.json()

        if response_json['success']:
            return Deal(
                id=response_json['data']['id'],
                title=response_json['data']['title'],
                org_id=response_json['data']['org_id']['value'] if response_json['data']['org_id'] else None,
                person_id=response_json['data']['person_id']['value'] if response_json['data']['person_id'] else None,
                ads_id=response_json['data']['67e90727a702feaee708eb4be15c896f1e4d125e'],
                campaign_id=response_json['data']['90ee914e411f8e76eda8b270c576fa20ce945af6'],
                ad_name=response_json['data']['cb5af1d8630657fc3ab4bb01c243f993141df2e7'],
                stage_id=response_json['data']['stage_id'],
                pipeline_id=response_json['data']['pipeline_id'],
                owner_id=response_json['data']['user_id']['id'] if response_json['data']['user_id'] else None,
                channel=response_json['data']['channel'],
                tag=response_json['data']['70a34135774fbab2a37608d3d4c5da3be9dfa10a']
            )

    @staticmethod
    def get_all_deals() -> list['Deal']:
        
        url = encode_url(entity='deals', params={ 'limit': 500 })

        response = requests.get(url)
        response_json = response.json()

        data = response_json['data']
        additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        while additional_data['pagination']['more_items_in_collection']:

            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json['data'].get('items', [])
            additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        if data:
            return [
                Deal(
                    id=result['id'],
                    title=result['title'],
                    org_id=result['org_id']['value'] if result['org_id'] else None,
                    person_id=result['person_id']['value'] if result['person_id'] else None,
                    stage_id=result['stage_id'],
                    pipeline_id=result['pipeline_id'],
                    owner_id=result['user_id']['id'] if result['user_id'] else None,
                    channel=result['channel'],
                    ads_id=result['67e90727a702feaee708eb4be15c896f1e4d125e'],
                    campaign_id=result['90ee914e411f8e76eda8b270c576fa20ce945af6'],
                    ad_name=result['cb5af1d8630657fc3ab4bb01c243f993141df2e7'],
                    tag=result['70a34135774fbab2a37608d3d4c5da3be9dfa10a']
                ) 
                for result in data
            ]
        
        return []

    def update(self, **kwargs) -> 'Deal':
        """
        Update a deal in Pipedrive.

        :param title: str
        :param org_id: int
        :param person_id: int
        :param stage_id: int
        :param pipeline_id: int
        :param owner_id: int
        :param channel: int
        :param ads_id: str
        :param campaign_id: str
        :param ad_name: str
        :param tag: str
        :return: Deal"""

        url = encode_url(entity='deals', entity_id=self.id)

        data = {}

        data['title'] = kwargs.get('title', self.title)
        data['org_id'] = kwargs.get('org_id', self.org_id)
        data['person_id'] = kwargs.get('person_id', self.person_id)
        data['stage_id'] = kwargs.get('stage_id', self.stage_id)
        data['pipeline_id'] = kwargs.get('pipeline_id', self.pipeline_id)
        data['user_id'] = kwargs.get('owner_id', self.owner_id)
        data['channel'] = kwargs.get('channel', self.channel)
        data['67e90727a702feaee708eb4be15c896f1e4d125e'] = kwargs.get('ads_id', self.ads_id)
        data['90ee914e411f8e76eda8b270c576fa20ce945af6'] = kwargs.get('campaign_id', self.campaign_id)
        data['cb5af1d8630657fc3ab4bb01c243f993141df2e7'] = kwargs.get('ad_name', self.ad_name),
        data['70a34135774fbab2a37608d3d4c5da3be9dfa10a'] = kwargs.get('tag', self.tag)

        try:
            response = requests.put(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error updating deal - {e}')
            return None

        response_json = response.json()

        if response_json['success']:
            return Deal(
                id=response_json['data']['id'],
                title=response_json['data']['title'],
                org_id=response_json['data']['org_id'],
                person_id=response_json['data']['person_id'],
                stage_id=response_json['data']['stage_id'],
                pipeline_id=response_json['data']['pipeline_id'],
                owner_id=response_json['data']['user_id']['id'] if response_json['data']['user_id'] else None,
                channel=response_json['data']['channel'],
                ads_id=response_json['data']['67e90727a702feaee708eb4be15c896f1e4d125e'],
                campaign_id=response_json['data']['90ee914e411f8e76eda8b270c576fa20ce945af6'],
                ad_name=response_json['data']['cb5af1d8630657fc3ab4bb01c243f993141df2e7'],
                tag=response_json['data']['70a34135774fbab2a37608d3d4c5da3be9dfa10a']
            )
        
    def move_in_pipeline(self) -> 'Deal':

        if self.is_meeting_scheduled_or_after:
            return self
        
        else:
            if self.pipeline_id == Deal.Pipeline.marketing:
                new_stage_id = Deal.Stage.marketing_meeting_scheduled
            elif self.pipeline_id == Deal.Pipeline.sales:
                new_stage_id = Deal.Stage.sales_meeting_scheduled
            elif self.pipeline_id == Deal.Pipeline.trial:
                new_stage_id = Deal.Stage.trial_meeting_scheduled

            updated = self.update(stage_id=new_stage_id)
            return updated


class Activity:
    
    @dataclass
    class Type:
        signup = 'sign_up'
        meeting = 'meeting'
        follow_up = 'task'

    def __init__(self, **kwargs):
        """
        :param id: int
        :param deal_id: int
        :param subject: str
        :param type: str
        :param due_date: str
        :param due_time: str
        :param duration: str
        :param org_id: int
        :param person_id: int
        :param note: str
        :param done: bool
        :param participants_ids: list[int]
        """
        
        self.id = kwargs.get('id', None)
        self.deal_id = kwargs.get('deal_id', None)
        self.subject = kwargs.get('subject', None)
        self.type = kwargs.get('type', None)
        self.due_date = kwargs.get('due_date', None)
        self.due_time = kwargs.get('due_time', None)
        self.duration = kwargs.get('duration', None)
        self.org_id = kwargs.get('org_id', None)
        self.person_id = kwargs.get('person_id', None)
        self.note = kwargs.get('note', None)
        self.done = kwargs.get('done', False)

        if 'participants_ids' in kwargs:
            self.participants_ids = kwargs['participants_ids'] if kwargs['participants_ids'] is not None else []
        elif self.person_id is not None:
            self.participants_ids = [self.person_id]
        else:
            self.participants_ids = []


    @staticmethod
    def create(**kwargs) -> 'Activity':
        """
        Create a new activity in Pipedrive.

        :param deal_id: int
        :param subject: str
        :param type: str
        :param note: str
        :param due_date: str
        :param due_time: str
        :param duration: str
        :param participants_ids: list[int]
        :param done: bool
        :return: Activity
        """


        if 'deal_id' not in kwargs or 'subject' not in kwargs:
            print('deal_id and subject are required')
            return None

        url = encode_url(entity='activities')

        data = {
            'deal_id': kwargs['deal_id'],
            'subject': kwargs['subject'],
            'type': kwargs.get('type', 'Meeting'),
            'note': kwargs.get('note', None),
            'due_date': kwargs.get('due_date', None),
            'due_time': kwargs.get('due_time', None),
            'duration': kwargs.get('duration', None),
            'done': kwargs.get('done', False)
        }

        if 'participants_ids' in kwargs:
            data['participants'] = [{'person_id': id, 'primary_flag': False} for id in kwargs['participants_ids']]
            data['participants'][0]['primary_flag'] = True

        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error creating task - {e}')
            return None

        response_json = response.json()

        if response_json['success']:
            return Activity(
                id=response_json['data']['id'],
                deal_id=response_json['data']['deal_id'],
                subject=response_json['data']['subject'],
                type=response_json['data']['type'],
                due_date=response_json['data']['due_date'],
                due_time=response_json['data']['due_time'],
                duration=response_json['data']['duration'],
                org_id=response_json['data']['org_id'],
                person_id=response_json['data']['person_id'],
                participants_ids=[r['person_id'] for r in response_json['data']['participants']] if response_json['data']['participants'] is not None else None,
                note=response_json['data']['note'],
                done=response_json['data']['done']
            )

    @staticmethod
    def get_all_activities() -> list['Activity']:
        
        url = encode_url(entity='activities', params={ 'limit': 500 })

        response = requests.get(url)
        response_json = response.json()

        data = response_json['data']
        additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        while additional_data['pagination']['more_items_in_collection']:

            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json['data'].get('items', [])
            additional_data = response_json.get('additional_data', {'pagination': {'more_items_in_collection': False}})

        if data:
            return [
                Activity(
                    id=result['id'],
                    deal_id=result['deal_id'],
                    subject=result['subject'],
                    type=result['type'],
                    due_date=result['due_date'],
                    due_time=result['due_time'],
                    duration=result['duration'],
                    org_id=result['org_id'],
                    person_id=result['person_id'],
                    participants_ids=[r['person_id'] for r in result['participants']] if result['participants'] is not None else None,
                    note=result['note'],
                    done=result['done']
                ) 
                for result in data
            ]
        
        return [] 
    
    def update(self, **kwargs) -> 'Activity':
        """
        Update an activity in Pipedrive.
        
        :param deal_id: int
        :param subject: str
        :param type: str
        :param note: str
        :param due_date: str
        :param due_time: str
        :param duration: str
        :param participants_ids: list[int]
        :param done: bool
        :return: Activity
        """

        url = encode_url(entity='activities', entity_id=self.id)

        data = {}

        data['deal_id'] = kwargs.get('deal_id', self.deal_id)
        data['subject'] = kwargs.get('subject', self.subject)
        data['type'] = kwargs.get('type', self.type)
        data['due_date'] = kwargs.get('due_date', self.due_date)
        data['due_time'] = kwargs.get('due_time', self.due_time)
        data['duration'] = kwargs.get('duration', self.duration)
        data['done'] = kwargs.get('done', False)

        if 'note' in kwargs:
            note = kwargs['note']
            data['note'] = self.note + ' / ' + note if self.note is not None else note

        if 'participants_ids' in kwargs:
            participants_ids = list(set(kwargs['participants_ids']).union(self.participants_ids))
            data['participants'] = [{'person_id': id, 'primary_flag': False} for id in participants_ids]
            data['participants'][0]['primary_flag'] = True

        try:
            response = requests.put(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error updating deal - {e}')
            return None
        
        response_json = response.json()

        if response_json['success']:
            return Activity(id=response_json['data']['id'],
                deal_id=response_json['data']['deal_id'],
                subject=response_json['data']['subject'],
                type=response_json['data']['type'],
                due_date=response_json['data']['due_date'],
                due_time=response_json['data']['due_time'],
                duration=response_json['data']['duration'],
                org_id=response_json['data']['org_id'],
                person_id=response_json['data']['person_id'],
                participants_ids=[r['person_id'] for r in response_json['data']['participants']] if response_json['data']['participants'] is not None else None,
                note=response_json['data']['note'],
                done=response_json['data']['done']
            )
        

class Notes:

    def __init__(self, **kwargs) -> None:
        """
        :param id: int
        :param deal_id: int
        :param content: str
        """

        self.id = kwargs.get('id', None)
        self.deal_id = kwargs.get('deal_id', None)
        self.content = kwargs.get('content', None)

    @staticmethod
    def create(**kwargs) -> 'Notes':
        """
        Create a new note in Pipedrive.

        :param deal_id: int
        :param content: str
        :return: Notes
        """

        if 'deal_id' not in kwargs or 'content' not in kwargs:
            print('deal_id and content are required')
            return None

        url = encode_url(entity='notes')

        data = {
            'deal_id': kwargs['deal_id'],
            'content': kwargs['content']
        }

        try:
            response = requests.post(url, data=json.dumps(data), headers={'Content-Type': CONTENT_TYPE})
            response.raise_for_status()
        except Exception as e:
            print(f'Error creating note - {e}')
            return None

        response_json = response.json()

        if response_json['success']:
            return Notes(
                id=response_json['data']['id'],
                deal_id=response_json['data']['deal_id'],
                content=response_json['data']['content']
            )
        