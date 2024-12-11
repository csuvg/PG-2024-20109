from voluptuous import Schema, Required, Any

notificationSchema = Schema({
    Required('description'): str,
    Required('sender_id'): str,
    Required('receptor_id'): str,
    Required('establishment_id'): str,
    Required('position'): Any('in', 'out'),
    Required('total'): Any(float, int),
    Required('path'): str,
})
