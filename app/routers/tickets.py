from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Ticket
from app.schemas import TicketCreate, TicketRead

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketRead, status_code=201)
async def create_ticket(
    payload: TicketCreate, session: AsyncSession = Depends(get_session)
):
    ticket = Ticket(**payload.model_dump())
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    return ticket


@router.get("", response_model=list[TicketRead])
async def list_tickets(
    status: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Ticket).order_by(Ticket.id.desc()).limit(limit).offset(offset)
    if status:
        stmt = stmt.where(Ticket.status == status)
    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/{ticket_id}", response_model=TicketRead)
async def get_ticket(ticket_id: int, session: AsyncSession = Depends(get_session)):
    ticket = await session.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket
