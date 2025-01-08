from voluptuous import Schema, Required, Any

notificationSchema = Schema({
    Required('token'): str,
    Required('company_id'): str,
    Required('position'): Any('in', 'out'),
})
