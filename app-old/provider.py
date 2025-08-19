import datetime
import json
import math
import os
from collections import defaultdict
from typing import Dict, Set

from flask import Blueprint, Flask

from app import config
from globus_action_provider_tools import (
    ActionProviderDescription,
    ActionRequest,
    ActionStatus,
    ActionStatusValue,
    AuthState,
)
from globus_action_provider_tools.flask import add_action_routes_to_blueprint
from globus_action_provider_tools.flask.helpers import assign_json_provider
from globus_action_provider_tools.flask.types import ActionCallbackReturn

import requests

def _retrieve_action_status(action_id: str) -> ActionStatus:
    simple_status = ActionStatus(
        status=ActionStatusValue.SUCCEEDED,
        creator_id="UNKNOWN",
        start_time=str(datetime.datetime.now().isoformat()),
        completion_time=str(datetime.datetime.now().isoformat()),
        release_after="P30D",
        display_status=ActionStatusValue.SUCCEEDED,
        details={},
    )
    
    return simple_status


def load_schema():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.json")
    ) as f:
        schema = json.load(f)
    return schema

def wrap_in_action_status(request: ActionRequest, auth: AuthState, data: dict) -> ActionCallbackReturn:
    """
    This function is a helper for the action_run functions. It takes the
    computed results and wraps them in an ActionStatus object.
    """
    caller_id = auth.effective_identity
    status = ActionStatus(
        status=ActionStatusValue.SUCCEEDED,
        creator_id=caller_id or "UNKNOWN",
        monitor_by=request.monitor_by,
        manage_by=request.manage_by,
        start_time=str(datetime.datetime.now().isoformat()),
        completion_time=str(datetime.datetime.now().isoformat()),
        release_after=request.release_after or "P30D",
        display_status=ActionStatusValue.SUCCEEDED,
        details=data,
    )
    return status


def machine_status_action_run(request: ActionRequest, auth: AuthState) -> ActionCallbackReturn:
    """
    Asynchronous actions most likely need to implement retry logic here to
    prevent duplicate requests with matching request_ids from launching
    another job. In the event that a request with an existing request_id
    and creator_id arrives, this function should simply return the action's
    status via the action_status function.

    Synchronous actions or actions where it makes sense to execute repeated
    runs with the same parameters need not implement retry logic.
    """
    # Tyler's verison
    s3m_data = get_s3m_data()

    # Will's version
    # total_nodes_count = len(gronk_data['nodeinfo'])
    # running_jobs_count = len(gronk_data['running'])
    # active_nodes_count = 0
    # for state_dict in gronk_data['nodeinfo'].values():
    #    if not "offline" in state_dict['state']:
    #         active_nodes_count += 1
    # is_active = running_jobs_count > 0 or active_nodes_count > 0

    # payload = {
    #     "is_active": is_active,
    #     "total_nodes_count": total_nodes_count,
    #     "active_nodes_count": active_nodes_count,
    #     "running_jobs_count": running_jobs_count,
    # }

    # return wrap_in_action_status(request, auth, payload)
    return wrap_in_action_status(request, auth, s3m_data)

def queues_action_run(request: ActionRequest, auth: AuthState) -> ActionCallbackReturn:
    # TYLER: currently identical to other route since s3m only has one /status. 
    s3m_data = get_s3m_data()

    """
    queue_to_stats = defaultdict(lambda: {"node_minutes": 0, "job_count": 0})

    # in epoch seconds
    updated_time = gronk_data['updated']
    
    for job_dict in gronk_data['running']:
        try:
            run_time_in_secs = updated_time - int(job_dict['starttime'])
            run_time_in_mins = run_time_in_secs // 60
            time_left_in_mins = job_dict['walltime'] - run_time_in_mins
            queue_name = job_dict['queue']
            queue_to_stats[queue_name]['node_minutes'] += time_left_in_mins
            queue_to_stats[queue_name]['job_count'] += 1
        except:
            pass
    
    for job_dict in gronk_data['queued']:
        queue_name = job_dict['queue']
        wall_time = job_dict['walltime']
        queue_to_stats[queue_name]['node_minutes'] += wall_time
        queue_to_stats[queue_name]['job_count'] += 1

    queue_objects = [
        {
            "queue": queue_name,
            "node_hours": math.ceil(stats["node_minutes"] / 60),
            "job_count": stats["job_count"],
        } for queue_name, stats in queue_to_stats.items()
    ]

    payload = {
        "queues": queue_objects,
    }
    """

    return wrap_in_action_status(request, auth, s3m_data)


