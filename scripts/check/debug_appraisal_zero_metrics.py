import asyncio
import os
from pprint import pprint

# Set environment variables for testing
os.environ["ENVIRONMENT"] = "development"

from config.container import container
from domain.appraisal import AppraisalRequest, PropertyCondition


async def test_appraisal():
    appraisal_service = container.appraisal_service

    request = AppraisalRequest(
        city="Florence",
        zone="50123",
        surface_sqm=100,
        condition=PropertyCondition.EXCELLENT,
        phone="+393401234567",
    )

    print(f"--- Running Appraisal for {request.city}, {request.zone} ---")
    try:
        result = appraisal_service.estimate_value(request)
        print("\n--- Result ---")
        pprint(result.model_dump())
    except Exception as e:
        print(f"\n--- Error ---\n{e}")


if __name__ == "__main__":
    asyncio.run(test_appraisal())
