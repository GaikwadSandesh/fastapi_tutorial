from fastapi import APIRouter, Depends, HTTPException, Response, status
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session


router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: schemas.UserOut = Depends(oauth2.get_current_user),
):
    print(vote)
    # print(current_user)
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    # print(post)
    # print(vote)
    # print(current_user)

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {vote.post_id} not found",
        )

    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )

    found_vote = vote_query.first()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"vote already exists"
            )
        new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id)
        db.add(new_vote)
        db.commit()

        return {"detail": "vote created"}
    else:
        if not found_vote:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"vote not found"
            )
        db.delete(found_vote)
        db.commit()
        return {"detail": "vote deleted"}
