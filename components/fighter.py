import tcod as libtcod

from game_messages import Message

class Fighter:
    def __init__(self, hp, defense, power):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

    def take_damage(self, amount):

        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner})
        
        return results

    def heal(self, amount):
        self.hp += amount

        if self.hp > self.max_hp:
            self.hp = self.max_hp


    def cast_lightning(*args, **kwargs):
        
        caster = args[0]
        entities = kwargs.get('entities')
        fov_map = kwargs.get('fov_map')
        damage = kwargs.get('damage')
        maximum_range = kwargs.get('maximum_range')

        results = []

        target = None
        closest_distance = maximum_range + 1

        for entity in entities:
            if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
                distance = caster.distance_to(entity)

                if distance < closest_distance:
                    target = entity
                    closest_distance = distance

        if target:
            results.append({'consumed': True, 
                            'target': target, 
                            'message': Message('A lightning bolt strikes the {0} with a loud thunder! The damage is {1}'.format(target.name, damage))})
            results.extend(target.fighter.take_damage(damage))
        else:
            results.append({'consumed': False,
                            'target': None,
                            'message': Message('No enemy is close enough to strike.', libtcod.red)})


    def attack(self, target):

        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            target.fighter.take_damage(damage)
            
            results.append({'message': Message('{0} attacks {1} for {2} hit points.'.format(
                self.owner.name.capitalize(), target.name, str(damage)), libtcod.white)})

            results.extend(target.fighter.take_damage(damage))


        else:
            results.append({'message': Message('{0} attacks {1} but does no damage.'.format(
                self.owner.name.capitalize(), target.name), libtcod.white)})

        return results