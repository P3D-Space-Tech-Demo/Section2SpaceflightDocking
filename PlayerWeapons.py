from panda3d.core import CollisionSphere, CollisionNode, CollisionRay, CollisionSegment, CollisionHandlerQueue, CollisionTraverser
from panda3d.core import BitMask32
from panda3d.core import Vec3
from panda3d.core import OmniBoundingVolume
from panda3d.core import Shader
from panda3d.core import TextNode
from panda3d.core import PandaNode
from direct.actor.Actor import Actor

from direct.gui.OnscreenText import OnscreenText

from Weapon import Weapon, Projectile, SeekingProjectile, ProjectileWeapon
from Explosion import Explosion

from CommonValues import *
from Common import Common

import random, math

class BlasterWeapon(ProjectileWeapon):
    def __init__(self):
        projectile = Projectile("Models/blasterShot", MASK_INTO_ENEMY,
                                100, 3, 75, 0.5, 0, 10,
                                0, "Models/blast")
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 0.2
        self.firingDelayPeriod = -1

        self.energyCost = 1

    def fire(self, owner, dt):
        if owner.energy > self.energyCost:
            ProjectileWeapon.fire(self, owner, dt)
            owner.alterEnergy(-self.energyCost)

    def triggerPressed(self, owner):
        ProjectileWeapon.triggerPressed(self, owner)

        if self.firingTimer <= 0:
            self.fire(owner, 0)

    def triggerReleased(self, owner):
        ProjectileWeapon.triggerReleased(self, owner)

    def update(self, dt, owner):
        ProjectileWeapon.update(self, dt, owner)

    def cleanup(self):
        ProjectileWeapon.cleanup(self)

class Rocket(SeekingProjectile):
    def __init__(self, model, mask, range, damage, speed, size, knockback, flinchValue,
                 aoeRadius = 0, blastModel = None,
                 pos = None, damageByTime = False):
        SeekingProjectile.__init__(self, model, mask, range, damage, speed, size, knockback, flinchValue,
                 aoeRadius, blastModel,
                 pos, damageByTime)

        self.acceleration = 100

    def impact(self, impactee):
        explosion = Explosion(7, 0.3, 0.55, 0)
        explosion.activate(Vec3(0, 0, 0), self.root.getPos(render))
        Common.framework.currentLevel.explosions.append(explosion)

        SeekingProjectile.impact(self, impactee)

class RocketWeapon(ProjectileWeapon):
    def __init__(self):
        projectile = Rocket("Models/rocket", MASK_INTO_ENEMY,
                            200, 55, 45, 0.7, 20, 0)
        ProjectileWeapon.__init__(self, projectile)

        self.firingPeriod = 1
        self.firingDelayPeriod = -1

        self.ammoCost = 1

    def fire(self, owner, dt):
        if owner.numMissiles >= self.ammoCost:
            proj = ProjectileWeapon.fire(self, owner, dt)
            proj.owner = owner
            owner.alterMissileCount(-self.ammoCost)

    def triggerPressed(self, owner):
        ProjectileWeapon.triggerPressed(self, owner)

        if self.firingTimer <= 0:
            self.fire(owner, 0)