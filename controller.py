import ConfigParser

import gtk
from gtkmvc import Controller
from gtkmvc.adapters import Adapter
from twisted.internet import reactor

from controllers.drivecontroller import DriveController
from controllers.jscontroller import JsController
from controllers.videocontroller import VideoController
from joystick import Joystick

class MainController(Controller):

    def __init__(self, model, view, config):
        Controller.__init__(self, model, view)
        self.config = config
        self.driveController = DriveController(model.driveModel, view.driveView)
        try:
            jsdevnum = self.config.get('joystick', 'jsdevnum')
        except ConfigParser.NoSectionError:
            jsdevnum = 0
        self.jsController = JsController(model, view.jsView, jsdevnum)
        self.videoController = VideoController(model, view.videoView)

    def register_view(self, view):
        view.setConnectState('disconnected')
        try:
            host = self.config.get('connection', 'host')
        except ConfigParser.NoSectionError:
            host = ''
        self.view['entry_host'].set_text(host)

    # signal handlers
    def on_window_main_delete_event(self, win, event):
        reactor.stop()

    def on_exit_activate(self, action):
        reactor.stop()

    def on_btn_connect_clicked(self, widget):
        host = self.view['entry_host'].get_text()
        self.model.connect(host)

    def on_btn_disconnect_clicked(self, widget):
        self.model.disconnect()

    # observers
    @Controller.observe("connected", assign=True)
    def connected_change(self, model, prop_name, info):
        if info.new:
            self.view.setConnectState('connected')
        else:
            self.view.setConnectState('disconnected')

    # special setters

