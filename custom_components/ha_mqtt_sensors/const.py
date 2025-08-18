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
DEFAULT_AVAIL_MINUTES = 5

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
CONTACT_OPEN_EVENTS = {160}
CONTACT_CLOSED_EVENTS = {128}
