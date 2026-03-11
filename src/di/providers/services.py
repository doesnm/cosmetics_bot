from dishka import Provider, Scope, provide

from src.core.interfaces.ai_provider import AIProvider
from src.core.interfaces.notifier import ManagerNotifier
from src.core.interfaces.uow import UnitOfWork
from src.infrastructure.survey_config.registry import SurveyFlowRegistry
from src.services.manager_service import ManagerService
from src.services.order_service import OrderService
from src.services.product_service import ProductService
from src.services.recommendation_service import RecommendationService
from src.services.prompt_builder import PromptBuilder
from src.services.survey_service import SurveyService
from src.services.user_service import UserService


class ServiceProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def provide_user_service(
        self,
        uow: UnitOfWork,
    ) -> UserService:
        return UserService(uow=uow)

    @provide
    def provide_product_service(
        self,
        uow: UnitOfWork,
    ) -> ProductService:
        return ProductService(uow=uow)

    @provide
    def provide_survey_service(
        self,
        uow: UnitOfWork,
        registry: SurveyFlowRegistry,
    ) -> SurveyService:
        return SurveyService(uow=uow, flow_registry=registry)

    @provide
    def provide_recommendation_service(
        self,
        ai_provider: AIProvider,
        product_service: ProductService,
        prompt_builder: PromptBuilder,
        uow: UnitOfWork,
    ) -> RecommendationService:
        return RecommendationService(
            ai_provider=ai_provider,
            product_service=product_service,
            prompt_builder=prompt_builder,
            uow=uow,
        )

    @provide
    def provide_order_service(
        self,
        uow: UnitOfWork,
    ) -> OrderService:
        return OrderService(uow=uow)

    @provide
    def provide_manager_service(
        self,
        uow: UnitOfWork,
        notifier: ManagerNotifier,
    ) -> ManagerService:
        return ManagerService(uow=uow, notifier=notifier)
