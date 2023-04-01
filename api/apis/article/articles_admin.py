from flask import Response
from flask_restful import Resource
from traceback import format_exception_only
from sqlalchemy.sql.functions import func
from jwt_token import admin_required
from sqlalchemy import desc
from ..utils.pagination import Pagination
from schemas.article import ArticleSchema
from entities import Session
from entities.article import Article
from entities.tag import Tag
from entities.user import User
from helper.message import ARTICLE_NOT_FOUND, PAGE_VALUE_ERROR
from helper.error import ErrorHandler
from helper.response import ResponseHandler


class ArticlesAdminAPI(Resource):
    @admin_required
    def get(self) -> Response:
        # ページネーションのバリデーション
        try:
            pagination = Pagination()
            pagination.check_pagination()
        except ValueError as e:
            return ErrorHandler.error400(PAGE_VALUE_ERROR)
        except Exception as e:
            return ErrorHandler.error400(format_exception_only(type(e), e))

        with Session() as session:
            articles = (
                session.query(Article)
                .order_by(desc(Article.updatedAt), desc(Article.createdAt))
                .offset(pagination.getPage())
                .limit(pagination.perpage)
                .all()
            )
            count = session.query(Article).count()
            session.commit()

            # 記事一覧が空リストなら
            if articles == [] or count == 0:
                return ResponseHandler.res204({"message": "記事が見つかりません｡"})

            return ResponseHandler.res200(
                ArticleSchema(many=True).dump(articles), count
            )


class ArticlesByUserAdminAPI(Resource):
    @admin_required
    def get(self, userName: str) -> Response:
        # ページネーションのバリデーション
        try:
            pagination = Pagination()
            pagination.check_pagination()
        except ValueError as e:
            return ErrorHandler.error400(PAGE_VALUE_ERROR)
        except Exception as e:
            return ErrorHandler.error400(format_exception_only(type(e), e))

        with Session() as session:
            articles = (
                session.query(Article)
                .join(User)
                .filter(User.userName == userName)
                .order_by(desc(Article.updatedAt), desc(Article.createdAt))
                .offset(pagination.getPage())
                .limit(pagination.perpage)
                .all()
            )
            count = (
                session.query(Article)
                .join(User)
                .filter(User.userName == userName)
                .count()
            )
            session.commit()

            # 記事一覧が空リストなら
            if articles == [] or count == 0:
                return ResponseHandler.res204({"message": "記事が見つかりません｡"})

            return ResponseHandler.res200(
                ArticleSchema(
                    many=True,
                    only=[
                        "articleId",
                        "content",
                        "createdAt",
                        "draft",
                        "isActivate",
                        "tags",
                        "title",
                        "updatedAt",
                    ],
                ).dump(articles),
                count,
            )


class ArticlesTagAdminAPI(Resource):
    @admin_required
    def get(self, tagName: str) -> Response:
        # ページネーションのバリデーション
        try:
            pagination = Pagination()
            pagination.check_pagination()
        except ValueError as e:
            return ErrorHandler.error400(PAGE_VALUE_ERROR)
        except Exception as e:
            return ErrorHandler.error400(format_exception_only(type(e), e))

        with Session() as session:
            tag = session.query(Tag).filter(Tag.tagName == tagName).first()
            session.commit()

            if tag is None:
                return ErrorHandler.error404(ARTICLE_NOT_FOUND)

            articles = tag.articles

            # 記事一覧が空リストなら
            if articles == []:
                return ResponseHandler.res204({"message": "記事が見つかりません｡"})

            articles = sorted(
                articles, key=lambda x: (x.updatedAt, x.createdAt), reverse=True
            )
            count = len(articles)
            articles = pagination.sliceList(articles)
            return ResponseHandler.res200(
                ArticleSchema(
                    many=True,
                    only=[
                        "articleId",
                        "content",
                        "createdAt",
                        "draft",
                        "isActivate",
                        "tags",
                        "title",
                        "updatedAt",
                    ],
                ).dump(articles),
                count,
            )


class SearchByTitleArticleAdminAPI(Resource):
    @admin_required
    def get(self, title: str) -> Response:
        # ページネーションのバリデーション
        try:
            pagination = Pagination()
            pagination.check_pagination()
        except ValueError as e:
            return ErrorHandler.error400(PAGE_VALUE_ERROR)
        except Exception as e:
            return ErrorHandler.error400(format_exception_only(type(e), e))

        with Session() as session:
            articles = (
                session.query(Article)
                .filter(
                    func.lower(Article.title).contains(title.lower(), autoescape=True),
                )
                .order_by(desc(Article.updatedAt), desc(Article.createdAt))
                .offset(pagination.getPage())
                .limit(pagination.perpage)
                .all()
            )
            count = (
                session.query(Article)
                .filter(
                    func.lower(Article.title).contains(title.lower(), autoescape=True),
                )
                .count()
            )
            session.commit()

            # 記事一覧が空リストなら
            if articles == [] or count == 0:
                return ResponseHandler.res204({"message": "記事が見つかりません｡"})

            return ResponseHandler.res200(
                ArticleSchema(
                    many=True,
                    only=[
                        "articleId",
                        "content",
                        "createdAt",
                        "draft",
                        "isActivate",
                        "tags",
                        "title",
                        "updatedAt",
                    ],
                ).dump(articles),
                count,
            )
