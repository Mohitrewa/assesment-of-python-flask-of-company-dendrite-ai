from flask import Flask, request, jsonify, render_template
from ariadne import QueryType, MutationType, make_executable_schema, graphql_sync
from ariadne.explorer import ExplorerApollo
import keycloak

def keycloack():
    key = keycloak.Client().payload_for_client()
    username = "graphql"
    password = "0000"
    client_id = "To-Do-List"
    Host = "http://localhost/5000"
    verify = True

app = Flask(__name__)

# In-memory storage for to-do items
todo_items = []
next_id = 1

type_defs = """
    type Query {
        todos: [TodoItem]
    }

    type TodoItem {
        id: ID!
        task: String!
        done: Boolean!
    }

    type Mutation {
        addTodoItem(task: String!): TodoItem
        markDone(id: ID!): TodoItem
    }
"""

query = QueryType()
mutation = MutationType()

@query.field("todos")
def resolve_todos(*_):
    return todo_items

@mutation.field("addTodoItem")
def resolve_add_todo_item(_, info, task):
    global next_id
    new_todo = {"id": next_id, "task": task, "done": False}
    todo_items.append(new_todo)
    next_id += 1
    return new_todo

@mutation.field("markDone")
def resolve_mark_done(_, info, id):
    for todo in todo_items:
        if todo["id"] == int(id):
            todo["done"] = True
            return todo
    return None

schema = make_executable_schema(type_defs, query, mutation)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", todos=todo_items)

@app.route("/graphql", methods=["GET"])
def graphql_playground():
    explorer_html = ExplorerApollo().html()
    return explorer_html, 200

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    app.run(debug=True)
