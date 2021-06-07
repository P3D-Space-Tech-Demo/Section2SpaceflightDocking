from GameObject import GameObject, ArmedObject
from panda3d.core import Vec4, Vec3, Vec2, Plane, Point3, BitMask32
from panda3d.core import CollisionSphere, CollisionNode, CollisionRay, CollisionSegment, CollisionHandlerQueue
from panda3d.core import TextureStage
from panda3d.core import ColorBlendAttrib

from CommonValues import *

from Common import Common

import random

class Enemy(GameObject, ArmedObject):
    def __init__(self, pos, modelName, maxHealth, maxSpeed, colliderName, size):
        GameObject.__init__(self, pos, modelName, None, maxHealth, maxSpeed, colliderName,
                            MASK_INTO_ENEMY | MASK_FROM_PLAYER | MASK_FROM_ENEMY, size)
        ArmedObject.__init__(self)

        self.colliderNP.node().setFromCollideMask(MASK_WALLS | MASK_FROM_ENEMY)

        base.pusher.addCollider(self.colliderNP, self.root)
        base.traverser.addCollider(self.colliderNP, base.pusher)

        colliderNode = CollisionNode("lock sphere")
        solid = CollisionSphere(0, 0, 0, size*2)
        solid.setTangible(False)
        colliderNode.addSolid(solid)
        self.lockColliderNP = self.root.attachNewNode(colliderNode)
        self.lockColliderNP.setPythonTag(TAG_OWNER, self)
        colliderNode.setFromCollideMask(0)
        colliderNode.setIntoCollideMask(MASK_ENEMY_LOCK_SPHERE)

        self.setFlinchPool(10, 15)

        self.attackAnimsPerWeapon = {}

        self.flinchAnims = []
        self.flinchTimer = 0

        self.shields = []
        self.shieldDuration = 0.5

        self.movementNames = ["walk"]

    def setFlinchPool(self, minVal, maxVal):
        self.flinchPoolMin = minVal
        self.flinchPoolMax = maxVal

        self.resetFlinchCounter()

    def resetFlinchCounter(self):
        self.flinchCounter = random.uniform(self.flinchPoolMin, self.flinchPoolMax)

    def alterHealth(self, dHealth, incomingImpulse, knockback, flinchValue, overcharge = False):
        GameObject.alterHealth(self, dHealth, incomingImpulse, knockback, flinchValue, overcharge)

        self.flinchCounter -= flinchValue
        if self.flinchCounter <= 0:
            self.resetFlinchCounter()
            self.flinch()

        if dHealth < 0 and incomingImpulse is not None:
            shield = loader.loadModel("Models/shield")
            shield.setScale(self.size)
            shield.reparentTo(self.root)
            shield.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha, ColorBlendAttrib.OOne))
            shield.lookAt(render, self.root.getPos(render) + incomingImpulse)
            shield.setBin("unsorted", 1)
            shield.setDepthWrite(False)
            self.shields.append([shield, 0])

    def flinch(self):
        if len(self.flinchAnims) > 0 and self.flinchTimer <= 0:
            anim = random.choice(self.flinchAnims)
            if self.inControl:
                self.velocity.set(0, 0, 0)
            self.inControl = False
            self.walking = False
            self.flinchTimer = 2

    def update(self, player, dt):
        GameObject.update(self, dt)
        ArmedObject.update(self, dt)

        if self.flinchTimer > 0:
            self.flinchTimer -= dt

        if self.inControl and self.flinchTimer <= 0:
            self.runLogic(player, dt)

        for index, (shield, timer) in enumerate(self.shields):
            timer += dt
            perc = timer / self.shieldDuration
            shield.setTexOffset(TextureStage.getDefault(), perc*3)
            shield.setAlphaScale(1.0 - perc)
            self.shields[index][1] = timer
        self.shields = [[shield, timer] for shield, timer in self.shields if timer < self.shieldDuration]

    def runLogic(self, player, dt):
        pass

    def attackPerformed(self, weapon):
        ArmedObject.attackPerformed(self, weapon)

        if self.attackSound is not None:
            self.attackSound.play()

    def cleanup(self):
        self.lockColliderNP.clearPythonTag(TAG_OWNER)
        ArmedObject.cleanup(self)
        GameObject.cleanup(self)

