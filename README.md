# Pipedrive ORM Documentation

This ORM facilitates interaction with Pipedrive's API, specifically for managing CRM. The following documentation outlines the attributes and methods available in the `Organization`, `Person`, `Deal` ans `Activity` classes.

## Entities

### Organization

#### Attributes:
- `id` (int)
- `name` (str)
- `owner_id` (int):  The ID of the owner associated with the organization.

#### Methods:

1. **retrieve_by(name: str) -> List[Organization]**

   **Description**: Search organizations in Pipedrive.

   **Inputs**:
   - `name` (str): The name of the organization to search for.

2. **create(kwargs) -> Organization**

   **Description**: Creates a new organization in Pipedrive.

   **Inputs**:
   - `name` (str): The name of the organization. `required`
   - `owner_id` (int): The ID of the owner for the organization.

---
### Person

#### Attributes:
- `id` (int)
- `name` (str)
- `email` (str)
- `organization_id` (int)
- `owner_id` (int)
- `phone` (str)
- `job_title` (str)
- `linkedin` (str)

#### Methods:

1. **retrieve_by(email: str) -> List[Person]**

   **Description**: Retrieves person from Pipedrive based on the email address provided.

   **Inputs**:
   - `email` (str): The email of the person to search for.
 

2. **create(kwargs) -> Person**

   **Description**: Creates a new person in Pipedrive using the provided attributes.

   **Inputs**:
   - `name` (str): The name of the person. `required`
   - `org_id` (int): The ID of the associated organization.
   - `email` (str): The email of the person.
   - `phone` (str): The phone number of the person.
   - `owner_id` (int): The ID of the owner.
   - `job_title` (str): The job title of the person.
   - `linkedin` (str): The LinkedIn profile URL.

---
### Deal

#### Nested Enums:

**Description**: Pipedrive uses numeric ids to describe pipelines, stages, owners and meeting channels. These classes store the respective ids of those attributes

1. **Pipeline**:
   Represents different types of pipelines in the system, such as sales, trial, customer success (CS), and marketing.

2. **Stage**:
   Defines the various stages within each pipeline, such as lead qualification, negotiation, and deal closure, for marketing, sales, and trial pipelines.

3. **Owner**:
   Lists the deal owners, each represented by a specific person responsible for managing the deal.

4. **Channel**:
   Represents the different channels through which deals are sourced, including organic and paid channels, such as events, personal networks, and ads platforms.

#### Attributes:
- `id` (int)
- `title` (str)
- `org_id` (int)
- `person_id` (int)
- `ads_id` (str)
- `campaign_id` (str)
- `ad_name` (str)
- `stage_id` (int)
- `pipeline_id` (int)
- `owner_id` (int)
- `channel` (str)  
#### Methods

1. **is_meeting_scheduled_or_after (property)**

    **Description**: `Meeting Scheduled` is a stage in the pipeline. This property differentiates between deals that had meetings and deals that didn't.

    **Returns**:  
    - `True` if the deal has a meeting scheduled or is in a later stage.
    - `False` if the deal is in an earlier stage.


2. **create(kwargs) -> Deal**

    **Description**: Creates a new deal in Pipedrive.

    **Inputs**:
    - `title` (str) `required`
    - `org_id` (int)
    - `person_id` (int)
    - `stage_id` (int)
    - `pipeline_id` (int)
    - `owner_id` (int)
    - `channel` (str)
    - `ads_id` (str)
    - `campaign_id` (str)
    - `ad_name` (str)

    **Returns**:  
    - A new `Deal` object if successful.
    - `None` if required parameters are missing or there’s an error.

3. **get_all_deals() -> List[Deal]**

    **Description**: Retrieves all deals from Pipedrive.

    **Returns**:  
    - A list of `Deal` objects retrieved from Pipedrive.
    - An empty list if no deals are found.

4. **update(self, kwargs) -> Deal**

    **Description**: Updates an existing deal in Pipedrive.

    **Parameters**:
    - `title` (str)
    - `org_id` (int)
    - `person_id` (int)
    - `stage_id` (int)
    - `pipeline_id` (int)
    - `owner_id` (int)
    - `channel` (str)
    - `ads_id` (str)
    - `campaign_id` (str)
    - `ad_name` (str)

    **Returns**:  
    - An updated `Deal` object if successful.
    - `None` if there’s an error during the update.

5. **move_in_pipeline(self) -> Deal**

    **Description**: Moves the deal to the next stage in the pipeline, depending on the current progress.

    **Returns**:  
    - An updated `Deal` object if the deal is moved to the next stage.
    - The current `Deal` object if it’s already in a stage where a meeting is scheduled or later.

---
### Activity

#### Attributes:

- `id` (int)
- `deal_id` (int)
- `subject` (str): The subject or title of the activity.
- `type` (str)
- `due_date` (str): The date the activity is due (format: YYYY-MM-DD).
- `due_time` (str): The time the activity is due (format: HH:MM).
- `duration` (str):  The duration of the activity minutes (format: MM).
- `org_id` (int)
- `person_id` (int)
- `note` (str)
- `done` (bool)
- `participants_ids` (list[int])

#### Methods

1. **create(kwargs) -> Activity**

    **Description**: Creates a new activity in Pipedrive.

    **Parameters**:
    - `deal_id` (int): `Required`
    - `subject` (str): `Required`
    - `type` (str)
    - `note` (str)
    - `due_date` (str): The due date of the activity (format: YYYY-MM-DD).
    - `due_time` (str): The due time of the activity (format: HH:MM).
    - `duration` (str): The duration in minutes (format MM).
    - `participants_ids` (list[int])
    - `done` (bool)

    **Returns**:  
    - A new `Activity` object if successful.
    - `None` if required parameters (`deal_id` and `subject`) are missing or there’s an error.

2. **get_all_activities() -> List[Activity]**

    **Description**: Retrieves all activities from Pipedrive.

    **Returns**:  
    - A list of `Activity` objects retrieved from Pipedrive.
    - An empty list if no activities are found.

3. **update(self, kwargs) -> Activity**

    **Description**: Updates an existing activity in Pipedrive.

    **Parameters**:
    - `deal_id` (int)
    - `subject` (str)
    - `type` (str)
    - `note` (str)
    - `due_date` (str): The due date of the activity (format: YYYY-MM-DD).
    - `due_time` (str): The due time of the activity (format: HH:MM).
    - `duration` (str): The duration in minutes (format MM).
    - `participants_ids` (list[int])
    - `done` (bool)

    **Returns**:  
    - An updated `Activity` object if successful.
    - `None` if there’s an error during the update.
