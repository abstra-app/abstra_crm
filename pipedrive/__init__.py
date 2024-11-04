import requests
import json
from dataclasses import dataclass
from .env_config import envs
from urllib.parse import urlencode
from typing import Optional, Callable
from datetime import datetime, timezone


CONTENT_TYPE = "application/json"
GENERIC_DOMAINS = generic_email_domains = [
    "aol.com",
    "aol.com.br",
    "bol.com",
    "bol.com.br",
    "countermail.com",
    "countermail.com.br",
    "disroot.org",
    "disroot.org.br",
    "fastmail.com",
    "fastmail.com.br",
    "gmail.com",
    "gmail.com.br",
    "gmx.com",
    "gmx.com.br",
    "hotmail.com",
    "hotmail.com.br",
    "hushmail.com",
    "hushmail.com.br",
    "icloud.com",
    "icloud.com.br",
    "keemail.me",
    "keemail.me.br",
    "kolabnow.com",
    "kolabnow.com.br",
    "lavabit.com",
    "lavabit.com.br",
    "live.com",
    "live.com.br",
    "mail.com",
    "mail.com.br",
    "mail.ru",
    "mail.ru.br",
    "mailbox.org",
    "mailbox.org.br",
    "msn.com",
    "msn.com.br",
    "outlook.com",
    "outlook.com.br",
    "posteo.de",
    "posteo.de.br",
    "protonmail.com",
    "protonmail.com.br",
    "rippermail.com",
    "rippermail.com.br",
    "runbox.com",
    "runbox.com.br",
    "tutanota.com",
    "tutanota.com.br",
    "uol.com",
    "uol.com.br",
    "yahoo.com",
    "yahoo.com.br",
    "yandex.com",
    "yandex.com.br",
    "ymail.com",
    "ymail.com.br",
    "zoho.com",
    "zoho.com.br",
]


def encode_url(
    entity: str,
    action: Optional[str] = None,
    entity_id: Optional[str] = None,
    subpath: Optional[str] = None,
    params: Optional[dict] = None,
    version: Optional[str] = "v1",
) -> str:
    """
    Encode URL with query parameters.

    :param url: str
    :param params: dict
    :return: str
    """

    base_url = f"https://{envs.company_domain}.pipedrive.com/api/{version}/{entity}"
    url = ""

    if action is None and entity_id is None:
        url = base_url

    if action is not None:
        url = f"{base_url}/{action}"
    elif entity_id is not None:
        url = f"{base_url}/{entity_id}"

    if subpath is not None:
        url = f"{url}/{subpath}"

    if params is None:
        params = {}

    params["api_token"] = envs.api_key
    query_string = urlencode(params)

    return f"{url}?{query_string}"