class FighterEnemy(Enemy):
    STATE_ATTACK = 0
    STATE_BREAK_AWAY = 1
    STATE_FLEE = 2

    def __init__(self, pos, modelName, maxHealth, maxSpeed, colliderName, size):
        Enemy.__init__(self, pos, modelName, maxHealth, maxSpeed, colliderName, size)

        self.acceleration = 100.0

        self.turnRate = 200.0

        self.yVector = Vec2(0, 1)

        self.steeringRayNPs = []

        self.steeringQueue = CollisionHandlerQueue()

        self.state = FighterEnemy.STATE_ATTACK
        self.breakAwayTimer = 0
        self.breakAwayMaxDuration = 3

        for i in range(4):
            ray = CollisionSegment(0, 0, 0, 0, 1, 0)

            rayNode = CollisionNode("steering ray")
            rayNode.addSolid(ray)

            rayNode.setFromCollideMask(MASK_WALLS)
            rayNode.setIntoCollideMask(0)

            rayNodePath = self.actor.attachNewNode(rayNode)

            #rayNodePath.show()

            self.steeringRayNPs.append(rayNodePath)

        base.traverser.addCollider(rayNodePath, self.steeringQueue)

    def runLogic(self, player, dt):
        Enemy.runLogic(self, player, dt)

        selfPos = self.root.getPos(render)

        vectorToPlayer = player.root.getPos() - selfPos

        distanceToPlayer = vectorToPlayer.length()

        quat = self.root.getQuat(render)
        forward = quat.getForward()

        angleToPlayer = forward.angleDeg(vectorToPlayer.normalized())

        testWeapon = self.weaponSets[0][0]

        fireWeapon = False
        if len(self.weaponSets) > 0:
            if distanceToPlayer < testWeapon.desiredRange:
                if angleToPlayer < 30:
                    fireWeapon = True

        if fireWeapon:
            self.startFiringSet(0)
        else:
            self.ceaseFiringSet(0)

        if self.inControl:
            self.walking = True
            if self.state == FighterEnemy.STATE_ATTACK:
                if distanceToPlayer < testWeapon.desiredRange*0.5:
                    self.state = FighterEnemy.STATE_BREAK_AWAY
                    self.breakAwayTimer = self.breakAwayMaxDuration
                else:
                    self.turnTowards(player, self.turnRate, dt)
            elif self.state == FighterEnemy.STATE_BREAK_AWAY:
                self.breakAwayTimer -= dt
                if angleToPlayer < 120:
                    self.turnTowards(selfPos - vectorToPlayer, self.turnRate, dt)
                if distanceToPlayer > testWeapon.desiredRange*2.5 or self.breakAwayTimer <= 0:
                    self.state = FighterEnemy.STATE_ATTACK
            elif self.state == FighterEnemy.STATE_FLEE:
                pass

            self.velocity += forward*self.acceleration*dt


        """if self.currentWeapon is not None:
            if distanceToPlayer > self.currentWeapon.desiredRange*0.9:
                attackControl = self.actor.getAnimControl("attack")
                if not attackControl.isPlaying():
                    self.walking = True
                    quat = self.root.getQuat(render)
                    forward = quat.getForward()
                    if vectorToPlayer.dot(forward) > 0 and self.steeringQueue.getNumEntries() > 0:
                        self.steeringQueue.sortEntries()
                        entry = self.steeringQueue.getEntry(0)
                        hitPos = entry.getSurfacePoint(render)
                        right = quat.getRight()
                        up = quat.getUp()
                        dotRight = vectorToPlayer.dot(right)
                        if STEER_RIGHT in self.steerDirs and dotRight < 0:
                            self.velocity += right*self.acceleration*dt
                            self.root.setH(render, self.root.getH(render) + self.turnRateWalking*2*dt)
                        if STEER_LEFT in self.steerDirs and dotRight >= 0:
                            self.velocity -= right*self.acceleration*dt
                            self.root.setH(render, self.root.getH(render) - self.turnRateWalking*2*dt)
                        if STEER_UP in self.steerDirs:
                            self.velocity += up*self.acceleration*dt
                        if STEER_DOWN in self.steerDirs:
                            self.velocity -= up*self.acceleration*dt
                    else:
                        self.turnTowards(player, self.turnRateWalking, dt)
                        self.velocity += self.root.getQuat(render).getForward()*self.acceleration*dt

                self.endAttacking()
            else:
                self.turnTowards(player, self.turnRateStanding, dt)

                self.walking = False
                self.velocity.set(0, 0, 0)

                self.startAttacking()"""

    def cleanup(self):
        for np in self.steeringRayNPs:
            base.traverser.removeCollider(np)
            np.removeNode()
        self.steeringRayNPs = []
        self.steeringQueue = None
        Enemy.cleanup(self)

