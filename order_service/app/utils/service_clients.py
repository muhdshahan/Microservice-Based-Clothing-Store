import httpx
import os
from fastapi import HTTPException, status
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logger = logging.getLogger(__name__)

# Service URLs with fallbacks
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://localhost:8000")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8001")

# Configure retry policy
RETRY_POLICY = {
    "stop": stop_after_attempt(3),
    "wait": wait_exponential(multiplier=1, min=2, max=10),
    "reraise": True
}

async def make_service_request(
    method: str,
    service_url: str,
    endpoint: str,
    **kwargs
):
    """Generic service request handler with retries and logging"""
    url = f"{service_url}{endpoint}"
    logger.info(f"Making {method} request to {url}")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.request(method, url, **kwargs)
            logger.debug(f"Response from {url}: {response.status_code}")
            return response
        except httpx.ConnectError as e:
            logger.error(f"Connection error to {url}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service at {service_url} is unreachable"
            )
        except httpx.TimeoutException as e:
            logger.error(f"Timeout calling {url}")
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Service request timed out"
            )

@retry(**RETRY_POLICY)
async def get_user_by_id(user_id: int):
    """Get user details from user service"""
    response = await make_service_request(
        "GET",
        USER_SERVICE_URL,
        f"/users/{user_id}"
    ) 
    
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    elif response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"User service returned {response.status_code}"
        )
    
    return response.json()

@retry(**RETRY_POLICY)
async def get_item_by_id(item_id: int):
    """Get item details from inventory service"""
    response = await make_service_request(
        "GET",
        INVENTORY_SERVICE_URL,
        f"/items/{item_id}"
    )
    
    if response.status_code == 404:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} not found"
        )
    elif response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Inventory service returned {response.status_code}"
        )
    
    return response.json()


# Connection with inventory for checking the stock
@retry(**RETRY_POLICY)
async def check_item_availability(item_id: int) -> int:
    """Check available quantity of an item"""
    item = await get_item_by_id(item_id)
    return item.get("quantity", 0)

@retry(**RETRY_POLICY)
async def reduce_inventory(item_id: int, qty: int):
    """Reduce item quantity in inventory"""
    response = await make_service_request(
        "PUT",
        INVENTORY_SERVICE_URL,
        f"/items/{item_id}/decrease",
        json={"qty": qty}
    )

    if response.status_code != 200:
        logger.error(f"Failed to reduce inventory for item {item_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to reduce inventory for item {item_id}"
        )

@retry(**RETRY_POLICY)
async def increase_inventory(item_id: int, qty: int):
    """Increase item quantity in inventory"""
    response = await make_service_request(
        "PUT",
        INVENTORY_SERVICE_URL,
        f"/items/{item_id}/increase",
        json={"qty": qty}
    )

    if response.status_code != 200:
        logger.error(f"Failed to increase inventory for item {item_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to increase inventory for item {item_id}"
        )
