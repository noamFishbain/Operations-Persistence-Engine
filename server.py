from math import factorial
from flask import Flask, request, jsonify
# Import our new DB manager
from db_manager import DBManager

app = Flask(__name__)
# Initialize DB connection
db = DBManager()

# Stack remains in memory as per instructions (only operations are persisted)
stack = []


@app.route('/calculator/health', methods=['GET'])
def health_check():
    return "OK", 200


@app.route('/calculator/independent/calculate', methods=['POST'])
def independent_calculate():
    data = request.get_json()
    args = data.get('arguments', [])
    operation = data.get('operation', '').lower()

    operations = {
        'plus': lambda x, y: x + y,
        'minus': lambda x, y: x - y,
        'times': lambda x, y: x * y,
        'divide': lambda x, y: x // y if y != 0 else None,
        'pow': lambda x, y: x ** y,
        'abs': lambda x: abs(x),
        'fact': lambda x: factorial(x),
    }

    if operation not in operations:
        return jsonify({"errorMessage": f"Error: unknown operation: {operation}"}), 409

    try:
        func = operations[operation]
        if operation in ['abs', 'fact']:
            if len(args) != 1:
                return jsonify(
                    {"errorMessage": f"Error: Not enough arguments to perform the operation {operation}"}), 409
            result = func(args[0])
            if result is None:
                return jsonify({
                                   "errorMessage": "Error while performing operation Factorial: not supported for the negative number"}), 409
        else:
            if len(args) < 2:
                return jsonify(
                    {"errorMessage": f"Error: Not enough arguments to perform the operation {operation}"}), 409
            if len(args) > 2:
                return jsonify({"errorMessage": f"Error: Too many arguments to perform the operation {operation}"}), 409
            if operation == 'divide' and args[1] == 0:
                return jsonify({"errorMessage": "Error while performing operation Divide: division by 0"}), 409
            result = func(args[0], args[1])

        # Save to DB instead of local list
        db.save_operation("INDEPENDENT", operation, result, args)

        return jsonify({"result": result}), 200
    except Exception as e:
        return jsonify({"errorMessage": f"Internal error: {str(e)}"}), 500


@app.route('/calculator/stack/size', methods=['GET'])
def stack_size():
    return jsonify({"result": len(stack)}), 200


@app.route('/calculator/stack/arguments', methods=['PUT'])
def stack_add():
    data = request.get_json()
    args = data.get('arguments', [])

    for arg in args:
        stack.append(arg)

    return jsonify({"result": len(stack)}), 200


@app.route('/calculator/stack/operate', methods=['GET'])
def stack_operate():
    operation = request.args.get('operation', '').lower()

    operations = {
        'plus': lambda x, y: x + y,
        'minus': lambda x, y: x - y,
        'times': lambda x, y: x * y,
        'divide': lambda x, y: x // y if y != 0 else None,
        'pow': lambda x, y: x ** y,
        'abs': lambda x: abs(x),
        'fact': lambda x: factorial(x)
    }

    if operation not in operations:
        return jsonify({"errorMessage": f"Error: unknown operation: {operation}"}), 409

    func = operations[operation]

    try:
        if operation in ['abs', 'fact']:
            if len(stack) < 1:
                return jsonify({
                                   "errorMessage": f"Error: cannot implement operation {operation}. It requires 1 arguments and the stack has only {len(stack)} arguments"}), 409
            arg = stack.pop()
            result = func(arg)
            if result is None:
                return jsonify({
                                   "errorMessage": "Error while performing operation Factorial: not supported for the negative number"}), 409

            # Save to DB
            db.save_operation("STACK", operation, result, [arg])
        else:
            if len(stack) < 2:
                return jsonify({
                                   "errorMessage": f"Error: cannot implement operation {operation}. It requires 2 arguments and the stack has only {len(stack)} arguments"}), 409
            x = stack.pop()
            y = stack.pop()
            if operation == 'divide' and y == 0:
                stack.extend([y, x])
                return jsonify({"errorMessage": "Error while performing operation Divide: division by 0"}), 409
            result = func(x, y)

            # Save to DB
            db.save_operation("STACK", operation, result, [x, y])

        return jsonify({"result": result}), 200

    except Exception as e:
        return jsonify({"errorMessage": f"Internal error: {str(e)}"}), 500


@app.route('/calculator/stack/arguments', methods=['DELETE'])
def stack_delete():
    try:
        count = int(request.args.get('count', '0'))
    except ValueError:
        return jsonify({"errorMessage": "Error: count must be an integer"}), 409

    if count > len(stack):
        return jsonify(
            {"errorMessage": f"Error: cannot remove {count} from the stack. It has only {len(stack)} arguments"}), 409

    for _ in range(count):
        stack.pop()

    return jsonify({"result": len(stack)}), 200


@app.route('/calculator/history', methods=['GET'])
def get_history():
    # Retrieve the new query parameter for DB selection [cite: 75]
    persistence_method = request.args.get('persistenceMethod')

    # Retrieve the optional flavor filter
    flavor_filter = request.args.get('flavor', None)

    if persistence_method not in ["POSTGRES", "MONGO"]:
        # While not explicitly asked to handle error, it's good practice or just return empty
        return jsonify({"result": []}), 200

    # Fetch raw history from the selected DB
    raw_history = db.fetch_history(persistence_method)

    # Filter by flavor if requested
    filtered_history = []
    if flavor_filter:
        for item in raw_history:
            if item["flavor"] == flavor_filter:
                filtered_history.append(item)
    else:
        filtered_history = raw_history

    return jsonify({"result": filtered_history}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8496)