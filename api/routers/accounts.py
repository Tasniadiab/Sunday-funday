from fastapi import (
    Body,
    status,
    Depends,
    Request,
    Response,
    APIRouter,
    HTTPException,
)

from utils.authenticator import authenticator
from models.accounts import (
    Account,
    AccountOut,
    AccountForm,
    AccountToken,
    AccountUpdate,
    DuplicateAccountError,
)
from uuid import UUID
from clients.client import db
from models.apis import HttpError
from repositories.accounts import AccountRepo


router = APIRouter()


# @router.get("/token", response_model=AccountToken)
# async def get_token(request: Request) -> AccountToken:
#     # check for cookie
#     if authenticator.cookie_name not in request.cookies:
#         raise HTTPException(
#             status_code=400, detail="Required cookie not found"
#         )

#     # response body
#     return {
#         "access_token": request.cookies[authenticator.cookie_name],
#         "type": "Bearer",
#     }


@router.get("/token", response_model=AccountToken | None)
async def get_token(
    request: Request,
    account: AccountOut = Depends(authenticator.try_get_current_account_data),
) -> AccountToken | None:
    if account and authenticator.cookie_name in request.cookies:
        return {
            "access_token": request.cookies[authenticator.cookie_name],
            "type": "Bearer",
            "account": account,
        }


# AUTH clause. Use this function when ready
# @router.get("/token", response_model=AccountToken | None)
# async def get_token(
#     request: Request,
#     account: AccountOut = Depends(authenticator.try_get_current_account_data),
# ) -> AccountToken | None:
#     print("request is:", request)
#     if not account:
#          raise HTTPException(status_code=404, detail="Account not found")
#     elif authenticator.cookie_name not in request.cookies:
#         raise HTTPException(
#             status_code=400, detail="Required cookie not found"
#         )
#     elif authenticator.cookie_name in request.cookies:
#         return {
#             "access_token": request.cookies[authenticator.cookie_name],
#             "type": "Bearer",
#         }


@router.post("/api/accounts", response_model=AccountToken | HttpError)
async def create_account(
    info: Account,
    request: Request,
    response: Response,
    repo: AccountRepo = Depends(),
):
    hashed_password = authenticator.hash_password(info.password)
    try:
        account = repo.create(info, hashed_password)
    except DuplicateAccountError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create an account with those credentials",
        )
    form = AccountForm(username=info.username, password=info.password)
    token = await authenticator.login(response, request, form, repo)
    return AccountToken(account=account, **token.dict())


@router.put(
    "/{id}",
    response_description="Update an account",
    response_model=AccountUpdate,
)
def update_account(
    id: str,
    account: AccountUpdate = Body(...),
    # account: dict = Depends(authenticator.get_current_account_data),
):
    existing_account = db.accounts.find_one({"id": str(id)})

    if not existing_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account with ID {id} not found",
        )

    account_data = {k: v for k, v in account.dict().items() if v is not None}

    if account_data:
        db.accounts.update_one({"_id": str(id)}, {"$set": account_data})

    return db.accounts.find_one({"_id": str(id)})
