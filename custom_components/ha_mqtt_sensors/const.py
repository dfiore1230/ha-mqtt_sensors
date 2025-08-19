DOMAIN = "ha_mqtt_sensors"
PLATFORMS = ["binary_sensor", "sensor"]

CONF_SENSOR_ID = "sensor_id"
CONF_NAME = "name"
CONF_PREFIX = "topic_prefix"
DEFAULT_PREFIX = "sensors_345"

# Device type & availability options
CONF_DEVICE_TYPE = "device_type"           # "door" | "window" | "leak"
DEFAULT_DEVICE_TYPE = "window"
CONF_AVAIL_MINUTES = "availability_minutes"
DEFAULT_AVAIL_MINUTES = 30 

# Optional triggers for contact sensors
CONF_USE_CONTACT = "use_contact_open"
CONF_USE_REED = "use_reed_open"
DEFAULT_USE_CONTACT = False
DEFAULT_USE_REED = False

# Subtopics
TOPIC_TIME = "time"
TOPIC_ID = "id"
TOPIC_CHANNEL = "channel"
TOPIC_EVENT = "event"
TOPIC_STATE = "state"
TOPIC_CONTACT = "contact_open"
TOPIC_REED = "reed_open"
TOPIC_ALARM = "alarm"
TOPIC_TAMPER = "tamper"
TOPIC_BATTOK = "battery_ok"
TOPIC_HEARTBEAT = "heartbeat"
TOPIC_MIC = "mic"

SIG_UPDATE = "ha_mqtt_sensors_update"
SUFFIX_AVAILABILITY = "availability"

# Normalized text states for contact sensors
CONTACT_OPEN_STATES = {"open", "opened", "wet", "leak"}
CONTACT_CLOSED_STATES = {"close", "closed", "dry"}

# Event codes for contact sensors
# Different firmware/conditions may report a variety of values while still
# indicating a simple open/closed state.  Include the known variants so the
# contact entity can normalize them.
CONTACT_OPEN_EVENTS = {160, 168, 192, 200, 232}
CONTACT_CLOSED_EVENTS = {128, 40, 64, 104}
