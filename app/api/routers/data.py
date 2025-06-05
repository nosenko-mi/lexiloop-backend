from os import listdir
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from requests import Session
import shutil
from os.path import isfile, isdir, join

from app.db import text_crud, schemas
from app.db.database import TextsSessionLocal

from app.service.text_parser.config import CHAPTER_TAG
from nltk.tokenize import sent_tokenize

router = APIRouter(
    prefix="/api/data",
    tags=["data"]
)


def get_db():
    db = TextsSessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/dataset",  response_model=schemas.Dataset)
async def create_dataset(dataset: schemas.DatasetCreate, db: Session = Depends(get_db)):
    db_dataset = text_crud.get_dataset_by_title(db, dataset.title)
    if db_dataset:
        raise HTTPException(status_code=400, detail="Dataset already exists")
    return text_crud.create_dataset(db, dataset)


@router.get("/dataset",  response_model=list[schemas.Dataset])
async def get_datasets(offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    datasets = text_crud.get_datasets(db=db, offset=offset, limit=limit)
    return datasets


@router.get("/dataset/{dataset_id}",  response_model=schemas.Dataset)
async def get_dataset(dataset_id: int, db: Session = Depends(get_db)):
    db_dataset = text_crud.get_dataset(db=db, dataset_id=dataset_id)
    if db_dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return db_dataset


@router.get("/text",  response_model=list[schemas.TextFeature])
async def get_texts(dataset_id: int, offset: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    texts = text_crud.get_text_features(
        db=db, dataset_id=dataset_id, offset=offset, limit=limit)
    return texts


@router.post("/text",  response_model=schemas.TextFeature)
async def create_text(feature: schemas.TextFeatureCreate, db: Session = Depends(get_db)):
    # should check first, but whatever...
    return text_crud.create_text_feature(db, feature)


@router.post("/create")
async def create_dataset_from_parsed_text(db: Session = Depends(get_db)):
    source_dir = "./source/parsed"

    if not isdir(source_dir):
        return {"message": "source directory is a file"}

    try:
        files = [f for f in listdir(source_dir) if isfile(join(source_dir, f))]
        print(files)
        for file in files:
            f = open(join(source_dir, file), 'r', encoding='utf-8')
            contents = f.read()
            f.close()
            chapters = contents.split(CHAPTER_TAG)
            # sentences = [sent_tokenize(c) for c in chapters]
            sentences = []
            for c in chapters:
                sentences.extend(sent_tokenize(c))
            print(len(sentences))

            db_dataset = text_crud.get_dataset_by_title(db=db, title=file)
            if not db_dataset:
                dataset = schemas.DatasetCreate(
                    title=file, source=join(source_dir, file))
                db_dataset = text_crud.create_dataset(dataset=dataset, db=db)

            text_features = []
            for s in sentences:
                if len(s) > 150 or len(s) <= 50:
                    continue
                text_features.append(schemas.TextFeatureCreate(
                    text=s, dataset_id=db_dataset.id))

            for feature in text_features:
                text_crud.create_text_feature(db=db, feature=feature)

            return {"processed files": f"{files}", "new features": len(text_features), "dataset": db_dataset.id}
    except Exception as e:
        return {"message": f"encountered error {e}"}


# @router.post("/parse")
# async def parse_static_resource():
#     # source_dir = "./source/raw"
#     # destination_dir = "./source/parsed"
#     # if isdir(source_dir) and isdir(destination_dir):
#     #     files = [f for f in listdir(source_dir) if isfile(join(source_dir, f))]
#     #     for f in files:
#     #         source = join(source_dir, f)
#     #         d, _ = splitext(join(destination_dir, f))
#     #         destination = d + ".txt"
#     #         book = load_book(source)
#     #         paragraphs = get_parapraphs(book)
#     #         save_file(destination, paragraphs)
#     # elif isfile(source_dir) and isfile(destination_dir):
#     #     book = load_book(source_dir)
#     #     paragraphs = get_parapraphs(book)
#     #     save_file(destination_dir, paragraphs)
#     return {"message": f"parse text"}
