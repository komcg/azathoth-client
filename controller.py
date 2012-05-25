import gtk
from gtkmvc import Controller
from gtkmvc.adapters import Adapter
from twisted.internet import reactor

from joystick import Joystick

class MainController(Controller):

    def __init__(self, model, view):
        Controller.__init__(self, model, view)
        self.joystick = None
        self.joystick_x = 0
        self.joystick_y = 0

    def register_view(self, view):
        view.setConnectState('disconnected')

    def register_adapters(self):
        a = Adapter(self.model, 'estop_act')
        a.connect_widget(self.view['label_estop_act'], setter=self.estop_setter)
        self.adapt(a)
        
        a = Adapter(self.model, 'estop_cmd')
        a.connect_widget(self.view['label_estop_cmd'], setter=self.estop_setter)
        self.adapt(a)
        
        a = Adapter(self.model, 'select_act')
        a.connect_widget(self.view['label_select_act'], setter=self.select_setter)
        self.adapt(a)

        a = Adapter(self.model, 'select_cmd')
        a.connect_widget(self.view['label_select_cmd'], setter=self.select_setter)
        self.adapt(a)

        a = Adapter(self.model, 'moving')
        a.connect_widget(self.view['label_drivestatus'], setter=self.drivestatus_setter)
        self.adapt(a)

        a = Adapter(self.model, 'joy_x')
        a.connect_widget(self.view['label_js_x'], setter=self.joystick_setter)
        self.adapt(a)

        a = Adapter(self.model, 'joy_y')
        a.connect_widget(self.view['label_js_y'], setter=self.joystick_setter)
        self.adapt(a)

    def enableJoystick(self):
        self.joystick_enabled = True
        try:
            self.joystick = Joystick(1)
        except:
            self.joystick_enabled = False
            return
        self.jsAxisHandler = self.joystick.connect('axis', self.on_axis_event)
        self.jsButtonHandler = self.joystick.connect('button', self.on_button_event)

    def disableJoystick(self):
        self.joystick_enabled = False
        if self.joystick is not None:
            self.joystick.disconnect(self.jsAxisHandler)
            self.joystick.disconnect(self.jsButtonHandler)
            self.joystick = None

    # signal handlers
    def on_window_main_delete_event(self, win, event):
        reactor.stop()

    def on_imi_quit_activate(self, widget):
        reactor.stop()

    def on_imi_calibration_activate(self, widget):
        #TODO
        pass

    def on_btn_connect_clicked(self, widget):
        host = self.view['entry_host'].get_text()
        self.model.connect(host)

    def on_btn_disconnect_clicked(self, widget):
        self.model.disconnect()

    def on_rb_js_enable_toggled(self, btn):
        #TODO
        pass

    def on_btn_select_clicked(self, btn):
        self.model.select()

    def on_btn_deselect_clicked(self, btn):
        self.model.deselect()

    def on_tb_estop_clicked(self, btn):
        self.model.estop()

    def on_tb_reset_clicked(self, btn):
        self.model.reset()

    def on_tb_calibrate_clicked(self, btn):
        #TODO
        pass

    def on_axis_event(self, object, axis, value, init):
        if init == 128:
            # Ignore this event. One gets sent per axis when the joystick
            # is initialized. I should really find out why.
            return
        if axis == 0:
            # dividing by 256 scales the value to fit within a signed char
            self.prev_x = self.joystick_x
            self.joystick_x = value / 256
            if self.joystick_x == self.prev_x:
                return
        if axis == 1:
            # this axis needs to be inverted
            self.prev_y = self.joystick_y
            self.joystick_y = -value / 256
            if self.joystick_y == self.prev_y:
                return
        else: # ignore other axises
            return
        self.model.joystickCommand(self.joystick_x, self.joystick_y)

    def on_button_event(self, object, button, value, init):
        pass

    # observers
    @Controller.observe("connected", assign=True)
    def connected_change(self, model, prop_name, info):
        if info.new:
            self.view.setConnectState('connected')
        else:
            self.view.setConnected('disconnected')

    # special setters
    def estop_setter(self, wid, val):
        if val == 'RUN':
            color = gtk.gdk.Color('#00FF00')
        elif val == 'STOP':
            color = gtk.gdk.Color('#FF0000')
        else:
            color = None
        wid.set_label(val)

        if wid == self.view['label_estop_act']: 
            eb = self.view['eb_estop_act']
        else:
            eb = self.view['eb_estop_cmd']
        eb.modify_bg(gtk.STATE_NORMAL, color)

    def select_setter(self, wid, val):
        if val == 'ROBOT':
            color = gtk.gdk.Color('#00FF00')
        elif val == 'CHAIR':
            color = gtk.gdk.Color('#00FFFF')
        else:
            color = None
        wid.set_label(val)
        
        if wid == self.view['label_select_act']:
            eb = self.view['eb_select_act']
        else:
            eb = self.view['eb_select_cmd']
        eb.modify_bg(gtk.STATE_NORMAL, color)
    
    def drivestatus_setter(self, wid, val):
        if val == 'MOVING':
            color = gtk.gdk.Color('#00FF00')
        else:
            color = None
        wid.set_label(val)
        self.view['eb_drivestatus'].modify_bg(gtk.STATE_NORMAL, color)

    def joystick_setter(self, wid, val):
        if val != 0:
            color = gtk.gdk.Color('#00FF00')
        else:
            color = None
        wid.set_label(str(val))
        if wid == self.view['label_js_x']:
            self.view['eb_js_x'].modify_bg(gtk.STATE_NORMAL, color)
        else:
            self.view['eb_js_y'].modify_bg(gtk.STATE_NORMAL, color)

