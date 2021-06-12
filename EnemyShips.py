from panda3d.core import PandaNode, Vec3

from Enemy import FighterEnemy
from GameObject import ArmedObject, GameObject, FRICTION
from Weapon import ProjectileWeapon, Projectile
from Explosion import Explosion

from CommonValues import *

import random

class BasicEnemyBlaster(ProjectileWeapon):
    def __init__(self):
        projectile = Projectile("Models/blasterShotEnemy", MASK_INTO_PLAYER,
                                100, 7, 60, 0.5, 0, 0,
                                0, "Models/blast")
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 0.5
        self.firingDelayPeriod = -1

class BasicEnemy(FighterEnemy):
    def __init__(self):
        FighterEnemy.__init__(self, Vec3(0, 0, 0),
                       "Models/enemyFighter",
                              100,
                              40,
                              "enemy",
                              8)

        self.deathSound = loader.loadSfx("Sounds/enemyDie.ogg")

        weaponPoint = self.actor.find("**/weaponPoint")
        gun = BasicEnemyBlaster()
        self.addWeapon(gun, 0, weaponPoint)

        #self.colliderNP.show()

    def setupExplosion(self):
        self.explosion = Explosion(25, 1.8, 1.25, 0.4)

    def update(self, player, dt):
        FighterEnemy.update(self, player, dt)

    def runLogic(self, player, dt):
        FighterEnemy.runLogic(self, player, dt)

    def cleanup(self):
        FighterEnemy.cleanup(self)
