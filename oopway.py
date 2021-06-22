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

    def clen(self):
        return abs(self)

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
def plotLine3d(x0: int, y0: int, z0: int, x1: int, y1: int, z1: int) -> List:
    res = []
    dx = abs(x1 - x0)
    if x0 < x1:
        sx = 1
    else:
        sx = -1
    dy = abs(y1 - y0)
    if y0 < y1:
        sy = 1
    else:
        sy = -1
    dz = abs(z1 - z0)
    if z0 < z1:
        sz = 1
    else:
        sz = -1
    dm = max(dx, dy, dz)
    x1 = y1 = z1 = dm // 2
    for i in range(dm):
        res.append((x0, y0, z0))
        # setPixel(x0,y0,z0);
        x1 -= dx
        if x1 < 0:
            x1 += dm
            x0 += sx
        y1 -= dy
        if y1 < 0:
            y1 += dm
            y0 += sy
        z1 -= dz
        if z1 < 0:
            z1 += dm
            z0 += sz
    return res


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


def make_simple_move(battle_state: BattleState, battle_output: BattleOutput, ship: Ship, point: Vector):
    battle_output.UserCommands.append(
        UserCommand(Command="MOVE",
                    Parameters=MoveCommandParameters(ship.Id, point)))


def shoot_nearest_enemy(ship, battle_state: BattleState, battle_output):
    global debug_string
    # вибирает самый слабый корабль до которого может дострелить
    guns = [x for x in ship.Equipment if isinstance(x, GunBlock)]  # берем все блоки оружия
    if not guns:  # нет оружия - не стреляем
        return
    gun = guns[0]  # самое простое получение пушки TODO написать норм алгоритм
    available = []  # список доступных целей в формате [(хп цели, вектор стрельбы)]
    for enemy in battle_state.Opponent:
        # ищем блок, из которого будет вестись стрельба
        ships_interposition = enemy.Position - ship.Position  # взаимоположение кораблей
        # пространство вокруг корабля на 8 частей, каждая для своего блока(как геометрические четверти в 3D)
        gun_pos = ship.Position
        if ships_interposition.X >= 0 and ships_interposition.Y >= 0:
            if ships_interposition.Z >= 0:
                gun_pos = ship.Position + Vector(0, 0, 1)
            else:
                gun_pos = ship.Position
        elif ships_interposition.X >= 0 and ships_interposition.Y < 0:
            if ships_interposition.Z >= 0:
                gun_pos = ship.Position + Vector(0, 1, 1)
            else:
                gun_pos = ship.Position + Vector(0, 1, 0)
        elif ships_interposition.X < 0 and ships_interposition.Y >= 0:
            if ships_interposition.Z >= 0:
                gun_pos = ship.Position + Vector(1, 0, 1)
            else:
                gun_pos = ship.Position + Vector(1, 0, 0)
        elif ships_interposition.X < 0 and ships_interposition.Y < 0:
            if ships_interposition.Z >= 0:
                gun_pos = ship.Position + Vector(1, 1, 1)
            else:
                gun_pos = ship.Position + Vector(1, 1, 0)
        min_distance = 1000000  # ищем ближайшую точку врага
        min_vector = None
        for point in enemy.get_all_points():  # перебираем все точки
            dist_to_point = abs(point - gun_pos)  # расстояние до точки по Чебышеву
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


draft_options: DraftOptions
debug_string = ''
WasFirstTurn = False
targets = {}
taken = set()


def make_draft(data: dict) -> DraftChoice:
    # принимаем данные
    global draft_options
    draft_options = DraftOptions.from_json(data)
    draft_choice = DraftChoice(Message=str(draft_options.Ships))
    # пихаем все корабли руками (место выбирается автоматически)
    draft_choice.Ships = []
    for i in range(5):
        if draft_options.Money >= 50:  # ценник forward, покупаем их на все деньги
            draft_choice.Ships.append(DraftShipChoice('forward'))
            draft_options.Money -= 50
        else:
            draft_choice.Ships.append(DraftShipChoice('scout'))
    draft_choice.Message = str(draft_options.StartArea.From) + ' ' + str(draft_options.StartArea.To)
    return draft_choice


