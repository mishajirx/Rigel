import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


# classes

class JSONCapability:
    def to_json(self):
        return {k: v if not isinstance(v, Vector) else str(v) for k, v in self.__dict__.items() if v is not None}


# region primitives
@dataclass
class Vector:
    X: int
    Y: int
    Z: int

    @classmethod
    def from_json(cls, data):
        x, y, z = map(int, data.split('/'))
        return cls(x, y, z)

    def __add__(self, other):
        return Vector(self.X + other.X, self.Y + other.Y, self.Z + other.Z)

    def __sub__(self, other):
        return Vector(self.X - other.X, self.Y - other.Y, self.Z - other.Z)

    def __reversed__(self):
        return Vector(self.X * -1, self.Y * -1, self.Z * -1)

    def __abs__(self):
        return max([abs(self.X), abs(self.Y), abs(self.Z)])

    def __str__(self):
        return f"{self.X}/{self.Y}/{self.Z}"


# endregion

# region equipment

class EquipmentType(Enum):
    Energy = 0
    Gun = 1
    Engine = 2
    Health = 3


class EffectType(Enum):
    Blaster = 0


@dataclass
class EquipmentBlock(JSONCapability):
    Name: str
    Type: EquipmentType

    @classmethod
    def from_json(cls, data):
        if EquipmentType(data['Type']) == EquipmentType.Energy:
            return EnergyBlock(**data)
        elif EquipmentType(data['Type']) == EquipmentType.Gun:
            return GunBlock(**data)
        elif EquipmentType(data['Type']) == EquipmentType.Engine:
            return EngineBlock(**data)
        elif EquipmentType(data['Type']) == EquipmentType.Health:
            return HealthBlock(**data)


@dataclass
class EnergyBlock(EquipmentBlock):
    IncrementPerTurn: int
    MaxEnergy: int
    StartEnergy: int
    Type = EquipmentType.Energy


@dataclass
class EngineBlock(EquipmentBlock):
    MaxAccelerate: int
    Type = EquipmentType.Engine


@dataclass
class GunBlock(EquipmentBlock):
    Damage: int
    EffectType: EffectType
    EnergyPrice: int
    Radius: int
    Type = EquipmentType.Gun


@dataclass
class HealthBlock(EquipmentBlock):
    MaxHealth: int
    StartHealth: int


@dataclass
class EffectType(EquipmentBlock):
    MaxHealth: int
    StartHealth: int
    Type = EquipmentType.Health


# endregion

# region battle commands

@dataclass
class CommandParameters(JSONCapability):
    pass


@dataclass
class AttackCommandParameters(CommandParameters):
    Id: int
    Name: str
    Target: Vector


@dataclass
class MoveCommandParameters(CommandParameters):
    Id: int
    Target: Vector


@dataclass
class AccelerateCommandParameters(CommandParameters):
    Id: int
    Vector: Vector


@dataclass
class UserCommand(JSONCapability):
    Command: str
    Parameters: CommandParameters


@dataclass
class BattleOutput(JSONCapability):
    Message: str = None
    UserCommands: List[UserCommand] = None


# endregion

# region draft commands
@dataclass
class MapRegion(JSONCapability):
    From: Vector
    To: Vector

    @classmethod
    def from_json(cls, data):
        v1 = Vector.from_json(data['From'])
        v2 = Vector.from_json(data['To'])
        return cls(v1, v2)


@dataclass
class DraftEquipment(JSONCapability):
    Size: int
    Equipment: List[EquipmentBlock]

    @classmethod
    def from_json(cls, data):
        size = data['Size']
        equipment = EquipmentBlock.from_json(data['Equipment'])
        return cls(size, equipment)


@dataclass
class DraftCompleteShip(JSONCapability):
    Id: str
    Price: int
    Equipment: List[str]

    @classmethod
    def from_json(cls, data):
        Id = data['Id']
        price = data['Price']
        equipment = data['Equipment']
        return cls(Id, price, equipment)


@dataclass
class DraftShipChoice(JSONCapability):
    CompleteShipId: str
    Position: Vector = None


@dataclass
class DraftOptions(JSONCapability):
    PlayerId: int
    MapSize: int
    Money: int
    MaxShipsCount: int
    # DraftTimeOut: int
    # BattleRoundTimeOut: int
    StartArea: MapRegion
    Equipment: List[DraftEquipment]
    Ships: List[DraftCompleteShip]

    @classmethod
    def from_json(cls, data):
        start_area = MapRegion.from_json(data['StartArea'])
        equipment = list(map(DraftEquipment.from_json, data['Equipment']))
        ships = list(map(DraftCompleteShip.from_json, data['CompleteShips']))
        player_id = data['PlayerId']
        map_size = data['MapSize']
        money = data['Money']
        max_ships_count = data['MaxShipsCount']
        # draft_time_out = data['DraftTimeOut']
        # battle_round_time_out = data['BattleRoundTimeOut']
        return cls(player_id, map_size, money, max_ships_count, start_area, equipment, ships)
        # return cls(player_id, map_size, money, max_ships_count, draft_time_out, battle_round_time_out,
        #            start_area, equipment, ships)


@dataclass
class DraftChoice(JSONCapability):
    Message: str = None
    Ships: List[DraftCompleteShip] = None


