import json


def convert_json(data):
    data = json.loads(data) if isinstance(data, str) else data
    result = []
    for key, value in data.items():
        if isinstance(value, str):
            result.append({"path": key, "value": value})
        else:
            temp = convert_json(value)
            for elem in temp:
                result.append({"path": key + "." + elem['path'], "value": elem['value']})
    return result


input = input("Write JSON:")
print("RESULT IS ", convert_json(input))


