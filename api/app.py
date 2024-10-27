from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from datetime import datetime

app = Flask(__name__)
api = Api(app)

# Roboter und Items initialisieren
# Der Roboter und die Items werden in einem Dictionaries gespeichert.
# Hier wird eine Funktion zum setzen des initialen Zustands definiert,
# um das Testen zu erleichtern.
def get_initial_state():
    return {
        "robots": {
            1: {
                "id": 1,
                "position": {"x": 0, "y": 0},
                "energy": 100,
                "inventory": {},
                "actions": []
            },
            2: {
                "id": 2,
                "position": {"x": 1, "y": 1},
                "energy": 100,
                "inventory": {},
                "actions": []
            }
        },
        "items": {
            1: {
                "id": 1,
                "position": {"x": 0, "y": 0},
            }
        }
    }


def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Attach initial state to the app instance
    initial_state = get_initial_state()
    app.robots = initial_state["robots"]
    app.items = initial_state["items"]
    
    # Roboter-Status abrufen
    class RobotStatus(Resource):
        def get(self, robot_id):
            robot = app.robots.get(robot_id)
            if robot:
                app.robots[robot_id] = robot
                response = jsonify(
                    {
                        "id": robot["id"],
                        "position": robot["position"],
                        "energy": robot["energy"],
                        "inventory": robot["inventory"],
                        "links": [
                            {"rel": "self", "href": f"/robots/{robot_id}/status"},
                            {"rel": "actions", "href": f"/robots/{robot_id}/actions?page=1&size=5"}
                        ]
                    }
                )
                return response
            return {"message": "Robot not found"}, 404

    # Roboter bewegen
    class RobotMove(Resource):
        def post(self, robot_id):
            data = request.get_json()
            direction = data.get("direction")
            robot = app.robots.get(robot_id)
            
            if not robot:
                return {"message": "Robot not found"}, 404

            # Bewegung des Roboters basierend auf der Richtung
            if direction == "up":
                robot["position"]["y"] += 1
            elif direction == "down":
                robot["position"]["y"] -= 1
            elif direction == "left":
                robot["position"]["x"] -= 1
            elif direction == "right":
                robot["position"]["x"] += 1
            else:
                return {"message": "Invalid direction"}, 400

            current_actions_idx = len(robot["actions"])
            robot["actions"].append(
                    {
                    "action": "move",
                    "direction": direction,
                    "timestamp": datetime.now().isoformat(),
                    "links": [
                        {"rel": "self", "href": f"/robots/{robot_id}/actions/{current_actions_idx}"},
                        ]
                    }
                )
            
            # Updating the robot in the robots dictionary
            app.robots[robot_id] = robot
            
            response = jsonify(
                {
                    "id": robot["id"],
                    "position": robot["position"],
                    "energy": robot["energy"],
                    "inventory": robot["inventory"],
                    "links": [
                        {"rel": "self", "href": f"/robots/{robot_id}/status"},
                        {"rel": "actions", "href": f"/robots/{robot_id}/actions?page=1&size=5"}
                    ]
                }
            )
            return response

    # Roboter-Zustand aktualisieren
    class RobotState(Resource):
        def patch(self, robot_id):
            data = request.get_json()
            robot = app.robots.get(robot_id)
            
            if not robot:
                return {"message": "Robot not found"}, 404

            # Aktualisieren des Energielevels und/oder Position
            if "energy" in data:
                robot["energy"] = data["energy"]
            if "position" in data:
                robot["position"] = data["position"]

            current_actions_idx = len(robot["actions"])
            robot["actions"].append({
                "action": "update_state",
                "data": data, "timestamp": datetime.now().isoformat(),
                "links": [
                        {"rel": "self", "href": f"/robots/{robot_id}/actions/{current_actions_idx}"},
                        ]
                })
            app.robots[robot_id] = robot
            response = jsonify(
                    {
                        "id": robot["id"],
                        "position": robot["position"],
                        "energy": robot["energy"],
                        "inventory": robot["inventory"],
                        "links": [
                            {"rel": "self", "href": f"/robots/{robot_id}/status"},
                            {"rel": "actions", "href": f"/robots/{robot_id}/actions?page=1&size=5"}
                        ]
                    }
                )
            return response
        
    # Roboter-Item aufheben
    class RobotPickup(Resource):
        def post(self, robot_id, item_id):
            item = app.items.get(item_id)
            robot = app.robots.get(robot_id)
            
            if not robot:
                return {"message": "Robot not found"}, 404
            if not item:
                return {"message": "Item not found"}, 404

            robot_pos = robot["position"]
            item_pos = item["position"]
            current_actions_idx = len(robot["actions"])
            if abs(robot_pos["x"] - item_pos["x"]) == 0 and abs(robot_pos["y"] - item_pos["y"]) == 0:
                robot["inventory"][item_id] = item
                app.items.pop(item_id)
                robot["actions"].append({
                    "action": "pickup",
                    "item": item, "timestamp": datetime.now().isoformat(),
                    "links": [
                        {"rel": "self", "href": f"/robots/{robot_id}/actions/{current_actions_idx}"},
                        ]
                    })
                app.robots[robot_id] = robot
                response = jsonify(
                    {
                        "id": robot["id"],
                        "position": robot["position"],
                        "energy": robot["energy"],
                        "inventory": robot["inventory"],
                        "links": [
                            {"rel": "self", "href": f"/robots/{robot_id}/status"},
                            {"rel": "actions", "href": f"/robots/{robot_id}/actions?page=1&size=5"}
                        ]
                    }
                )
                return response  
            else:    
                return {"message": "Item not in range"}, 400
        
    class RobotPutDown(Resource):
        def post(self, robot_id, item_id):
            robot = app.robots.get(robot_id)
            item = robot['inventory'].get(item_id)        
            if not robot:
                return {"message": "Robot not found"}, 404
            if not item:
                return {"message": "Item not found"}, 404

            if item_id in robot["inventory"]:
                robot["inventory"].pop(item_id)
                item['position'] = robot['position'].copy()
                app.items[item_id] = item
                current_actions_idx = len(robot["actions"])
                robot["actions"].append({
                    "action": "drop",
                    "item": item,
                    "timestamp": datetime.now().isoformat(),
                    "links": [
                        {"rel": "self", "href": f"/robots/{robot_id}/actions/{current_actions_idx}"},
                        ]
                    })
                app.robots[robot_id] = robot
                response = jsonify(
                    {
                        "id": robot["id"],
                        "position": robot["position"],
                        "energy": robot["energy"],
                        "inventory": robot["inventory"],
                        "links": [
                            {"rel": "self", "href": f"/robots/{robot_id}/status"},
                            {"rel": "actions", "href": f"/robots/{robot_id}/actions?page=1&size=5"}
                        ]
                    }
                )
                return response        
            return {"message": "Item not in range"}, 400
        
    class RobotGetActions(Resource):
        def get(self, robot_id, action_id=None):
            robot = app.robots.get(robot_id)
            if not robot:
                return {"message": "Robot not found"}, 404

            # If action_id is provided, return only that action
            if action_id is not None:
                if action_id < 0 or action_id >= len(robot["actions"]):
                    return {"message": "Action not found"}, 404
                action = robot["actions"][action_id]
                # Add HATEOAS link to the specific action
                action_with_link = {
                    "action": action,
                    "links": [
                        {"rel": "self", "href": f"/robots/{robot_id}/actions/{action_id}"}
                    ]
                }
                return jsonify(action_with_link)

            # Handle pagination if no specific action_id is requested
            page = int(request.args.get('page', 1))
            size = int(request.args.get('size', 5))
            actions = robot["actions"]

            start = (page - 1) * size
            end = start + size
            paginated_actions = actions[start:end]

            # Calculate total number of pages
            total_elements = len(actions)
            total_pages = (total_elements + size - 1) // size
            has_next = page < total_pages
            has_previous = page > 1

            # Add pagination links
            links = [
                {"rel": "self", "href": f"/robots/{robot_id}/actions?page={page}&size={size}"},
                {"rel": "next", "href": f"/robots/{robot_id}/actions?page={page+1}&size={size}"} if has_next else None,
                {"rel": "prev", "href": f"/robots/{robot_id}/actions?page={page-1}&size={size}"} if has_previous else None
            ]
            links = [link for link in links if link]  # Remove None values

            # Format response with pagination and links
            response = {
                "page": {
                    "number": page,
                    "size": size,
                    "totalElements": total_elements,
                    "totalPages": total_pages,
                    "hasNext": has_next,
                    "hasPrevious": has_previous
                },
                "actions": paginated_actions,
                "links": links
            }

            return jsonify(response)
        
    class RobotAttack(Resource):
        def post(self, robot_id, target_id):
            robot = app.robots.get(robot_id)
            target = app.robots.get(target_id)
            if not robot:
                return {"message": "Robot not found"}, 404
            if not target:
                return {"message": "Target not found"}, 404
            if robot["energy"] < 5:
                return {"message": "Not enough energy"}, 400
            elif abs(robot["position"]["x"] - target["position"]["x"]) <= 1 and abs(robot["position"]["y"] - target["position"]["y"]) <= 1:
                robot["energy"] -= 5
                current_actions_idx = len(robot["actions"])
                robot["actions"].append({
                    "action": "attack",
                    "target": target_id,
                    "timestamp": datetime.now().isoformat(),
                    "links": [
                            {"rel": "self", "href": f"/robots/{robot_id}/actions/{current_actions_idx}"},
                            ]
                    })
                app.robots[robot_id] = robot
                response = jsonify(
                    {
                        "id": robot["id"],
                        "position": robot["position"],
                        "energy": robot["energy"],
                        "inventory": robot["inventory"],
                        "links": [
                            {"rel": "self", "href": f"/robots/{robot_id}/status"},
                            {"rel": "actions", "href": f"/robots/{robot_id}/actions?page=1&size=5"}
                        ]
                    }
                )
                return response

    # Endpunkte registrieren
    api.add_resource(RobotStatus, '/robots/<int:robot_id>/status')
    api.add_resource(RobotMove, '/robots/<int:robot_id>/move')
    api.add_resource(RobotState, '/robots/<int:robot_id>/state')
    api.add_resource(RobotPickup, '/robots/<int:robot_id>/pickup/<int:item_id>')
    api.add_resource(RobotPutDown, '/robots/<int:robot_id>/putdown/<int:item_id>')
    api.add_resource(RobotGetActions, '/robots/<int:robot_id>/actions', '/robots/<int:robot_id>/actions/<int:action_id>')
    api.add_resource(RobotAttack, '/robots/<int:robot_id>/attack/<int:target_id>')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
