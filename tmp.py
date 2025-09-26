from app.schemas.itinerary import ItineraryPlanRequest
from app.services.itinerary_planner import itinerary_planner
from app.services.recommendation_service import recommendation_service
from app.services.open_data_service import load_default_sources
import asyncio

async def main():
    if recommendation_service.is_initialized:
        return
    await recommendation_service.initialize(load_default_sources())
    req = ItineraryPlanRequest(
        user_id='u',
        preferences={
            'activity_types':['natural','scenic'],
            'budget_range':[100,400],
            'travel_style':'adventure',
            'max_travel_distance':50,
            'group_size':2,
            'duration':3
        },
        current_location={'lat':-41.3,'lng':174.8,'address':'Wellington, New Zealand'},
        save=False
    )
    resp = await recommendation_service.get_recommendations(req)
    plan = itinerary_planner.build_itinerary(req, [r.model_dump() for r in resp.recommendations])
    from pprint import pprint
    pprint(plan['summary'])

asyncio.run(main())
