import obspython as obs

source_name = "Timer"
start_hours = 0
start_minutes = 0
start_seconds = 0
countdown = False
timer_seconds = 0
timer_active = False
start_with_recording = False
stop_signal = False

def timer_callback():
    global timer_seconds, timer_active, countdown, stop_signal
    
    if stop_signal or not timer_active:
        return

    if countdown:
        timer_seconds -= 1
        if timer_seconds < 0:
            timer_seconds = 0
            timer_active = False
    else:
        timer_seconds += 1

    update_timer_text()
    obs.remove_current_callback()
    obs.timer_add(timer_callback, 1000)

def update_timer_text():
    time_string = "{:02d}:{:02d}:{:02d}".format(timer_seconds // 3600, (timer_seconds % 3600) // 60, timer_seconds % 60)
    source = obs.obs_get_source_by_name(source_name)

    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", time_string)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

def start_timer(props, prop):
    global timer_active
    timer_active = True

def pause_timer(props, prop):
    global timer_active
    timer_active = False

def reset_timer(props, prop):
    global timer_seconds, timer_active, start_seconds, start_minutes, start_hours
    timer_seconds = start_seconds + start_minutes * 60 + start_hours * 3600
    timer_active = False
    update_timer_text()

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "source_name", "Text Source Name", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "start_hours", "Start Hours", 0, 23, 1)
    obs.obs_properties_add_int(props, "start_minutes", "Start Minutes", 0, 59, 1)
    obs.obs_properties_add_int(props, "start_seconds", "Start Seconds", 0, 59, 1)
    obs.obs_properties_add_bool(props, "countdown", "Countdown")
    obs.obs_properties_add_bool(props, "start_with_recording", "Start with recording")
    obs.obs_properties_add_button(props, "start_button", "Start Timer", start_timer)
    obs.obs_properties_add_button(props, "pause_button", "Pause Timer", pause_timer)
    obs.obs_properties_add_button(props, "reset_button", "Reset Timer", reset_timer)
    return props

def script_update(settings):
    global source_name, start_hours, start_minutes, start_seconds, countdown, start_with_recording, timer_seconds
    source_name = obs.obs_data_get_string(settings, "source_name")
    if not start_with_recording:
        start_hours = obs.obs_data_get_int(settings, "start_hours")
        start_minutes = obs.obs_data_get_int(settings, "start_minutes")
        start_seconds = obs.obs_data_get_int(settings, "start_seconds")
    countdown = obs.obs_data_get_bool(settings, "countdown")
    start_with_recording = obs.obs_data_get_bool(settings, "start_with_recording")
    if not start_with_recording:
        timer_seconds = start_seconds + start_minutes * 60 + start_hours * 3600
    update_timer_text()

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "source_name", "Timer")
    obs.obs_data_set_default_int(settings, "start_hours", 0)
    obs.obs_data_set_default_int(settings, "start_minutes", 0)
    obs.obs_data_set_default_int(settings, "start_seconds", 0)
    obs.obs_data_set_default_bool(settings, "countdown", False)
    obs.obs_data_set_default_bool(settings, "start_with_recording", False)

def on_event(event):
    global timer_active, start_hours, start_minutes, start_seconds, timer_seconds, start_with_recording
    if event == obs.OBS_FRONTEND_EVENT_RECORDING_STARTED and start_with_recording:
        if not timer_active:
            timer_seconds = start_seconds + start_minutes * 60 + start_hours * 3600
        timer_active = True
    elif event == obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED and start_with_recording:
        timer_active = False
        start_hours = timer_seconds // 3600
        start_minutes = (timer_seconds % 3600) // 60
        start_seconds = timer_seconds % 60

def script_load(settings):
    obs.timer_add(timer_callback, 1000)
    obs.obs_frontend_add_event_callback(on_event)

def script_unload():
    global stop_signal
    stop_signal = True
    obs.obs_frontend_remove_event_callback(on_event)

