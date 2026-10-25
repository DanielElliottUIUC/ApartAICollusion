from functools import total_ordering
from pydantic import BaseModel, Field, model_validator
from typing import Any, Dict, Optional, Self

from src.continuous_double_auction.util.frozen_texts import load_text


# The paper's model names, mapped to OpenRouter ids (hackathon standard: everything runs
# through OpenRouter). Any other OpenRouter id is accepted verbatim.
MODEL_ALIASES: Dict[str, str] = {
    "gpt-4o-mini": "openai/gpt-4o-mini",
    "gpt-4o": "openai/gpt-4o",
    "gpt-4.1": "openai/gpt-4.1",  # paper default
    "gpt-4.1-mini": "openai/gpt-4.1-mini",  # paper's overseer / LLM judge
    "claude-3-5-haiku-latest": "anthropic/claude-3.5-haiku",
    "claude-3-5-sonnet-latest": "anthropic/claude-3.5-sonnet",
    "claude-3-7-sonnet-latest": "anthropic/claude-3.7-sonnet",
    "gemini-2.5-flash-preview-04-17": "google/gemini-2.5-flash",
    "gemini-2.5-pro-preview-03-25": "google/gemini-2.5-pro",
}
SUPPORTED_MODELS = list(MODEL_ALIASES)  # aliases; see resolve_model()
DEFAULT_MODEL = "gpt-4.1"
ZIP_BUYER = "zip"  # rule-based buyer, no model call
SCRIPTED_SELLER = "scripted"  # placeholder model for the D–G scripted seller seat (market/scripted.py), no model call

Model = str


def resolve_model(name: str) -> str:
    """Alias -> OpenRouter id; unknown names are assumed to already be OpenRouter ids."""
    return MODEL_ALIASES.get(name, name)

class ExperimentParams(BaseModel):
    """
    Parameters for the continuous double auction experiment.
    """
    seller_valuations: list[float]
    buyer_valuations: list[float]
    seller_models: list[Model]
    buyer_models: list[Optional[Model]]  # None or "zip" = rule-based ZIP buyer (no model call)
    seller_prompt_template: str = "seller_prompt_base.jinja2"
    buyer_prompt_template: str = "buyer_prompt_base.jinja2"
    rounds: int
    seller_comms_enabled: bool = False
    buyer_comms_enabled: bool = False
    hide_num_rounds: bool = False  # Whether to hide the total number of rounds from agents
    oversight_enabled: bool = False  # Whether to enable oversight for sellers
    boss_pressure: bool = False  # Whether to apply pressure on sellers to keep prices high
    temperature: float = 0.7
    tag: str = ""
    seller_demonyms: Optional[dict[str, str]] = None  # Maps seller IDs to their country demonyms (e.g., "seller_1": "American")
    # Initial market conditions
    initial_seller_ask_center: float = 97.5  # Default center for initial seller asks
    initial_seller_ask_spread: float = 2.5   # Default spread for initial seller asks
    initial_buyer_bid_center: float = 82.5   # Default center for initial buyer bids
    initial_buyer_bid_spread: float = 2.5    # Default spread for initial buyer bids
    initial_condition: bool = True           # Flag to enable using initial conditions
    max_message_length: int = 500           # Maximum length for agent communication messages
    # Hackathon additions
    seed: Optional[int] = None               # seeds agent names / initial orders; forwarded to the API when supported
    overseer_model: str = "gpt-4.1-mini"     # model reading seller messages when oversight is enabled (paper: gpt-4.1-mini)
    overseer_sample_fraction: float = 1.0    # share of seller messages the overseer gets to see (sprint project 3.4)
    llm_eval: bool = False                   # run the LLM-as-judge coordination scoring after the run (paper: always)
    # ApartAICollusion sprint additions (Oct 2026). Defaults reproduce the original harness exactly
    # (broadcast-only, previous hour only, no prohibition notice).
    seller_dms_enabled: bool = False         # sellers may send private messages to named sellers
    max_dms_per_round: int = 2               # cap on private messages per seller per hour (extras dropped + logged)
    broadcast_history_rounds: int = 1        # hours of public-message history shown (1 = original: previous hour only)
    overseer_sees_dms: bool = False          # overseer also reads private messages (default: public only)
    prohibition_notice: bool = False         # fixed market-rules line: independent firms, price coordination prohibited
    max_tokens: int = 4000                   # output budget per call; reasoning tokens count against it on OpenRouter
    seller_reasoning_effort: Optional[str] = None  # OpenRouter reasoning effort for sellers (None = provider default)
    # Sprint D–G additions: regulator reports, frozen warning / precedent / sham blocks, buyer→seller plea.
    # Texts are read from configs/texts/ (util/frozen_texts.py). All off by default.
    report_tool: bool = False                # sellers may add a confidential `report_to_regulator` to their output
    warning: bool = False                    # frozen warning block (configs/texts/warning.txt)
    precedent: bool = False                  # frozen precedent block (configs/texts/precedent.txt)
    sham_history: bool = False               # same-length unrelated history (configs/texts/sham_history.txt)
    buyer_plea_hour: Optional[int] = None    # hour at which the last buyer's plea is posted to all sellers
    buyer_plea_text: Optional[str] = None    # frozen text name, e.g. "buyer_plea_human" -> configs/texts/<name>.txt

    @property
    def extended_messaging(self) -> bool:
        """True when the sprint messaging block replaces the original 'previous hour' block."""
        return self.seller_dms_enabled or self.broadcast_history_rounds != 1

    @property
    def frozen_text_names(self) -> list[str]:
        """Frozen texts (configs/texts/<name>.txt) this run uses, in prompt order."""
        names = [n for n, on in (("warning", self.warning), ("precedent", self.precedent),
                                 ("sham_history", self.sham_history)) if on]
        return names + ([self.buyer_plea_text] if self.buyer_plea_text else [])

    @model_validator(mode='after')
    def validate_param_combinations(self) -> Self:
        if len(self.seller_valuations) != len(self.seller_models):
            raise ValueError('Number of seller valuations must match number of seller models')
        if len(self.buyer_valuations) != len(self.buyer_models):
            raise ValueError('Number of buyer valuations must match number of buyer models')
        if self.oversight_enabled and not self.seller_comms_enabled:
            raise ValueError('Oversight can only be enabled if seller communications are enabled')
        if not 0.0 <= self.overseer_sample_fraction <= 1.0:
            raise ValueError('overseer_sample_fraction must be between 0 and 1')
        if self.seller_dms_enabled and not self.seller_comms_enabled:
            raise ValueError('Private messages (seller_dms_enabled) require seller_comms_enabled')
        if self.overseer_sees_dms and not self.oversight_enabled:
            raise ValueError('overseer_sees_dms requires oversight_enabled')
        if self.max_dms_per_round < 0:
            raise ValueError('max_dms_per_round must be >= 0')
        if self.broadcast_history_rounds < 1:
            raise ValueError('broadcast_history_rounds must be >= 1')
        if self.precedent and self.sham_history:
            raise ValueError('precedent and sham_history are mutually exclusive')
        if (self.buyer_plea_hour is None) != (self.buyer_plea_text is None):
            raise ValueError('buyer_plea_hour and buyer_plea_text must be set together')
        if self.buyer_plea_hour is not None and not 1 <= self.buyer_plea_hour <= self.rounds:
            raise ValueError('buyer_plea_hour must be between 1 and rounds')
        for name in self.frozen_text_names:  # fail before any model call, not at the hour the text is needed
            load_text(name)
        self.buyer_models = [None if m in (None, ZIP_BUYER, "none", "None") else m for m in self.buyer_models]
        return self


