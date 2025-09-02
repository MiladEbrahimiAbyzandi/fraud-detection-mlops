from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from data_loader.load_data import load_data
from merge_csvs.merge_data import merge_csvs
from transformation_stage1.transformation_stage_1 import transform_stage1
from splitter.data_splitter import split_data
from metadata.metadata_extractor import metadata

router=APIRouter()

class ArtifactsRequest(BaseModel):
    cards_path: str | None = None
    users_path: str | None = None
    transaction_path: str| None = None
    splite_size: float = 0.2
    random_state: int = 42


@router.get("/artifacts", tags=["Artifacts"])
async def get_artifacts(Request: ArtifactsRequest):
    """
    Get data artifacts in order to apply to the next levels of data transformation.
    """
    try:
        data= load_data(
            cards_path=Request.cards_path,
            users_path=Request.users_path,
            transaction_path=Request.transaction_path
        )

        merged_df=merge_csvs(data.cards, data.users, data.transactions)

        transformed_df=transform_stage1(merged_df)

        X_train, X_test, y_train, y_test = split_data(
            transformed_df,
            test_size=Request.splite_size,
            random_state=Request.random_state
        )

        data_metadata = metadata(X_train, y_train)

        return {
            "metadata": data_metadata
        }
    except Exception as e:
        return HTTPException(
            status_code=500,
            detail= str(e)
        )


