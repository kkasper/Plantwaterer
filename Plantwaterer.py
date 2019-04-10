from WateringSite import create_app, db
from WateringSite.models import User, WateringEvent, Device

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Device': Device, 'WateringEvent': WateringEvent}