# endregion

# region battle state

@dataclass
class Ship(JSONCapability):
    Id: int
    Position: Vector
    Velocity: Vector
    Energy: Optional[int] = None
    Health: Optional[int] = None
    Equipment: List[EquipmentBlock] = None

    @classmethod
    def from_json(cls, data):
        if data.get('Equipment'):
            data['Equipment'] = list(map(EquipmentBlock.from_json, data.get('Equipment', [])))
        data['Position'] = Vector.from_json(data['Position'])
        data['Velocity'] = Vector.from_json(data['Velocity'])
        return cls(**data)

    def get_all_points(self):
        return [self.Position,
                self.Position + Vector(1, 0, 0),
                self.Position + Vector(0, 1, 0),
                self.Position + Vector(0, 0, 1),
                self.Position + Vector(1, 1, 0),
                self.Position + Vector(0, 1, 1),
                self.Position + Vector(1, 0, 1),
                self.Position + Vector(1, 1, 1)]


@dataclass
class FireInfo(JSONCapability):
    EffectType: EffectType
    Source: Vector
    Target: Vector

    @classmethod
    def from_json(cls, data):
        data['Source'] = Vector.from_json(data['Source'])
        data['Target'] = Vector.from_json(data['Target'])
        return cls(**data)


@dataclass
class BattleState(JSONCapability):
    FireInfos: List[FireInfo]
    My: List[Ship]
    Opponent: List[Ship]

    @classmethod
    def from_json(cls, data):
        my = list(map(Ship.from_json, data['My']))
        opponent = list(map(Ship.from_json, data['Opponent']))
        fire_infos = list(map(FireInfo.from_json, data['FireInfos']))
        return cls(fire_infos, my, opponent)


# endregion


# help methods
def shoot_nearest_enemy(ship, battle_state: BattleState, battle_output):
    global debug_string
    # выбирает самый слабый корабль до которого может дострелить
    guns = [x for x in ship.Equipment if isinstance(x, GunBlock)]  # берем все блоки оружия
    if not guns:  # нет оружия - не стреляем
        return
    gun = guns[0]  # самое простое получение пушки TODO написать норм алгоритм
    available = []  # список доступных целей в формате [(хп цели, вектор стрельбы)]
    for enemy in battle_state.Opponent:
        min_distance = 1000000  # ищем ближайшую точку врага
        min_vector = None
        for point in enemy.get_all_points():  # перебираем все точки
            dist_to_point = abs(point - ship.Position)  # расстояние до точки по Чебышеву
            if gun.Radius >= dist_to_point and dist_to_point < min_distance:  # если можем дострелить и точка ближе всех остальных
                min_distance = dist_to_point
                min_vector = point
        if min_distance < 1000000:  # если нашли точку, до которой можем дострелить, то добаляем
            available.append((enemy.Health, min_vector))
    if not available:  # если никого не можем задеть не стреляем
        return
    best_target = sorted(available, key=lambda x: x[0])[0][1]  # враг с самым низким здоровьем
    debug_string += '   ' + str(ship.Id) + ':' + str(available)
    battle_output.UserCommands.append(UserCommand(Command="ATTACK",
                                                  Parameters=AttackCommandParameters(ship.Id,
                                                                                     gun.Name,
                                                                                     best_target)))


def adapt(team: int, vector: Vector):
    if team == 1:
        return Vector(draft_options.MapSize - 2 - vector.X,
                      draft_options.MapSize - 2 - vector.Y,
                      draft_options.MapSize - 2 - vector.Z)
    return vector


def speed_limiter(initial, limit):
    if initial > limit:
        return limit
    if initial < limit * -1:
        return limit * -1
    return initial


draft_options: DraftOptions
debug_string = ''


def make_draft(data: dict) -> DraftChoice:
    # принимаем данные
    global draft_options
    draft_options = DraftOptions.from_json(data)
    draft_choice = DraftChoice(Message='AHAHAHA')
    # пихаем все корабли руками (место выбирается автоматически)
    draft_choice.Ships = []
    for i in range(5):
        draft_choice.Ships.append(DraftShipChoice('scout'))
    return draft_choice


def make_turn(data: dict) -> BattleOutput:
    global debug_string, draft_options
    # принимаем данные
    team = draft_options.PlayerId
    battle_state = BattleState.from_json(data)
    battle_output = BattleOutput()
    battle_output.UserCommands = []
    for ship in battle_state.My:
        # каждому отдельному кораблю даём команду двигаться на автопилоте
        battle_output.UserCommands.append(
            UserCommand(Command="MOVE",
                        Parameters=MoveCommandParameters(ship.Id, adapt(team, Vector(15, 15, 15))))
        )
        shoot_nearest_enemy(ship, battle_state, battle_output)
    battle_output.Message = debug_string
    debug_string = ''
    return battle_output


def play_game():
    global draft_options
    while True:
        raw_line = input()
        line = json.loads(raw_line)
        if 'PlayerId' in line:
            print(json.dumps(make_draft(line), default=lambda x: x.to_json(), ensure_ascii=False))
        elif 'My' in line:
            print(json.dumps(make_turn(line), default=lambda x: x.to_json(), ensure_ascii=False))


if __name__ == '__main__':
    play_game()