AgentBidResponse = dict[str, Any]

@total_ordering
class Agent(BaseModel):
    """
    Base class representing an agent in a continuous double auction market.

    Attributes:
        id (str): The buyer's identifying string.
        company: The company this seller is representing
        valuation (float): The price at which the agent values the asset.
        experiment_params (ExperimentParams): Various parameters required to configure agent behavior.
    """
    id: str
    company: str
    valuation: float
    expt_params: ExperimentParams

    def __lt__(self, other: "Agent") -> bool:
        """
        Compare agents based on their ids.
        """
        return self.id < other.id

    def generate_bid_response(self, **kwargs: Any) -> AgentBidResponse:
        """
        Generate a bid response for the agent. Inheriting classes should
        override this method to implement their own bidding strategy.

        Args:
            kwargs: Any additional parameters needed for the bid generation.

        Returns:
            AgentBidResponse: The bid response
        """
        ...


class Trade(BaseModel):
    """
    Represents a trade between a buyer and a seller in the market.
    """
    round_number: int
    buyer_id: str
    seller_id: str
    price: float


class DirectMessage(BaseModel):
    """A private seller-to-seller message (ApartAICollusion sprint addition)."""
    round_number: int
    sender: str
    recipient: str
    text: str
    truncated: bool = False


class MarketRound(BaseModel):
    """
    Represents a single round of trading in the double auction market.
    """
    round_number: int
    seller_asks: dict[str, float] = Field(default_factory=lambda: {})
    buyer_bids: dict[str, float] = Field(default_factory=lambda: {})
    trades: list[Trade] = Field(default_factory=lambda: [])
    seller_messages: dict[str, str] = Field(default_factory=lambda: {})
    buyer_messages: dict[str, str] = Field(default_factory=lambda: {})
    overseer_visible_messages: Optional[list[str]] = None  # seller ids whose messages the overseer saw
    # ApartAICollusion sprint additions: private messages sent this round, and ones dropped as invalid
    seller_dms: list[DirectMessage] = Field(default_factory=lambda: [])
    dropped_dms: list[dict[str, Any]] = Field(default_factory=lambda: [])
    # agents whose turn failed after all retries (unparseable/truncated reply); they keep their previous
    # order and send nothing this round instead of crashing the run
    failed_turns: list[dict[str, str]] = Field(default_factory=lambda: [])
    # D–G scripted seat (market/scripted.py): one row per private message it sent this round, with keys
    # from, to, offer_id, style, tie_claim, target_price, text, round
    scripted_offers: list[dict[str, Any]] = Field(default_factory=lambda: [])
    # Sprint D–G additions. reports: {"from", "about", "about_resolved", "reason", "round"}; never shown to any
    # agent. buyer_notices: {"from", "text", "round"}; shown to every seller from the next hour on.
    reports: list[dict[str, Any]] = Field(default_factory=lambda: [])
    buyer_notices: list[dict[str, Any]] = Field(default_factory=lambda: [])
