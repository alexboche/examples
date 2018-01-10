import eye
import time
from talon import ctrl, tap
from talon.voice import Context
ctx = Context('mouse')

x, y = ctrl.mouse_pos()
mouse_history = [(x, y, time.time())]
force_move = None

def on_move(_, e):
    mouse_history.append((e.x, e.y, time.time()))
    if force_move:
        e.x, e.y = force_move
        return True
tap.register(tap.MMOVE, on_move)

def click_pos(m):
    word = m._words[0]
    start = (word.start + min((word.end - word.start) / 2, 0.05)) / 1000.0
    diff, pos = min([(abs(start - pos[2]), pos) for pos in mouse_history])
    return pos[:2]

def delayed_click(m, button=0, times=1):
    global force_move
    with ctrl.lock:
        try:
            # force_move = mouse_history[-1][:2]
            lx, ly = mouse_history[-1][:2]
            x, y = click_pos(m)
            ctrl.mouse(x, y)
            for i in range(times):
                ctrl.mouse_click(x, y, button=button, times=i+1)
            time.sleep(0.05)
            ctrl.mouse(lx, ly)
        finally:
            force_move = None

def delayed_right_click(m):
    delayed_click(m, button=1)

def delayed_dubclick(m):
    delayed_click(m, button=0, times=2)

def delayed_tripclick(m):
    delayed_click(m, button=0, times=3)

def mouse_drag(m):
    x, y = click_pos(m)
    ctrl.mouse_click(x, y, down=True)

def mouse_release(m):
    x, y = click_pos(m)
    ctrl.mouse_click(x, y, up=True)

keymap = {
    'righty': delayed_right_click,
    'click': delayed_click,
    'dubclick': delayed_dubclick,
    'tripclick': delayed_tripclick,
    'drag': mouse_drag,
    'release': mouse_release,
}
ctx.keymap(keymap)

def unload():
    ctx.disable()
    tap.unregister(tap.MMOVE, on_move)
