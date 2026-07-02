# Добавьте эндпойнт PATCH /contacts/{id} для частичного обновления контакта.


from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict


app = FastAPI()


# --- Модели данных ---

class ContactCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=5, max_length=20)
    email: EmailStr


class ContactUpdate(BaseModel):
    # Все поля необязательные — это как раз подходит и для PATCH
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=5, max_length=20)
    email: Optional[EmailStr] = None


class Contact(ContactCreate):
    id: int


# --- In-memory хранилище ---

contacts_db: Dict[int, dict] = {}
next_id: int = 1

def get_next_id() -> int:
    global next_id
    current = next_id
    next_id += 1
    return current


# --- CRUD-эндпоинты ---

@app.post("/contacts", response_model=Contact, status_code=status.HTTP_201_CREATED)
def create_contact(contact: ContactCreate):
    contact_id = get_next_id()
    contacts_db[contact_id] = {
        "name": contact.name,
        "phone": contact.phone,
        "email": contact.email,
    }
    return Contact(id=contact_id, **contacts_db[contact_id])


@app.get("/contacts", response_model=List[Contact])
def list_contacts():
    return [
        Contact(id=cid, **data)
        for cid, data in contacts_db.items()
    ]


@app.get("/contacts/{contact_id}", response_model=Contact)
def get_contact(contact_id: int):
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )
    data = contacts_db[contact_id]
    return Contact(id=contact_id, **data)


@app.put("/contacts/{contact_id}", response_model=Contact)
def update_contact(contact_id: int, contact_update: ContactUpdate):
    """
    Полная замена полей, которые переданы.
    Если поле передано как None — оно не обновляется (логика частичного обновления).
    """
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    existing = contacts_db[contact_id]

    if contact_update.name is not None:
        existing["name"] = contact_update.name
    if contact_update.phone is not None:
        existing["phone"] = contact_update.phone
    if contact_update.email is not None:
        existing["email"] = contact_update.email

    return Contact(id=contact_id, **existing)


@app.patch("/contacts/{contact_id}", response_model=Contact)
def patch_contact(contact_id: int, contact_update: ContactUpdate):
    """
    Частичное обновление: обновляются только те поля, которые явно переданы в запросе.
    Это семантика PATCH. Логика здесь совпадает с PUT в этой простой реализации,
    но метод HTTP и назначение разные.
    """
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )

    existing = contacts_db[contact_id]

    # Обновляем только те поля, что пришли и не равны None
    if contact_update.name is not None:
        existing["name"] = contact_update.name
    if contact_update.phone is not None:
        existing["phone"] = contact_update.phone
    if contact_update.email is not None:
        existing["email"] = contact_update.email

    return Contact(id=contact_id, **existing)


@app.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int):
    if contact_id not in contacts_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Контакт не найден"
        )
    del contacts_db[contact_id]
