from api.dependencies import get_db_session
from auth.utils import create_access_token
from crud import crud_user
from db_models.user_model import User
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

auth_router = APIRouter(prefix="/auth", tags=["auth"])

templates = Jinja2Templates(directory="auth/templates")


@auth_router.post("/token")
async def get_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_db_session)
) -> dict[str, str]:
    """
    Gets user by username and password. Then generate access token.

    :param form_data: Login form data. Contains username and password.
    :param session: Sqlalchemy session.
    :return: access token
    """
    user: User | None = await crud_user.read_user_by_username(
        session=session,
        username=form_data.username,
    )
    if user is None:
        raise HTTPException(status_code=400, detail="Wrong username or password")

    # if not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Wrong username or password"
    #     )

    access_token = create_access_token({"user_id": user.user_id})

    return {"access_token": access_token, "token_type": "Bearer"}


@auth_router.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    """
    Renders login page for jwt access token.

    :param request: Request
    :return: Rendered login page.
    """
    context = {"request": request}
    return templates.TemplateResponse("login.html", context=context)