def make_turn(data: dict) -> BattleOutput:
    global debug_string, draft_options, targets
    # принимаем данные
    team = draft_options.PlayerId
    battle_state = BattleState.from_json(data)
    battle_output = BattleOutput()
    battle_output.UserCommands = []
    for ship in battle_state.My:
        if targets.get(ship.Id, -1) not in [enemy.Id for enemy in battle_state.Opponent]:
            check_ships = lambda enemy: (enemy.Id in taken, abs(ship.Position - enemy.Position))
            targets[ship.Id] = min(battle_state.Opponent, key=check_ships)
            # targets[ship.Id] = min(battle_state.Opponent, key=lambda enemy: enemy.Health)
        target = targets[ship.Id]
        taken.add(target.Id)
        my_positions = ship.get_all_points()
        target_positions = target.get_all_points()
        closest_point = [draft_options.MapSize, target_positions[0], my_positions[0]]
        for v1 in my_positions:
            for v2 in target_positions:
                dist = abs(v2 - v1)
                if dist < closest_point[0]:
                    closest_point[0] = [dist, v2, v1]

        # ищем пушку
        guns = [x for x in ship.Equipment if isinstance(x, GunBlock)]  # берем все блоки оружия
        engines = [x for x in ship.Equipment if isinstance(x, EngineBlock)]
        engine = engines[0]
        if not guns:
            make_simple_move(battle_state, battle_output, ship, closest_point[1])
            continue
        gun = guns[0]

        if gun.Radius < closest_point[0]:  # слишком далеко
            # каждому отдельному кораблю даём команду двигаться на автопилоте
            make_simple_move(battle_state, battle_output, ship, closest_point[1])
            for i in range(len(guns)):
                shoot_nearest_enemy(ship, battle_state, battle_output)

        elif gun.Radius == closest_point[0]:  # сейчас находимся на окубности
            # затычка
            # make_simple_move(battle_state, battle_output, ship, closest_point[1])
            # shoot_nearest_enemy(ship, battle_state, battle_output)
            # затычка
            # тормозим
            battle_output.UserCommands.append(UserCommand(
                Command="ACCELERATE",
                Parameters=AccelerateCommandParameters(ship.Id, Vector(0, 0, 0) - ship.Velocity))
            )
            for i in range(len(guns)):
                battle_output.UserCommands.append(UserCommand(
                    Command="ATTACK",
                    Parameters=AttackCommandParameters(ship.Id, gun.Name, closest_point[1] + Vector(0, 0, i))))

        else:  # слишком близко
            # затычка
            # make_simple_move(battle_state, battle_output, ship, closest_point[1])
            # затычка
            escape_v = closest_point[2] - closest_point[1]
            if abs(escape_v.X) > engine.MaxAccelerate:
                escape_v.X = engine.MaxAccelerate * (1 if escape_v.X > 0 else -1)
            if abs(escape_v.Y) > engine.MaxAccelerate:
                escape_v.Y = engine.MaxAccelerate * (1 if escape_v.Y > 0 else -1)
            if abs(escape_v.Z) > engine.MaxAccelerate:
                escape_v.Z = engine.MaxAccelerate * (1 if escape_v.Z > 0 else -1)
            test = ship.Position + escape_v
            if test.X <= draft_options.MapSize and test.Y <= draft_options.MapSize and test.Z <= draft_options.MapSize:
                battle_output.UserCommands.append(UserCommand(
                    Command="ACCELERATE",
                    Parameters=AccelerateCommandParameters(ship.Id, escape_v - ship.Velocity))
                )
            else:
                battle_output.UserCommands.append(UserCommand(
                    Command="ACCELERATE",
                    Parameters=AccelerateCommandParameters(ship.Id, Vector(0, 0, 0) - escape_v - ship.Velocity))
                )
                # make_simple_move(battle_state, battle_output, ship, closest_point[1])
            for i in range(len(guns)):
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