class Organization:
    def __init__(self, **kwargs):
        """
        :param id: int
        :param name: str
        :param website: str
        :param linkedin: str
        :param owner_id: int
        """

        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)
        self.owner_id = kwargs.get("owner_id", None)
        self.website = kwargs.get("website", None)
        self.linkedin = kwargs.get("linkedin", None)

    @staticmethod
    def retrieve_by(name: str) -> list["Organization"]:
        """
        Retrieve organizations from Pipedrive by name.

        :param name: str
        :return: list[Organization]
        """

        params = {
            "fields": "name",
            "term": name,
        }

        url = encode_url(entity="organizations", action="search", params=params)

        response = requests.get(url)
        response_json = response.json()

        data = response_json["data"].get("items", [])
        additional_data = response_json.get(
            "additional_data", {"pagination": {"more_items_in_collection": False}}
        )

        while additional_data["pagination"]["more_items_in_collection"]:
            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"].get("items", [])
            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

        if data:
            return [
                Organization(
                    id=result["item"]["id"],
                    name=result["item"]["name"],
                    owner_id=result["item"]["owner"]["id"],
                    website="",
                    linkedin="",
                )
                for result in data
            ]
        else:
            return []

        return []

    @staticmethod
    def create(**kwargs) -> "Organization":
        """
        Create a new organization in Pipedrive.

        :param name: str
        :param owner_id: int
        :param linkedin: str
        :param website: str
        :return: Organization
        """

        if "name" not in kwargs:
            print("name is required")
            return None

        data = {
            "name": kwargs["name"],
            "owner_id": kwargs.get("owner_id", None),
            "e6b50efd95fed42b00f5b9c4a68b0e7abf935f9a": kwargs.get(
                "linkedin", None
            ),  # custom field
            "1b420d4868fd8f870880be6add510fc5af54f046": kwargs.get(
                "website", None
            ),  # custom field
        }

        url = encode_url(entity="organizations")

        try:
            response = requests.post(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error creating organization - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Organization(
                id=response_json["data"]["id"],
                name=response_json["data"]["name"],
                owner_id=response_json["data"]["owner_id"]["id"]
                if response_json["data"]["owner_id"]
                else None,
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

        self.id = kwargs.get("id", None)
        self.name = kwargs.get("name", None)
        self.email = kwargs.get("email", None)
        self.organization_id = kwargs.get("organization_id", None)
        self.owner_id = kwargs.get("owner_id", None)
        self.phone = kwargs.get("phone", None)
        self.job_title = kwargs.get("job_title", None)
        self.linkedin = kwargs.get("linkedin", None)

    @staticmethod
    def retrieve_by(email: str) -> list["Person"]:
        """
        Retrieve persons from Pipedrive by email.

        :param email: str
        :return: list[Person]
        """

        params = {
            "fields": "email",
            "term": email,
        }

        url = encode_url(entity="persons", action="search", params=params)

        response = requests.get(url)
        response_json = response.json()

        data = response_json["data"].get("items", [])
        additional_data = response_json.get(
            "additional_data", {"pagination": {"more_items_in_collection": False}}
        )

        while additional_data["pagination"]["more_items_in_collection"]:
            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"].get("items", [])
            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

        if data:
            return [
                Person(
                    id=result["item"]["id"],
                    name=result["item"]["name"],
                    email=result["item"]["primary_email"],
                    organization_id=result["item"]["organization"]["id"]
                    if result["item"]["organization"]
                    else None,
                    owner_id=result["item"]["owner"]["id"]
                    if result["item"]["owner"]
                    else None,
                    phone=result["item"]["phones"][0]
                    if result["item"]["phones"]
                    else "",
                    job_title="",
                    linkedin="",
                )
                for result in data
            ]
        else:
            return []

    @staticmethod
    def retrieve_by_phone(phone: str) -> list["Person"]:
        """
        Retrieve persons from Pipedrive by phone.

        :param phone: str
        :return: list[Person]
        """

        params = {
            "fields": "phone",
            "term": phone,
        }

        url = encode_url(entity="persons", action="search", params=params)

        response = requests.get(url)
        response_json = response.json()

        # ! Remove this line after testing
        print(response.text)

        # ! Temporary fix for the response
        if "data" not in response_json:
            return []

        data = response_json["data"].get("items", [])
        additional_data = response_json.get(
            "additional_data", {"pagination": {"more_items_in_collection": False}}
        )

        while additional_data["pagination"]["more_items_in_collection"]:
            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"].get("items", [])
            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

        if data:
            return [
                Person(
                    id=result["item"]["id"],
                    name=result["item"]["name"] if result["item"]["name"] else "",
                    email=result["item"]["primary_email"]
                    if result["item"]["primary_email"]
                    else "",
                    organization_id=result["item"]["organization"]["id"]
                    if result["item"]["organization"]
                    else None,
                    owner_id=result["item"]["owner"]["id"]
                    if result["item"]["owner"]
                    else None,
                    phone=result["item"]["phones"][0]
                    if result["item"]["phones"]
                    else "",
                )
                for result in data
            ]
        else:
            return []

    @staticmethod
    def create(**kwargs) -> "Person":
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

        if "name" not in kwargs:
            print("name is required")
            return None

        data = {
            "name": kwargs["name"],
            "org_id": kwargs.get("org_id", None),
            "email": kwargs.get("email", None),
            "phone": kwargs.get("phone", None),
            "owner_id": kwargs.get("owner_id", None),
            "f746ba550001ac6682ab9d4e1b8f44999217250c": kwargs.get(
                "job_title", None
            ),  # custom field
            "275f25452ed859a914f51cad90d349f92f1756ad": kwargs.get(
                "linkedin", None
            ),  # custom field
        }

        url = encode_url(entity="persons")

        try:
            response = requests.post(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error creating person - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Person(
                id=response_json["data"]["id"],
                name=response_json["data"]["name"],
                email=response_json["data"]["primary_email"],
                organization_id=response_json["data"]["org_id"],
                owner_id=response_json["data"]["owner_id"]["id"]
                if response_json["data"]["owner_id"]
                else None,
                phone=response_json["data"]["phone"][0]["value"]
                if response_json["data"]["phone"]
                else None,
                job_title=response_json["data"][
                    "f746ba550001ac6682ab9d4e1b8f44999217250c"
                ],
                linkedin=response_json["data"][
                    "275f25452ed859a914f51cad90d349f92f1756ad"
                ],
            )

        return None

    def extract_domain(self):
        if self.email is None:
            return None
        if "@" not in self.email:
            return None

        return self.email.split("@")[1]


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
        marketing_contact_sent = 29
        marketing_engaging = 28

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
        none = "(None)"
        rpf = "RPF"
        personal_network = "Personal Network"
        event = "Event"
        google_ads = "Google Ads"
        linkedin_ads = "Linkedin Ads"
        website_demo = "Website Demo"
        outbound = "Outbound"
        product = "Product"
        cubo = "Cubo"

    @dataclass
    class Tag:
        trial = "In Trial"

    @dataclass
    class Milestone:
        contact_with_influencer = 35
        contact_with_buyer = 36
        contact_with_technical_decision_maker = 40
        usecase_mapped = 37
        urgency_for_usecase = 38
        budget_available = 39
        pricing_presented = 84
        capable_editors = 41
        appoved_by_technical_decision_maker = 42
        appoved_by_buyer = 43

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
        :param tag: str
        :param use_case: str
        :param company_domain: str
        :param abstra_cloud_org_id: str
        :param value: int
        :param qualification_milestone: comma separated string
        :param status: str
        :param lost_reason: str
        :param add_time: str iso format
        """

        self.id = kwargs.get("id", None)
        self.title = kwargs.get("title", None)
        self.org_id = kwargs.get("org_id", None)
        self.person_id = kwargs.get("person_id", None)
        self.ads_id = kwargs.get("ads_id", None)
        self.campaign_id = kwargs.get("campaign_id", None)
        self.stage_id = kwargs.get("stage_id", None)
        self.pipeline_id = kwargs.get("pipeline_id", None)
        self.owner_id = kwargs.get("owner_id", None)
        self.channel = kwargs.get("channel", None)
        self.ad_name = kwargs.get("ad_name", None)
        self.tag = kwargs.get("tag", None)
        self.use_case = kwargs.get("use_case", None)
        self.company_domain = kwargs.get("company_domain", None)
        self.abstra_cloud_org_id = kwargs.get("abstra_cloud_org_id", None)
        self.value = kwargs.get("value", None)
        self.qualification_milestone = kwargs.get("qualification_milestone", None)
        self.status = kwargs.get("status", None)
        self.lost_reason = kwargs.get("lost_reason", None)
        self.add_time = kwargs.get("add_time", None)

    @property
    def is_meeting_scheduled_or_after(self):
        if self.pipeline_id == self.Pipeline.marketing:
            return self.stage_id not in [
                self.Stage.marketing_new_lead,
                self.Stage.marketing_mql,
            ]

        elif self.pipeline_id == self.Pipeline.sales:
            return self.stage_id not in [
                self.Stage.sales_mapped,
                self.Stage.sales_prospected,
                self.Stage.sales_engaging,
            ]

        elif self.pipeline_id == self.Pipeline.trial:
            return self.stage_id not in [
                self.Stage.trial_started,
                self.Stage.trial_engaged,
            ]

        else:
            return True

    @staticmethod
    def create(**kwargs) -> "Deal":
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
        :param use_case: str
        :param company_domain: str
        :param abstra_cloud_org_id: str
        :param value: int
        :param qualification_milestone: comma separated string
        :param status: str
        :param lost_reason: str
        :param add_time: str iso format
        :return: Deal
        """

        if "title" not in kwargs:
            print("title is required")
            return None

        company_domain = kwargs.get("company_domain", None)
        if company_domain in GENERIC_DOMAINS:
            company_domain = None

        data = {
            "title": kwargs["title"],
            "org_id": kwargs.get("org_id", None),
            "person_id": kwargs.get("person_id", None),
            "stage_id": kwargs.get("stage_id", None),
            "pipeline_id": kwargs.get("pipeline_id", None),
            "user_id": kwargs.get("owner_id", None),
            "channel": kwargs.get("channel", None),
            "67e90727a702feaee708eb4be15c896f1e4d125e": kwargs.get(
                "ads_id", None
            ),  # custom field
            "90ee914e411f8e76eda8b270c576fa20ce945af6": kwargs.get(
                "campaign_id", None
            ),  # custom field
            "cb5af1d8630657fc3ab4bb01c243f993141df2e7": kwargs.get(
                "ad_name", None
            ),  # custom field
            "70a34135774fbab2a37608d3d4c5da3be9dfa10a": kwargs.get(
                "tag", None
            ),  # custom field
            "aa6cbdaafd283f46db835b902902f549e86bb915": kwargs.get(
                "use_case", None
            ),  # custom field
            "34d3f450e4c96e0390b8dd9a7a034e7d64c53db0": company_domain,  # custom field
            "68396303430f23178b5bc6978b5b3021cf5eff47": kwargs.get(
                "abstra_cloud_org_id", None
            ),  # custom field
            "value": kwargs.get("value", None),
            "5abfbfa90d21348b998b9c259392182130d04647": kwargs.get(
                "qualification_milestone", None
            ),  # custom field
            "status": kwargs.get("status", None),
            "lost_reason": kwargs.get("lost_reason", None),
            "add_time": kwargs.get("add_time", None),
        }

        url = encode_url(entity="deals")

        try:
            response = requests.post(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error creating deal - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Deal(
                id=response_json["data"]["id"],
                title=response_json["data"]["title"],
                org_id=response_json["data"]["org_id"]["value"]
                if response_json["data"]["org_id"]
                else None,
                person_id=response_json["data"]["person_id"]["value"]
                if response_json["data"]["person_id"]
                else None,
                ads_id=response_json["data"][
                    "67e90727a702feaee708eb4be15c896f1e4d125e"
                ],
                campaign_id=response_json["data"][
                    "90ee914e411f8e76eda8b270c576fa20ce945af6"
                ],
                ad_name=response_json["data"][
                    "cb5af1d8630657fc3ab4bb01c243f993141df2e7"
                ],
                stage_id=response_json["data"]["stage_id"],
                pipeline_id=response_json["data"]["pipeline_id"],
                owner_id=response_json["data"]["user_id"]["id"]
                if response_json["data"]["user_id"]
                else None,
                channel=response_json["data"]["channel"],
                tag=response_json["data"]["70a34135774fbab2a37608d3d4c5da3be9dfa10a"],
                use_case=response_json["data"][
                    "aa6cbdaafd283f46db835b902902f549e86bb915"
                ],
                company_domain=response_json["data"][
                    "34d3f450e4c96e0390b8dd9a7a034e7d64c53db0"
                ],
                abstra_cloud_org_id=response_json["data"][
                    "68396303430f23178b5bc6978b5b3021cf5eff47"
                ],
                value=response_json["data"]["value"],
                status=response_json["data"]["status"],
                lost_reason=response_json["data"]["lost_reason"],
                add_time=response_json["data"]["add_time"],
                qualification_milestone=response_json["data"][
                    "5abfbfa90d21348b998b9c259392182130d04647"
                ],
            )

    @staticmethod
    def get_all_deals() -> list["Deal"]:
        url = encode_url(entity="deals", params={"limit": 500})

        response = requests.get(url)
        response_json = response.json()

        data = response_json["data"]
        additional_data = response_json.get(
            "additional_data", {"pagination": {"more_items_in_collection": False}}
        )

        while additional_data["pagination"]["more_items_in_collection"]:
            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"]
            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

        if data:
            return [
                Deal(
                    id=result["id"],
                    title=result["title"],
                    org_id=result["org_id"]["value"] if result["org_id"] else None,
                    person_id=result["person_id"]["value"]
                    if result["person_id"]
                    else None,
                    stage_id=result["stage_id"],
                    pipeline_id=result["pipeline_id"],
                    owner_id=result["user_id"]["id"] if result["user_id"] else None,
                    channel=result["channel"],
                    ads_id=result["67e90727a702feaee708eb4be15c896f1e4d125e"],
                    campaign_id=result["90ee914e411f8e76eda8b270c576fa20ce945af6"],
                    ad_name=result["cb5af1d8630657fc3ab4bb01c243f993141df2e7"],
                    tag=result["70a34135774fbab2a37608d3d4c5da3be9dfa10a"],
                    use_case=result["aa6cbdaafd283f46db835b902902f549e86bb915"],
                    company_domain=result["34d3f450e4c96e0390b8dd9a7a034e7d64c53db0"],
                    absrta_cloud_org_id=result[
                        "68396303430f23178b5bc6978b5b3021cf5eff47"
                    ],
                    value=result["value"],
                    status=result["status"],
                    lost_reason=result["lost_reason"],
                    add_time=result["add_time"],
                    qualification_milestone=result[
                        "5abfbfa90d21348b998b9c259392182130d04647"
                    ],
                )
                for result in data
            ]
        else:
            return []

    @staticmethod
    def get_deals_by_person_id(person_id: int) -> list["Deal"]:
        """
        Retrieve Deals from Pipedrive by Person_id.

        :param person_id: int
        :return: list[Deal]
        """

        params = {"person_id": person_id}

        url = encode_url(entity="deals", params=params, version="v2")

        response = requests.get(url)
        response_json = response.json()

        data = response_json["data"]
        additional_data = response_json.get("additional_data", {"next_cursor": None})
        cursor = additional_data["next_cursor"]

        while cursor:
            new_url = url + f"&cursor={cursor}"
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"]
            additional_data = response_json.get(
                "additional_data", {"next_cursor": None}
            )
            cursor = additional_data["next_cursor"]
        if data:
            return [
                Deal(
                    id=result["id"],
                    title=result["title"],
                    org_id=result["org_id"],
                    person_id=result["person_id"],
                    stage_id=result["stage_id"],
                    pipeline_id=result["pipeline_id"],
                    owner_id=result["owner_id"],
                    channel=result["channel"],
                    status=result["status"],
                )
                for result in data
            ]
        else:
            return []

    @staticmethod
    def from_dict(data: dict) -> "Deal":
        return Deal(
            id=data["id"],
            title=data["title"],
            org_id=data["org_id"]["value"] if data["org_id"] else None,
            person_id=data["person_id"]["value"] if data["person_id"] else None,
            stage_id=data["stage_id"],
            pipeline_id=data["pipeline_id"],
            owner_id=data["user_id"]["id"] if data["user_id"] else None,
            channel=data["channel"],
            ads_id=data["67e90727a702feaee708eb4be15c896f1e4d125e"],
            campaign_id=data["90ee914e411f8e76eda8b270c576fa20ce945af6"],
            ad_name=data["cb5af1d8630657fc3ab4bb01c243f993141df2e7"],
            tag=data["70a34135774fbab2a37608d3d4c5da3be9dfa10a"],
            use_case=data["aa6cbdaafd283f46db835b902902f549e86bb915"],
            company_domain=data["34d3f450e4c96e0390b8dd9a7a034e7d64c53db0"],
            absrta_cloud_org_id=data["68396303430f23178b5bc6978b5b3021cf5eff47"],
            value=data["value"],
            status=data["status"],
            lost_reason=data["lost_reason"],
            add_time=data["add_time"],
            qualification_milestone=data["5abfbfa90d21348b998b9c259392182130d04647"],
        )

    @staticmethod
    def filter(
        filter_function: Callable[["Deal"], bool] = lambda _: True,
    ) -> list["Deal"]:
        url = encode_url(entity="deals", params={"limit": 200})

        filtered_deals = []
        additional_data = {"pagination": {"more_items_in_collection": True}}

        while additional_data["pagination"]["more_items_in_collection"]:
            response = requests.get(url)
            response_json = response.json()

            current_page_data = response_json["data"]
            if current_page_data:
                deal_list = [Deal.from_dict(result) for result in current_page_data]
                filtered_deals = filtered_deals + list(
                    filter(filter_function, deal_list)
                )

            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

            if additional_data["pagination"]["more_items_in_collection"]:
                url += f'&start={additional_data["pagination"]["next_start"]}'

        return filtered_deals

    @staticmethod
    def retrieve_by(
        company_domain: Optional[str] = None,
        abstra_cloud_org_id: Optional[str] = None,
    ) -> list["Deal"]:
        """
        Retrieve Deals from Pipedrive by Company_domain.

        :param company_domain: str
        :return: list[Deal]
        """

        if abstra_cloud_org_id is None and company_domain is None:
            return []

        if abstra_cloud_org_id is None:
            if company_domain is None or company_domain in GENERIC_DOMAINS:
                return []

        params = {
            "fields": "custom_fields",
        }

        if company_domain is not None:
            params["term"] = company_domain
        elif abstra_cloud_org_id is not None:
            params["term"] = abstra_cloud_org_id

        url = encode_url(entity="deals", action="search", params=params)

        response = requests.get(url)
        response_json = response.json()

        data = response_json["data"].get("items", [])
        additional_data = response_json.get(
            "additional_data", {"pagination": {"more_items_in_collection": False}}
        )

        while additional_data["pagination"]["more_items_in_collection"]:
            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"].get("items", [])
            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

        if data:
            return [
                Deal(
                    id=result["item"]["id"],
                    title=result["item"]["title"],
                    org_id=result["item"]["organization"]["id"]
                    if result["item"]["organization"]
                    else None,
                    person_id=result["item"]["person"]["id"]
                    if result["item"]["person"]
                    else None,
                    owner_id=result["item"]["owner"]["id"]
                    if result["item"]["owner"]
                    else None,
                    stage_id=result["item"]["stage"]["id"],
                    pipeline_id=None,
                    channel="",
                    ads_id="",
                    campaign_id="",
                    ad_name="",
                    tag="",
                    use_case="",
                    company_domain=company_domain,
                    abstra_cloud_org_id=abstra_cloud_org_id,
                    value=result["item"].get("value", ""),
                    status=result["item"].get("status", ""),
                    lost_reason=result["item"].get("lost_reason", ""),
                    add_time=result["item"].get("add_time", ""),
                    qualification_milestone="",
                )
                for result in data
            ]
        else:
            return []

    def update(self, **kwargs) -> "Deal":
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
        :param use_case: str
        :param company_domain: str
        :param abstra_cloud_org_id: str
        :param value: int
        :param qualification_milestone: comma separated string
        :param status: str
        :param lost_reason: str
        :return: Deal"""

        url = encode_url(entity="deals", entity_id=self.id)

        data = {}

        if "title" in kwargs:
            data["title"] = kwargs["title"]
        if "org_id" in kwargs:
            data["org_id"] = kwargs["org_id"]
        if "person_id" in kwargs:
            data["person_id"] = kwargs["person_id"]
        if "stage_id" in kwargs:
            data["stage_id"] = kwargs["stage_id"]
        if "pipeline_id" in kwargs:
            data["pipeline_id"] = kwargs["pipeline_id"]
        if "owner_id" in kwargs:
            data["user_id"] = kwargs["owner_id"]
        if "channel" in kwargs:
            data["channel"] = kwargs["channel"]
        if "ads_id" in kwargs:
            data["67e90727a702feaee708eb4be15c896f1e4d125e"] = kwargs["ads_id"]
        if "campaign_id" in kwargs:
            data["90ee914e411f8e76eda8b270c576fa20ce945af6"] = kwargs["campaign_id"]
        if "ad_name" in kwargs:
            data["cb5af1d8630657fc3ab4bb01c243f993141df2e7"] = kwargs["ad_name"]
        if "tag" in kwargs:
            data["70a34135774fbab2a37608d3d4c5da3be9dfa10a"] = kwargs["tag"]
        if "use_case" in kwargs:
            data["aa6cbdaafd283f46db835b902902f549e86bb915"] = kwargs["use_case"]
        if "company_domain" in kwargs:
            data["34d3f450e4c96e0390b8dd9a7a034e7d64c53db0"] = kwargs["company_domain"]
        if "abstra_cloud_org_id" in kwargs:
            data["68396303430f23178b5bc6978b5b3021cf5eff47"] = kwargs[
                "abstra_cloud_org_id"
            ]
        if "value" in kwargs:
            data["value"] = kwargs["value"]
        if "qualification_milestone" in kwargs:
            data["5abfbfa90d21348b998b9c259392182130d04647"] = kwargs[
                "qualification_milestone"
            ]
        if "status" in kwargs:
            data["status"] = kwargs["status"]
        if "lost_reason" in kwargs:
            data["lost_reason"] = kwargs["lost_reason"]

        try:
            response = requests.put(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error updating deal - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Deal(
                id=response_json["data"]["id"],
                title=response_json["data"]["title"],
                org_id=response_json["data"]["org_id"],
                person_id=response_json["data"]["person_id"],
                stage_id=response_json["data"]["stage_id"],
                pipeline_id=response_json["data"]["pipeline_id"],
                owner_id=response_json["data"]["user_id"]["id"]
                if response_json["data"]["user_id"]
                else None,
                channel=response_json["data"]["channel"],
                ads_id=response_json["data"][
                    "67e90727a702feaee708eb4be15c896f1e4d125e"
                ],
                campaign_id=response_json["data"][
                    "90ee914e411f8e76eda8b270c576fa20ce945af6"
                ],
                ad_name=response_json["data"][
                    "cb5af1d8630657fc3ab4bb01c243f993141df2e7"
                ],
                tag=response_json["data"]["70a34135774fbab2a37608d3d4c5da3be9dfa10a"],
                use_case=response_json["data"][
                    "aa6cbdaafd283f46db835b902902f549e86bb915"
                ],
                company_domain=response_json["data"][
                    "34d3f450e4c96e0390b8dd9a7a034e7d64c53db0"
                ],
                abstra_cloud_org_id=response_json["data"][
                    "68396303430f23178b5bc6978b5b3021cf5eff47"
                ],
                value=response_json["data"]["value"],
                status=response_json["data"]["status"],
                lost_reason=response_json["data"]["lost_reason"],
                add_time=response_json["data"]["add_time"],
                qualification_milestone=response_json["data"][
                    "5abfbfa90d21348b998b9c259392182130d04647"
                ],
            )

    def move_in_pipeline(self) -> "Deal":
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

    def add_participant(self, participant_id: int) -> None:
        """Add a participant to a deal in Pipedrive."""

        url = encode_url(entity="deals", entity_id=self.id, subpath="participants")
        data = {"person_id": participant_id}

        try:
            response = requests.post(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error adding participant to deal - {e}")
            return None


class Activity:
    @dataclass
    class Type:
        meeting = "meeting"
        no_show = "no_show"
        follow_up = "task"
        proposal_sent = "deadline"
        contract_sent = "contract_sent"
        email = "email"
        call = "call"
        start_trial = "start_trial"
        start_a_poc = "lunch"
        signup = "sign_up"
        contact_sent = "contact_sent"
        task = "task1"
        petit_comite = "petit_comite"
        trial_ended = "trial_ended"

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

        self.id = kwargs.get("id", None)
        self.deal_id = kwargs.get("deal_id", None)
        self.subject = kwargs.get("subject", None)
        self.type = kwargs.get("type", None)
        self.due_date = kwargs.get("due_date", None)
        self.due_time = kwargs.get("due_time", None)
        self.duration = kwargs.get("duration", None)
        self.org_id = kwargs.get("org_id", None)
        self.person_id = kwargs.get("person_id", None)
        self.note = kwargs.get("note", None)
        self.done = kwargs.get("done", False)

        if "participants_ids" in kwargs:
            self.participants_ids = (
                kwargs["participants_ids"]
                if kwargs["participants_ids"] is not None
                else []
            )
        elif self.person_id is not None:
            self.participants_ids = [self.person_id]
        else:
            self.participants_ids = []

    @staticmethod
    def create(**kwargs) -> "Activity":
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

        if "deal_id" not in kwargs or "subject" not in kwargs:
            print("deal_id and subject are required")
            return None

        url = encode_url(entity="activities")

        data = {
            "deal_id": kwargs["deal_id"],
            "subject": kwargs["subject"],
            "type": kwargs.get("type", "Meeting"),
            "note": kwargs.get("note", None),
            "due_date": kwargs.get("due_date", None),
            "due_time": kwargs.get("due_time", None),
            "duration": kwargs.get("duration", None),
            "done": kwargs.get("done", False),
        }

        if "participants_ids" in kwargs:
            data["participants"] = [
                {"person_id": id, "primary_flag": False}
                for id in kwargs["participants_ids"]
            ]
            data["participants"][0]["primary_flag"] = True

        try:
            response = requests.post(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error creating task - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Activity(
                id=response_json["data"]["id"],
                deal_id=response_json["data"]["deal_id"],
                subject=response_json["data"]["subject"],
                type=response_json["data"]["type"],
                due_date=response_json["data"]["due_date"],
                due_time=response_json["data"]["due_time"],
                duration=response_json["data"]["duration"],
                org_id=response_json["data"]["org_id"],
                person_id=response_json["data"]["person_id"],
                participants_ids=[
                    r["person_id"] for r in response_json["data"]["participants"]
                ]
                if response_json["data"]["participants"] is not None
                else None,
                note=response_json["data"]["note"],
                done=response_json["data"]["done"],
            )

    @staticmethod
    def get_all_activities() -> list["Activity"]:
        url = encode_url(entity="activities", params={"limit": 500})

        response = requests.get(url)
        response_json = response.json()

        data = response_json["data"]
        additional_data = response_json.get(
            "additional_data", {"pagination": {"more_items_in_collection": False}}
        )

        while additional_data["pagination"]["more_items_in_collection"]:
            new_url = url + f'&start={additional_data["pagination"]["next_start"]}'
            response = requests.get(new_url)
            response_json = response.json()

            data += response_json["data"]
            additional_data = response_json.get(
                "additional_data", {"pagination": {"more_items_in_collection": False}}
            )

        if data:
            return [
                Activity(
                    id=result["id"],
                    deal_id=result["deal_id"],
                    subject=result["subject"],
                    type=result["type"],
                    due_date=result["due_date"],
                    due_time=result["due_time"],
                    duration=result["duration"],
                    org_id=result["org_id"],
                    person_id=result["person_id"],
                    participants_ids=[r["person_id"] for r in result["participants"]]
                    if result["participants"] is not None
                    else None,
                    note=result["note"],
                    done=result["done"],
                )
                for result in data
            ]
        else:
            return []

    def update(self, **kwargs) -> "Activity":
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

        url = encode_url(entity="activities", entity_id=self.id)

        data = {}

        data["deal_id"] = kwargs.get("deal_id", self.deal_id)
        data["subject"] = kwargs.get("subject", self.subject)
        data["type"] = kwargs.get("type", self.type)
        data["due_date"] = kwargs.get("due_date", self.due_date)
        data["due_time"] = kwargs.get("due_time", self.due_time)
        data["duration"] = kwargs.get("duration", self.duration)
        data["done"] = kwargs.get("done", False)

        if "note" in kwargs:
            note = kwargs["note"]
            data["note"] = self.note + " / " + note if self.note is not None else note

        if "participants_ids" in kwargs:
            participants_ids = list(
                set(kwargs["participants_ids"]).union(self.participants_ids)
            )
            data["participants"] = [
                {"person_id": id, "primary_flag": False} for id in participants_ids
            ]
            data["participants"][0]["primary_flag"] = True

        try:
            response = requests.put(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error updating deal - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Activity(
                id=response_json["data"]["id"],
                deal_id=response_json["data"]["deal_id"],
                subject=response_json["data"]["subject"],
                type=response_json["data"]["type"],
                due_date=response_json["data"]["due_date"],
                due_time=response_json["data"]["due_time"],
                duration=response_json["data"]["duration"],
                org_id=response_json["data"]["org_id"],
                person_id=response_json["data"]["person_id"],
                participants_ids=[
                    r["person_id"] for r in response_json["data"]["participants"]
                ]
                if response_json["data"]["participants"] is not None
                else None,
                note=response_json["data"]["note"],
                done=response_json["data"]["done"],
            )

    @staticmethod
    def current_date():
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def current_time():
        return datetime.now(timezone.utc).strftime("%H:%M")


class Notes:
    def __init__(self, **kwargs) -> None:
        """
        :param id: int
        :param deal_id: int
        :param content: str
        """

        self.id = kwargs.get("id", None)
        self.deal_id = kwargs.get("deal_id", None)
        self.content = kwargs.get("content", None)

    @staticmethod
    def create(**kwargs) -> "Notes":
        """
        Create a new note in Pipedrive.

        :param deal_id: int
        :param content: str
        :return: Notes
        """

        if "deal_id" not in kwargs or "content" not in kwargs:
            print("deal_id and content are required")
            return None

        url = encode_url(entity="notes")

        data = {"deal_id": kwargs["deal_id"], "content": kwargs["content"]}

        try:
            response = requests.post(
                url, data=json.dumps(data), headers={"Content-Type": CONTENT_TYPE}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Error creating note - {e}")
            return None

        response_json = response.json()

        if response_json["success"]:
            return Notes(
                id=response_json["data"]["id"],
                deal_id=response_json["data"]["deal_id"],
                content=response_json["data"]["content"],
            )
