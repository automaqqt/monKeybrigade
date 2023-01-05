
from models import Work
from listener.util import DictObj
from sqlalchemy.orm import scoped_session
from datetime import datetime

class BrigadePlugin:
        def __init__(
            self,
            db: scoped_session,
        ):
            self.monkey_venues = ['1099622537608']
            self.db = db

        def process(self, trace, block):
            venue_visit = self.parse_trace(trace)
            print([venue_visit.user, venue_visit.venue_owner,block['timestamp']])
            new_work = Work(
                block_time = block['timestamp'],
                venue_id = venue_visit.venue_id,
                mnky = venue_visit.venue_id in self.monkey_venues,
                venue_owner = venue_visit.venue_owner,
                user = venue_visit.user
            )
            self.db.add(new_work)
            self.db.commit()
        
        def parse_trace(self,trace):
            return DictObj(trace['data'])