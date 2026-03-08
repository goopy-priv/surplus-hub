import logging
from typing import List, Optional

from sqlalchemy import or_, desc, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.chat import ChatRoom, Message
from app.schemas.chat_response import ChatRoomCreate, MessageCreate

logger = logging.getLogger(__name__)


class CRUDChatRoom(CRUDBase[ChatRoom, ChatRoomCreate, dict]):
    def get_user_rooms(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[ChatRoom], int]:
        # Subquery: latest message time per room
        last_msg_time = (
            db.query(
                Message.chat_room_id,
                func.max(Message.created_at).label("last_message_time"),
            )
            .group_by(Message.chat_room_id)
            .subquery()
        )

        query = (
            db.query(ChatRoom)
            .outerjoin(last_msg_time, ChatRoom.id == last_msg_time.c.chat_room_id)
            .filter(or_(ChatRoom.buyer_id == user_id, ChatRoom.seller_id == user_id))
            .order_by(desc(func.coalesce(last_msg_time.c.last_message_time, ChatRoom.created_at)))
        )

        total = query.count()
        rooms = query.offset(skip).limit(limit).all()
        return rooms, total

    def get_or_create(
        self, db: Session, *, material_id: Optional[int], buyer_id: int, seller_id: int
    ) -> tuple[ChatRoom, bool]:
        existing = db.query(ChatRoom).filter(
            ChatRoom.material_id == material_id,
            ChatRoom.buyer_id == buyer_id,
            ChatRoom.seller_id == seller_id,
        ).first()

        if existing:
            return existing, False

        db_obj = ChatRoom(
            material_id=material_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
        )
        db.add(db_obj)
        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj, True
        except IntegrityError:
            db.rollback()
            logger.info(
                "ChatRoom race condition: duplicate for material=%s buyer=%s seller=%s",
                material_id, buyer_id, seller_id,
            )
            existing = db.query(ChatRoom).filter(
                ChatRoom.material_id == material_id,
                ChatRoom.buyer_id == buyer_id,
                ChatRoom.seller_id == seller_id,
            ).first()
            return existing, False

    def is_participant(self, room: ChatRoom, user_id: int) -> bool:
        return room.buyer_id == user_id or room.seller_id == user_id


    def get_user_rooms_cursor(
        self, db: Session, *, user_id: int, cursor: Optional[int] = None, limit: int = 20
    ) -> tuple[List[ChatRoom], Optional[int]]:
        """Cursor-based pagination for chat rooms."""
        query = (
            db.query(ChatRoom)
            .filter(or_(ChatRoom.buyer_id == user_id, ChatRoom.seller_id == user_id))
        )
        if cursor:
            query = query.filter(ChatRoom.id < cursor)

        query = query.order_by(desc(ChatRoom.id))
        items = query.limit(limit + 1).all()

        next_cursor = None
        if len(items) > limit:
            items = items[:limit]
            next_cursor = items[-1].id

        return items, next_cursor


class CRUDMessage(CRUDBase[Message, MessageCreate, dict]):
    def get_room_messages(
        self, db: Session, *, room_id: int, skip: int = 0, limit: int = 50
    ) -> tuple[List[Message], int]:
        query = db.query(Message).filter(
            Message.chat_room_id == room_id
        ).order_by(desc(Message.created_at))

        total = query.count()
        messages = query.offset(skip).limit(limit).all()
        return messages, total

    def create_message(
        self,
        db: Session,
        *,
        room_id: int,
        sender_id: int,
        content: str,
        message_type: str = "TEXT",
    ) -> Message:
        db_obj = Message(
            chat_room_id=room_id,
            sender_id=sender_id,
            content=content,
            message_type=message_type,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def mark_as_read(self, db: Session, *, room_id: int, user_id: int) -> int:
        count = db.query(Message).filter(
            Message.chat_room_id == room_id,
            Message.sender_id != user_id,
            Message.is_read.is_(False),
        ).update({"is_read": True})
        if count > 0:
            db.commit()
        return count

    def get_unread_count(self, db: Session, *, room_id: int, user_id: int) -> int:
        return db.query(Message).filter(
            Message.chat_room_id == room_id,
            Message.sender_id != user_id,
            Message.is_read.is_(False),
        ).count()

    def get_last_message(self, db: Session, *, room_id: int) -> Optional[Message]:
        return db.query(Message).filter(
            Message.chat_room_id == room_id
        ).order_by(desc(Message.created_at)).first()


crud_chat_room = CRUDChatRoom(ChatRoom)
crud_message = CRUDMessage(Message)
