
from fastapi import APIRouter

router = APIRouter()
# Print is handled via payment webhook mostly, 
# but could add manual retry here if needed.