def projects_action_run(request: ActionRequest, auth: AuthState) -> ActionCallbackReturn:
    # TYLER: currently identical to other routes because s3m only has one /status
    s3m_data = get_s3m_data()
    """
    project_name_to_counts = defaultdict(lambda: {"running_count": 0, "queued_count": 0})
    for job_dict in gronk_data['queued']:
        project_name = job_dict['project']
        project_name_to_counts[project_name]['queued_count'] += 1

    for job_dict in gronk_data['running']:
        project_name = job_dict['project']
        project_name_to_counts[project_name]['running_count'] += 1

    formatted_project_list = [
        {
            "project_name": project_name,
            "running_count": counts["running_count"],
            "queued_count": counts["queued_count"]
        } for project_name, counts in project_name_to_counts.items()
    ]

    payload = {
        "projects": formatted_project_list,
    }
    """

    return wrap_in_action_status(request, auth, s3m_data)

# Generic stub functions for all the actions

def action_enumerate(auth: AuthState, params: Dict[str, Set]):
    return []

def action_status(action_id: str, auth: AuthState) -> ActionCallbackReturn:
    status = _retrieve_action_status(action_id)
    return status, 200

def action_cancel(action_id: str, auth: AuthState) -> ActionCallbackReturn:
    status = _retrieve_action_status(action_id)
    return status

def action_release(action_id: str, auth: AuthState) -> ActionCallbackReturn:
    return ActionStatusValue.SUCCEEDED, 200

# Will's version
# def get_gronkulator_data():
#    return requests.get("https://status.alcf.anl.gov/polaris/activity.json").json()

# Tyler's version
def get_s3m_status_data():
    return requests.get("https://s3m.apps.olivine.ccs.ornl.gov/olcf/v1alpha/status", timeout=5).json() 

def create_app():
    app = Flask(__name__)
    assign_json_provider(app)
    app.url_map.strict_slashes = False

    # Create and define a blueprint onto which the routes will be added
    status_blueprint = Blueprint("machine-status", __name__, url_prefix="/machine-status")
    queues_blueprint = Blueprint("queues", __name__, url_prefix="/queues")
    projects_blueprint = Blueprint("projects", __name__, url_prefix="/projects")


    # Create the ActionProviderDescription with the correct scope and schema
    provider_description = ActionProviderDescription(
        globus_auth_scope=config.our_scope,
        title="alcf_resource_status",
        admin_contact="willengler@uchicago.edu",
        synchronous=True,
        input_schema=load_schema(),
        log_supported=False,  # This provider doesn't implement the log callback
        visible_to=["public"],
    )

    def add_handler_to_blueprint(blueprint, handler):
        add_action_routes_to_blueprint(
            blueprint=blueprint,
            client_id=config.client_id,
            client_secret=config.client_secret,
            client_name=None,
            provider_description=provider_description,
            action_run_callback=handler,
            action_status_callback=action_status,
            action_cancel_callback=action_cancel,
            action_release_callback=action_release,
            action_enumeration_callback=action_enumerate,
            additional_scopes=[
                "https://auth.globus.org/scopes/d3a66776-759f-4316-ba55-21725fe37323/secondary_scope"
            ],
        )

    for (blueprint, handler) in zip(
        [status_blueprint, queues_blueprint, projects_blueprint],
        [machine_status_action_run, queues_action_run, projects_action_run]
    ):
        add_handler_to_blueprint(blueprint, handler)
        app.register_blueprint(blueprint)

    return app


def make_app():
    app = create_app()
    return app


if __name__ == "__main__":
    app = make_app()
    app.run(debug=True)
