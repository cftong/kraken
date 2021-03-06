"""
Endpoints for management of arkOS security policies.

arkOS Kraken
(c) 2016 CitizenWeb
Written by Jacob Cook
Licensed under GPLv3, see LICENSE.md
"""

from flask import Blueprint, abort, jsonify, request
from flask.views import MethodView

from kraken import auth
from arkos import security, tracked_services

backend = Blueprint("security", __name__)


class PolicyAPI(MethodView):
    @auth.required()
    def get(self, id):
        svcs = tracked_services.get(id)
        if id and not svcs:
            abort(404)
        if isinstance(svcs, tracked_services.SecurityPolicy):
            return jsonify(policy=svcs.serialized)
        else:
            return jsonify(policies=[x.serialized for x in svcs])

    @auth.required()
    def post(self):
        data = request.get_json()["policy"]
        pol = tracked_services.SecurityPolicy(
            "custom", data["id"], data["name"], "shield", data["ports"],
            data["policy"]
        )
        pol.save()
        return jsonify(policy=pol.serialized)

    @auth.required()
    def put(self, id):
        data = request.get_json()["policy"]
        policy = tracked_services.get(id)
        if not id or not policy:
            abort(404)
        policy.policy = data["policy"]
        policy.save()
        return jsonify(policy=policy.serialized)

    @auth.required()
    def delete(self, id):
        policy = tracked_services.get(id)
        if not id or not policy or policy.type != "custom":
            abort(404)
        policy.remove()
        return jsonify(), 204


class DefenceAPI(MethodView):
    @auth.required()
    def get(self, id):
        return jsonify(jails=security.get_defense_rules())

    @auth.required()
    def put(self, id):
        data = request.get_json()["jail"]
        if data["operation"] == "enable":
            security.enable_all_def(data["name"])
        else:
            security.disable_all_def(data["name"])


policy_view = PolicyAPI.as_view('policy_api')
backend.add_url_rule('/api/system/policies', defaults={'id': None},
    view_func=policy_view, methods=['GET',])
backend.add_url_rule('/api/system/policies', view_func=policy_view,
                     methods=['POST', ])
backend.add_url_rule('/api/system/policies/<string:id>', view_func=policy_view, methods=['GET', 'PUT', 'DELETE'])

defence_view = DefenceAPI.as_view('defence_api')
backend.add_url_rule('/api/system/jails', defaults={'id': None},
    view_func=defence_view, methods=['GET',])
backend.add_url_rule('/api/system/jails/<string:id>', view_func=defence_view, methods=['GET', 'PUT'])
