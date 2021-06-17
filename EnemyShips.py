from panda3d.core import PandaNode, Vec3

from Section2SpaceflightDocking.Enemy import FighterEnemy
from Section2SpaceflightDocking.GameObject import ArmedObject, GameObject, FRICTION
from Section2SpaceflightDocking.Weapon import ProjectileWeapon, Projectile
from Section2SpaceflightDocking.Explosion import Explosion

from Section2SpaceflightDocking.CommonValues import *
from Section2SpaceflightDocking.Common import Common

import random

class BasicEnemyBlaster(ProjectileWeapon):
    def __init__(self):
        projectile = Projectile("../Section2SpaceflightDocking/Models/blasterShotEnemy", MASK_INTO_PLAYER,
                                100, 7, 60, 0.5, 0, 0,
                                0, "../Section2SpaceflightDocking/Models/blast")
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 0.5
        self.firingDelayPeriod = -1

class BasicEnemy(FighterEnemy):
    def __init__(self):
        FighterEnemy.__init__(self, Vec3(0, 0, 0),
                       "../Section2SpaceflightDocking/Models/enemyFighter",
                              100,
                              20,
                              "enemy",
                              4)
        self.actor.setScale(0.5)

        self.deathSound = Common.framework.showBase.loader.loadSfx("../Section2SpaceflightDocking/Sounds/enemyDie.ogg")

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
