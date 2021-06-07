from direct.showbase.ShowBase import ShowBase

from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import CollisionTraverser, CollisionHandlerPusher, CollisionSphere, CollisionTube, CollisionNode
from panda3d.core import Vec4, Vec3, Vec2
from panda3d.core import WindowProperties
from panda3d.core import Shader
from panda3d.core import ClockObject

from direct.gui.DirectGui import *

from GameObject import *
from Player import *
from Enemy import *
from Level import Level

from Common import Common

import random

class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        #globalClock.setMode(ClockObject.M_limited)
        #globalClock.setFrameRate(60)

        self.win.setClearColor(Vec4(0, 0, 0, 1))

        self.disableMouse()

        Common.initialise()
        Common.framework = self

        properties = WindowProperties()
        properties.setSize(1000, 750)
        self.win.requestProperties(properties)

        self.exitFunc = self.cleanup

        render.setShaderAuto()

        self.keyMap = {
            "up" : False,
            "down" : False,
            "left" : False,
            "right" : False,
            "shoot" : False,
            "shootSecondary" : False
        }

        self.accept("w", self.updateKeyMap, ["up", True])
        self.accept("w-up", self.updateKeyMap, ["up", False])
        self.accept("s", self.updateKeyMap, ["down", True])
        self.accept("s-up", self.updateKeyMap, ["down", False])
        #self.accept("a", self.updateKeyMap, ["left", True])
        #self.accept("a-up", self.updateKeyMap, ["left", False])
        #self.accept("d", self.updateKeyMap, ["right", True])
        #self.accept("d-up", self.updateKeyMap, ["right", False])
        self.accept("mouse1", self.updateKeyMap, ["shoot", True])
        self.accept("mouse1-up", self.updateKeyMap, ["shoot", False])
        self.accept("mouse3", self.updateKeyMap, ["shootSecondary", True])
        self.accept("mouse3-up", self.updateKeyMap, ["shootSecondary", False])

        self.accept("\\", self.toggleFriction)

        self.accept("f", self.toggleFrameRateMeter)
        self.showFrameRateMeter = False

        self.pusher = CollisionHandlerPusher()
        self.traverser = CollisionTraverser()
        self.traverser.setRespectPrevTransform(True)

        self.pusher.add_in_pattern("%fn-into-%in")
        self.pusher.add_in_pattern("%fn-into")
        self.pusher.add_again_pattern("%fn-again-into")
        self.accept("projectile-into", self.projectileImpact)
        self.accept("projectile-again-into", self.projectileImpact)
        self.accept("player-into", self.gameObjectPhysicalImpact)
        self.accept("enemy-into", self.gameObjectPhysicalImpact)

        self.updateTask = taskMgr.add(self.update, "update")

        self.player = None
        self.currentLevel = None

        self.gameOverScreen = DirectDialog(frameSize = (-0.7, 0.7, -0.7, 0.7),
                                           fadeScreen = 0.4,
                                           relief = DGG.FLAT)
        self.gameOverScreen.hide()

        label = DirectLabel(text = "Game Over!",
                            parent = self.gameOverScreen,
                            scale = 0.1,
                            pos = (0, 0, 0.2),
                            #text_font = self.font,
                            relief = None)

        self.finalScoreLabel = DirectLabel(text = "",
                                           parent = self.gameOverScreen,
                                           scale = 0.07,
                                           pos = (0, 0, 0),
                                           #text_font = self.font,
                                           relief = None)

        btn = DirectButton(text = "Restart",
                           command = self.openMenu,
                           pos = (-0.3, 0, -0.2),
                           parent = self.gameOverScreen,
                           scale = 0.07,
                           #text_font = self.font,
                           frameSize = (-4, 4, -1, 1),
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2))
        btn.setTransparency(True)

        btn = DirectButton(text = "Quit",
                           command = self.quit,
                           pos = (0.3, 0, -0.2),
                           parent = self.gameOverScreen,
                           scale = 0.07,
                           #text_font = self.font,
                           frameSize = (-4, 4, -1, 1),
                           text_scale = 0.75,
                           relief = DGG.FLAT,
                           text_pos = (0, -0.2))
        btn.setTransparency(True)

        self.render.setShaderAuto()

        # Temporary; these are intended to come from previous player-decisions
        # in the final game
        self.shipSpecs = []

        # Light fighter
        shipSpec = ShipSpec()
        shipSpec.gunPositions = [
            Vec3(-2, 1, -2),
            Vec3(2, 1, -2),
            Vec3(-5, 1, 0),
            Vec3(5, 1, 0),
            Vec3(-2, 1, 2),
            Vec3(2, 1, 2)
        ]
        shipSpec.missilePositions = [
            Vec3(0, 1, -2),
        ]
        shipSpec.maxEnergy = 200
        shipSpec.shieldRechargeRate = 7
        shipSpec.energyRechargeRate = 20
        shipSpec.maxShields = 50
        shipSpec.numMissiles = 5
        shipSpec.maxSpeed = 25
        shipSpec.turnRate = 200
        shipSpec.acceleration = 60
        shipSpec.cockpitModelFile = "Models/cockpit"

        self.shipSpecs.append(shipSpec)

        # Medium fighter
        shipSpec = ShipSpec()
        shipSpec.gunPositions = [
            Vec3(-2, 1, -2),
            Vec3(0, 1, -2),
            Vec3(2, 1, -2)
        ]
        shipSpec.missilePositions = [
            Vec3(-2, 1, -2),
            Vec3(2, 1, -2),
        ]
        shipSpec.maxEnergy = 100
        shipSpec.shieldRechargeRate = 10
        shipSpec.energyRechargeRate = 15
        shipSpec.maxShields = 100
        shipSpec.numMissiles = 15
        shipSpec.maxSpeed = 18
        shipSpec.turnRate = 150
        shipSpec.acceleration = 40
        shipSpec.cockpitModelFile = "Models/cockpit"

        self.shipSpecs.append(shipSpec)

        # Heavy missile-platform
        shipSpec = ShipSpec()
        shipSpec.gunPositions = [
            Vec3(0, 1, -2),
        ]
        shipSpec.missilePositions = [
            Vec3(-5, 1, -2),
            Vec3(-5, 1, 0),
            Vec3(5, 1, -2),
            Vec3(5, 1, 0),
        ]
        shipSpec.maxEnergy = 50
        shipSpec.shieldRechargeRate = 20
        shipSpec.energyRechargeRate = 7
        shipSpec.maxShields = 200
        shipSpec.numMissiles = 400
        shipSpec.maxSpeed = 14
        shipSpec.turnRate = 100
        shipSpec.acceleration = 20
        shipSpec.cockpitModelFile = "Models/cockpit"

        self.shipSpecs.append(shipSpec)

        self.tempMenu = DirectFrame(frameSize = (-1, 1, -1, 1))
        btn1 = DirectButton(text = "Light Fighter: \"Serpent\"",
                            parent = self.tempMenu,
                            scale = 0.1,
                            pos = (0, 0, 0.7),
                            command = self.testStart,
                            extraArgs = [0])
        btn02 = DirectButton(text = "Medium Interceptor: \"Manticore\"",
                            parent = self.tempMenu,
                            scale = 0.1,
                            pos = (0, 0, 0.15),
                            command = self.testStart,
                            extraArgs = [1])
        btn2 = DirectButton(text = "Heavy Bombardment Platform: \"Dragon\"",
                            parent = self.tempMenu,
                            scale = 0.1,
                            pos = (0, 0, -0.4),
                            command = self.testStart,
                            extraArgs = [2])

        blurb1 = DirectLabel(text = "Fast, manoeuvrable, and fitted with no less than six blasters and\nan energy reserve to match, the \"Serpent\" is devastating in battle.\n\nHowever, the dedication of so much energy to weapons and engines\nleaves it little for its shields, and its light frame will carry no more than five missiles.\n\nA ship for the experienced, or the reckless.",
                             parent = self.tempMenu,
                             scale = 0.045,
                             pos = (0, 0, 0.6))
        blurb2 = DirectLabel(text = "The \"Manticore\" is a solid all-purpose fighter.\n\nReasonable shield-performance keeps the ship safe, while three blasters\nsupported by a decent energy-bank provide solid firepower.\nIn reserve are fifteen missiles for use against more-difficult targets.",
                             parent = self.tempMenu,
                             scale = 0.045,
                             pos = (0, 0, 0.05))
        blurb1 = DirectLabel(text = "Beware, should the \"Dragon\" enter the battle-field.\n\nHeavy shielding wards it against attack, while a battery of no less than\nfour hundred missiles devastates whatever it's pointed at.\n\nOn the down-side, the dedication of so much space to missiles\nleaves it with little for energy-generation, and both its engines and\nweapons-energy suffer for it.\n\nSimilarly, only a single blaster is fitted to the ship,\nlimiting its usefulness once ammunition runs out.",
                             parent = self.tempMenu,
                             scale = 0.045,
                             pos = (0, 0, -0.5))

    def openMenu(self):
        self.cleanup()
        self.gameOverScreen.hide()
        self.tempMenu.show()

    def testStart(self, index):
        self.startGame(self.shipSpecs[index])
        self.tempMenu.hide()

    def toggleFriction(self):
        Common.useFriction = not Common.useFriction

    def toggleFrameRateMeter(self):
        self.showFrameRateMeter = not self.showFrameRateMeter

        self.setFrameRateMeter(self.showFrameRateMeter)

    def startGame(self, shipSpec):
        self.gameOverScreen.hide()

        self.cleanup()

        self.player = Player(shipSpec)

        self.currentLevel = Level("spaceLevel")

    def updateKeyMap(self, controlName, controlState, callback = None):
        self.keyMap[controlName] = controlState

        if callback is not None:
            callback(controlName, controlState)

    def update(self, task):
        dt = globalClock.getDt()

        if self.currentLevel is not None:
            self.currentLevel.update(self.player, self.keyMap, dt)

            if self.player is not None and self.player.health <= 0:
                if self.gameOverScreen.isHidden():
                    self.gameOverScreen.show()
                    #self.finalScoreLabel["text"] = "Final score: " + str(self.player.score)
                    #self.finalScoreLabel.setText()

            self.traverser.traverse(render)

            if self.player is not None and self.player.health > 0:
                self.player.postTraversalUpdate(dt)

        return Task.cont

    def projectileImpact(self, entry):
        fromNP = entry.getFromNodePath()
        proj = fromNP.getPythonTag(TAG_OWNER)

        intoNP = entry.getIntoNodePath()
        if intoNP.hasPythonTag(TAG_OWNER):
            intoObj = intoNP.getPythonTag(TAG_OWNER)
            proj.impact(intoObj)
        else:
            proj.impact(None)

    def gameObjectPhysicalImpact(self, entry):
        fromNP = entry.getFromNodePath()
        if fromNP.hasPythonTag(TAG_OWNER):
            fromNP.getPythonTag(TAG_OWNER).physicalImpact(entry.getSurfaceNormal(render))

    def triggerActivated(self, entry):
        intoNP = entry.getIntoNodePath()
        trigger = intoNP.getPythonTag(TAG_OWNER)

        if self.currentLevel is not None:
            self.currentLevel.triggerActivated(trigger)

    def cleanup(self):
        if self.currentLevel is not None:
            self.currentLevel.cleanup()
            self.currentLevel = None

        if self.player is not None:
            self.player.cleanup()
            self.player = None

    def quit(self):
        self.cleanup()

        base.userExit()

game = Game()
game.run()
