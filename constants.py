
# Start of battle event
EVENT_BATTLE_START = intern("battle start")

# Signaled when round messages have been dispatched and the round has begun
EVENT_ROUND_START = intern("round start")

# Signaled when View is ready to procede to next battle round
EVENT_VIEW_READY = intern("view ready")

# Log message event
EVENT_MESSAGE = intern("message")

# Signaled when a new entity is to be created
EVENT_ENTITY_NEW = intern("entity new")

# Signaled when an entity wishes the viewer to wait before continuing to the next round
EVENT_ENTITY_WAIT = intern("entity wait")

# Signaled when an entity no longer wants to viewer to wait
EVENT_ENTITY_READY = intern("entity ready")

# Signaled when one ship fires upon another
EVENT_ENTITY_FIRE = intern("entity fire")

# Signaled when a ship is damaged
EVENT_ENTITY_DAMAGE = intern("entity damaged")

# Signaled when a ship is destroyed
EVENT_ENTITY_DEATH = intern("entity death")

# Signaled when a laser must be drawn
EVENT_ANIMATION_LASER = intern("animation laser")

# Signaled when a damage animation must be drawn
EVENT_ANIMATION_DAMAGE = intern("animation damage")

# Signaled when a damage animation is complete
EVENT_ANIMATION_DAMAGE_COMPLETE = intern("animation damage complete")