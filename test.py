import json
# тест терминатор

def make_draft(data: dict) -> dict:
    draft = {}
    # TODO: Make draft here
    return draft


def make_turn(data: dict) -> dict:
    battle_output = {
        'Message': f"I have {len(data['My'])} ships and move to center of galaxy and shoot",
        'UserCommands': []
    }
    for ship in data['My']:
        battle_output['UserCommands'].append({
            "Command": "MOVE",
            "Parameters": {
                'Id': ship['Id'],
                'Target': '15/15/15'
            }
        })
        guns = [x for x in ship['Equipment'] if x['Type'] == 1]
        if guns:
            gun = guns[0]
            battle_output['UserCommands'].append({
                "Command": "ATTACK",
                "Parameters": {
                    'Id': ship['Id'],
                    'Name': gun['Name'],
                    'Target': '15/15/15'
                }
            })
    return battle_output


def play_game():
    while True:
        raw_line = input()
        line = json.loads(raw_line)
        if 'PlayerId' in line:
            print(json.dumps(make_draft(line), ensure_ascii=False))
        elif 'My' in line:
            print(json.dumps(make_turn(line), ensure_ascii=False))


if __name__ == '__main__':
    play_game()
