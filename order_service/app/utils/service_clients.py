# Handles REST calls to User & Inventory
import httpx
import os
from fastapi import HTTPException

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL","http://localhost:8000")
INVENTORY_SERVICE_URL = os.getenv("INVENTORY_SERVICE_URL", "http://localhost:8001")

async def get_user_by_id(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
        return response.json()
    
async def get_item_by_id(item_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{INVENTORY_SERVICE_URL}/items/{item_id}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="User not found")
        return response.json()