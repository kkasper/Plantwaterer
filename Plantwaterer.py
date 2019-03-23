from WateringSite import create_app, db
from WateringSite.models import User, WateringEvent

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'WateringEvent': WateringEvent}
