from .greenhouse import GreenhouseAdapter
from .lever import LeverAdapter
from .ashby import AshbyAdapter
from .workday import WorkdayAdapter
from .custom import CustomAdapter
from .kula import KulaAdapter
from .adaptive import AdaptiveBrowserAdapter
from .foundation import FoundationMedicineAdapter
from .smartrecruiters import SmartRecruitersAdapter
from .gem import GemAdapter
from .recruitee import RecruiteeAdapter
from .oracle import OracleAdapter
from .career_page import CareerPageAdapter
from .browser_career import BrowserCareerPageAdapter
from .indigo_ag import IndigoAgAdapter
from .successfactors import SuccessFactorsAdapter
from .jazzhr import JazzHRAdapter
from .empty import EmptyAdapter
from .ultipro import UltiProAdapter
from .hologic import HologicAdapter
from .jobvite import JobviteAdapter
from .adp import ADPAdapter
from .icims import ICIMSAdapter
from .promega import PromegaAdapter
from .eligo import EligoAdapter

ADAPTERS = {
    "greenhouse": GreenhouseAdapter,
    "lever": LeverAdapter,
    "ashby": AshbyAdapter,
    "workday": WorkdayAdapter,
    "custom": CustomAdapter,
    "kula": KulaAdapter,
    "adaptive": AdaptiveBrowserAdapter,
    "foundation": FoundationMedicineAdapter,
    "smartrecruiters": SmartRecruitersAdapter,
    "gem": GemAdapter,
    "recruitee": RecruiteeAdapter,
    "oracle": OracleAdapter,
    "career_page": CareerPageAdapter,
    "browser_career": BrowserCareerPageAdapter,
    "indigo_ag": IndigoAgAdapter,
    "successfactors": SuccessFactorsAdapter,
    "jazzhr": JazzHRAdapter,
    "empty": EmptyAdapter,
    "ultipro": UltiProAdapter,
    "hologic": HologicAdapter,
    "jobvite": JobviteAdapter,
    "adp": ADPAdapter,
    "icims": ICIMSAdapter,
    "promega": PromegaAdapter,
    "eligo": EligoAdapter,
}
