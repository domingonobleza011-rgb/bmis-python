from ..models import CERTIFICATE_MODELS
from ..crud_factory import build_certificate_router

# One real, fully working router per certificate type — same behavior as
# the original 9 services_*.php + admn_*.php page pairs, generated from
# CERTIFICATE_MODELS in models.py instead of duplicated by hand.
certificate_routers = [
    build_certificate_router(prefix, model, tag=f"certificates-{prefix}")
    for prefix, model in CERTIFICATE_MODELS.items()
]
