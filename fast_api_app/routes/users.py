from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import date, timedelta
from fast_api_app.database.connect_db import get_db
from fast_api_app.schemas import UserSchema, UserResponse, UserDb
from fast_api_app.repository import users as repository_users
from fast_api_app.database.models import User, UserAuth
from fast_api_app.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix='/users', tags=["users"])


@router.get("/", response_model=List[UserResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                     current_user: UserAuth = Depends(auth_service.get_current_user)):
    """
    The read_users function returns a list of users.

    :param skip: int: Skip the first n users
    :param limit: int: Limit the number of users returned
    :param db: Session: Pass the database session to the function
    :param current_user: UserAuth: Get the current user from the database
    :return: A list of users
    :doc-author: Trelent
    """
    users = await repository_users.get_users(skip, limit, current_user, db)
    return users


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_me function is a GET request that returns the current user's information.
        It requires authentication, and it uses the auth_service to get the current user.

    :param current_user: User: Get the current user from the database
    :return: The current user object
    :doc-author: Trelent
    """
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    """
    The update_avatar_user function is used to update the avatar of a user.
        The function takes in an UploadFile object, which contains the file that will be uploaded to Cloudinary.
        It also takes in a User object, which is obtained from auth_service.get_current_user(). This ensures that only
        authenticated users can access this endpoint and change their own avatars (and not anyone else's). Finally, it
        takes in a Session object for database access.

    :param file: UploadFile: Get the file from the request body
    :param current_user: User: Get the current user from the database
    :param db: Session: Get the database session
    :return: The updated user
    :doc-author: Trelent
    """
    cloudinary.config(
        cloud_name="dmybldclv",
        api_key="592143484358843",
        api_secret="YqKAI25KSkQ9UwyWxPn_gcwX-3A",
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'NotesApp/{current_user.username}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'NotesApp/{current_user.username}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.get("/birthdays", response_model=List[UserResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_birthdays(db: Session = Depends(get_db),
                         current_user: UserAuth = Depends(auth_service.get_current_user)):
    """
    The read_birthdays function returns a list of users who have birthdays in the next 7 days.
    The function takes an optional db parameter, which is used to access the database.
    If no db parameter is provided, then it will use the default get_db() function to obtain a database connection.

    :param db: Session: Pass the database session to the function
    :param current_user: UserAuth: Get the current user from the database
    :return: A list of users with birthdays in the next 7 days
    :doc-author: Trelent
    """
    today = date.today()
    end_date = today + timedelta(days=7)
    birthdays = await repository_users.get_birthday(today, end_date, current_user, db)
    if birthdays is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return birthdays


@router.get("/search", response_model=List[UserResponse], description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search(db: Session = Depends(get_db), current_user: UserAuth = Depends(auth_service.get_current_user),
                 first_name: str = Query(None), last_name: str = Query(None), email: str = Query(None)):
    """
    The search function allows users to search for other users by first name, last name, or email.
        The function takes in the following parameters:
            - db: a database session object that is used to query the database. This parameter is automatically passed in
                when this function is called from an endpoint (see below). It can also be manually passed into this function
                if it needs to be called outside of an endpoint (e.g., during testing) and a database session object needs
                to be provided as input. If no value for db is provided when calling this function, then Depends(get

    :param db: Session: Get the database session
    :param current_user: UserAuth: Get the current user from the database
    :param first_name: str: Get the first name of the user from the request body
    :param last_name: str: Search for a user by last name
    :param email: str: Get the email of the user to be deleted
    :return: A list of users, but the user_id function returns a single user
    :doc-author: Trelent
    """
    users = await repository_users.search_users(first_name, last_name, email, current_user, db)
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return users


@router.get("/{user_id}", response_model=UserResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_user(user_id: int, db: Session = Depends(get_db),
                    current_user: UserAuth = Depends(auth_service.get_current_user)):
    """
    The read_user function is used to read a single user from the database.
    It takes in an integer user_id, and returns a User object.

    :param user_id: int: Specify the user id of the user to be updated
    :param db: Session: Pass the database session to the function
    :param current_user: UserAuth: Get the current user
    :return: A user object
    :doc-author: Trelent
    """
    users = await repository_users.get_user(user_id, current_user, db)
    if users is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 requests per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_users(body: UserSchema, db: Session = Depends(get_db),
                       current_user: UserAuth = Depends(auth_service.get_current_user)):
    """
    The create_users function creates a new user in the database.

    :param body: UserSchema: Validate the body of the request
    :param db: Session: Get the database session
    :param current_user: UserAuth: Get the current user from the database
    :return: The user object created
    :doc-author: Trelent
    """
    return await repository_users.create_users(body, current_user, db)


@router.put("/{user_id}", response_model=UserResponse, description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_user(body: UserSchema, user_id: int, db: Session = Depends(get_db),
                      current_user: UserAuth = Depends(auth_service.get_current_user)):
    """
    The update_user function updates a user in the database.
        The function takes three arguments:
            body (UserSchema): A UserSchema object containing the new values for the user.
            user_id (int): An integer representing the ID of a specific user to update.
            db (Session, optional): A SQLAlchemy Session object used to query and modify data in a database. Defaults to Depends(get_db).

    :param body: UserSchema: Validate the body of the request
    :param user_id: int: Identify the user to update
    :param db: Session: Get the database session
    :param current_user: UserAuth: Get the current user
    :return: A user object
    :doc-author: Trelent
    """
    user = await repository_users.update_user(user_id, body, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=UserResponse, description='No more than 10 requests per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_user(user_id: int, db: Session = Depends(get_db),
                      current_user: UserAuth = Depends(auth_service.get_current_user)):
    """
    The remove_user function removes a user from the database.
        The function takes in an integer representing the id of the user to be removed,
        and returns a User object if successful.

    :param user_id: int: Specify the user_id of the user to be removed
    :param db: Session: Pass the database session to the function
    :param current_user: UserAuth: Get the current user
    :return: The removed user
    :doc-author: Trelent
    """
    user = await repository_users.remove_user(user_id, current_user, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
