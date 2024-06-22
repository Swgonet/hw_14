from typing import List
from libgravatar import Gravatar
from sqlalchemy.orm import Session
from fast_api_app.database.models import User, UserAuth
from fast_api_app.schemas import UserSchema, UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(UserAuth).filter(UserAuth.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.
        Args:
            body (UserModel): The UserModel object containing the data to be inserted into the database.
            db (Session): The SQLAlchemy Session object used to interact with our PostgreSQL database.

    :param body: UserModel: Create a new user object
    :param db: Session: Pass in the database session
    :return: A user object
    :doc-author: Trelent
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = UserAuth(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_avatar(email, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    :param email: Find the user in the database
    :param url: str: Specify the type of data that will be passed to the function
    :param db: Session: Pass the database session to the function
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_token(user: UserAuth, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()


async def get_users(skip: int, limit: int, user: UserAuth, db: Session) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


async def get_user(user_id: int, user: UserAuth, db: Session) -> User:
    return db.query(User).filter(User.id == user_id).first()


async def get_birthday(today, end_date, user: UserAuth, db: Session):
    """
    The get_birthday function returns a list of users whose birthday is between today and the end date.


    :param today: Get the current date, and the end_date parameter is used to set a date range
    :param end_date: Determine the end date of the range
    :param user: UserAuth: Get the user's information from the database
    :param db: Session: Access the database
    :return: A list of users whose birthday is between today and end_date
    :doc-author: Trelent
    """
    users = db.query(User).all()
    result = []
    for user in users:
        if (
                user.birthday_date.month >= today.month and user.birthday_date.day >= today.day and user.birthday_date.month <= end_date.month and user.birthday_date.day <= end_date.day):
            result.append(user)
    return result


async def search_users(first_name: str | None, last_name: str | None, email: str | None, user: UserAuth, db: Session):
    """
    The search_users function searches for users in the database based on first name, last name, or email.
        If a user is found with any of these parameters, they are added to a list and returned.

    :param first_name: str | None: Specify that the first_name parameter is a string or none
    :param last_name: str | None: Search for a user with the last name specified
    :param email: str | None: Search for users with a specific email
    :param user: UserAuth: Check if the user is logged in
    :param db: Session: Access the database
    :return: A list of users that match the search criteria
    :doc-author: Trelent
    """
    result = []
    users = db.query(User).all()
    for user in users:
        if first_name != None:
            if user.first_name == first_name:
                result.append(user)
        if last_name != None:
            if user.last_name == last_name:
                result.append(user)
        if email != None:
            if user.email == email:
                result.append(user)
    return result


async def create_users(body: UserSchema, user: UserAuth, db: Session) -> User:
    """
    The create_users function creates a new user in the database.
        Args:
            body (UserSchema): The UserSchema object containing all of the information for creating a new user.
            db (Session): The SQLAlchemy Session object that is used to communicate with the database.

    :param body: UserSchema: Get the information from the request body
    :param user: UserAuth: Get the user's id from the jwt token
    :param db: Session: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user_ = User(first_name=body.first_name, last_name=body.last_name, birthday_date=body.birthday_date,
                 email=body.email, phone_numbers=body.phone_numbers, other_description=body.other_description)
    db.add(user_)
    db.commit()
    db.refresh(user_)
    return user_


async def update_user(user_id: int, body: UserSchema, user: UserAuth, db: Session) -> User | None:
    """
    The update_user function updates a user's information in the database.
        Args:
            user_id (int): The id of the user to update.
            body (UserSchema): A UserSchema object containing all of the new data for this user.

    :param user_id: int: Find the user in the database
    :param body: UserSchema: Pass the data that is being updated
    :param user: UserAuth: Check if the user is authorized to update a user
    :param db: Session: Access the database
    :return: A user object, which is a model
    :doc-author: Trelent
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.first_name = body.first_name
        user.last_name = body.last_name
        user.phone_numbers = body.phone_numbers
        user.email = body.email
        user.other_description = body.other_description
        db.commit()
    return user


async def remove_user(user_id: int, user: UserAuth, db: Session) -> User | None:
    """
    The remove_user function removes a user from the database.
        Args:
            user_id (int): The id of the user to remove.
            db (Session): A connection to the database.

    :param user_id: int: Specify the user id of the user to be deleted
    :param user: UserAuth: Check if the user is authorized to perform this action
    :param db: Session: Pass the database session to the function
    :return: The user object that was removed from the database
    :doc-author: Trelent
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
    return user


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the email of the user
    :param db: Session: Pass the database session to this function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()
