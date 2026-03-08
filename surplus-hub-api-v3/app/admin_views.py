from sqladmin import ModelView
from app.models.user import User
from app.models.material import Material
from app.models.chat import ChatRoom, Message
from app.models.community import Post, Comment

class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.name, User.role, User.trust_level]
    column_searchable_list = [User.name, User.email]
    icon = "fa-solid fa-user"

class MaterialAdmin(ModelView, model=Material):
    column_list = [Material.id, Material.title, Material.price, Material.status, Material.seller_id]
    column_searchable_list = [Material.title, Material.description]
    column_sortable_list = [Material.price, Material.created_at]
    icon = "fa-solid fa-box"

class ChatRoomAdmin(ModelView, model=ChatRoom):
    column_list = [ChatRoom.id, ChatRoom.material_id, ChatRoom.buyer_id, ChatRoom.seller_id]
    icon = "fa-solid fa-comments"

class PostAdmin(ModelView, model=Post):
    column_list = [Post.id, Post.title, Post.category, Post.author_id]
    icon = "fa-solid fa-newspaper"
