from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import models, schemas


def create_dataset(db: Session, dataset: schemas.DatasetCreate) -> models.Dataset:
    db_dataset = models.Dataset(title=dataset.title, source=dataset.source)
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset


def get_dataset(db: Session, dataset_id: int) -> models.Dataset:
    return db.scalars(select(models.Dataset).where(models.Dataset.id == dataset_id)).first()


def get_dataset_by_title(db: Session, title: str) -> models.Dataset:
    return db.scalars(select(models.Dataset).where(models.Dataset.title == title)).first()


def get_datasets(db: Session, offset: int, limit: int) -> list[models.Dataset]:
    return db.scalars(select(models.Dataset).offset(offset).limit(limit))


def create_text_feature(db: Session, feature: schemas.TextFeatureCreate) -> models.TextFeature:
    db_feature = models.TextFeature(text=feature.text, dataset_id=feature.dataset_id)
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature


def get_text_feature(db: Session, feature_id: int) -> models.TextFeature:
    return db.scalars(select(models.TextFeature).where(models.TextFeature.id == feature_id)).first()


def get_text_features(db: Session, dataset_id: int, offset: int, limit: int) -> list[models.TextFeature]:
    return db.scalars(select(models.TextFeature).where(models.TextFeature.dataset_id == dataset_id).offset(offset).limit(limit))
