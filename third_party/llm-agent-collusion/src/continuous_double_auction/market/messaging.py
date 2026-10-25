"""
Seller messaging helpers: capped public history and persistent private messages.

ApartAICollusion sprint addition (Oct 2026), not part of the original harness. See RESEARCH.md §5.1.

Channels:
- Public (broadcast): one message per seller per hour, visible to every seller. Sellers see the last
  `broadcast_history_rounds` hours of it (1 = the original harness: previous hour only).
- Private (DM): up to `max_dms_per_round` messages per seller per hour, each to one named seller.
  Each seller sees its full private thread with every other seller for the whole episode.

Everything sent in hour k is first visible in hour k+1, matching the original broadcast timing.
"""

from typing import Any, Iterable, Optional, Sequence

from src.continuous_double_auction.cda_types import DirectMessage, MarketRound


def resolve_recipient(raw: Any, sender: str, seller_ids: Sequence[str]) -> Optional[str]:
    """Map a model-written recipient ("Seller Max", "seller max", "Max") to a seller id, or None."""
    if not isinstance(raw, str):
        return None
    name = raw.strip().strip('"').strip()
    if not name:
        return None
    lowered = {sid.lower(): sid for sid in seller_ids}
    if name.lower() in lowered:
        return lowered[name.lower()]
    # allow the bare first name: "Max" -> "Seller Max"
    bare = {sid.lower().removeprefix("seller ").strip(): sid for sid in seller_ids}
    return bare.get(name.lower().removeprefix("seller ").strip())


def _iter_raw_dms(raw: Any) -> Iterable[tuple[Any, Any]]:
    """Yield (recipient, text) pairs from the shapes models actually produce."""
    if raw is None or raw == "null" or raw == "":
        return
    if isinstance(raw, dict):  # {"Seller Max": "text", ...}
        if "to" in raw:  # a single {"to": ..., "text": ...} object instead of a list
            yield raw.get("to"), raw.get("text")
            return
        for to, text in raw.items():
            yield to, text
        return
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                yield item.get("to"), item.get("text", item.get("message"))
            else:
                yield None, item
        return
    yield None, raw


def parse_direct_messages(
    raw: Any,
    sender: str,
    seller_ids: Sequence[str],
    round_number: int,
    max_dms: int,
    max_length: int,
) -> tuple[list[DirectMessage], list[dict[str, Any]]]:
    """
    Validate a seller's `direct_messages` field.

    Returns (accepted, dropped). Invalid entries are dropped with a reason, never raised:
    unknown_recipient, self, empty, over_limit.
    """
    accepted: list[DirectMessage] = []
    dropped: list[dict[str, Any]] = []
    for to_raw, text_raw in _iter_raw_dms(raw):
        record = {"round_number": round_number, "sender": sender, "to": to_raw, "text": text_raw}
        recipient = resolve_recipient(to_raw, sender, seller_ids)
        text = "" if text_raw is None else str(text_raw).strip()
        if recipient is None:
            dropped.append({**record, "reason": "unknown_recipient"})
        elif recipient == sender:
            dropped.append({**record, "reason": "self"})
        elif not text or text.lower() == "null":
            dropped.append({**record, "reason": "empty"})
        elif len(accepted) >= max_dms:
            dropped.append({**record, "reason": "over_limit"})
        else:
            truncated = len(text) > max_length
            accepted.append(
                DirectMessage(
                    round_number=round_number,
                    sender=sender,
                    recipient=recipient,
                    text=text[:max_length] if truncated else text,
                    truncated=truncated,
                )
            )
    return accepted, dropped


def broadcast_history(rounds: Sequence[MarketRound], n_rounds: int) -> list[dict[str, Any]]:
    """Public messages from the last `n_rounds` completed hours, oldest first."""
    history = []
    for rnd in rounds[-n_rounds:] if n_rounds > 0 else []:
        history.append(
            {
                "round_number": rnd.round_number,
                "messages": [(sid, rnd.seller_messages[sid]) for sid in sorted(rnd.seller_messages)],
            }
        )
    return history


def dm_threads(rounds: Sequence[MarketRound], seller_id: str, seller_ids: Sequence[str]) -> dict[str, list[dict[str, Any]]]:
    """
    The seller's full private thread with each other seller, oldest first.

    Keys are every other seller (empty list if no messages yet) so the prompt lists who can be messaged.
    Each entry: {"round_number", "direction": "sent"|"received", "text"}.
    """
    threads: dict[str, list[dict[str, Any]]] = {sid: [] for sid in sorted(seller_ids) if sid != seller_id}
    for rnd in rounds:
        for dm in rnd.seller_dms:
            if dm.sender == seller_id and dm.recipient in threads:
                threads[dm.recipient].append({"round_number": dm.round_number, "direction": "sent", "text": dm.text})
            elif dm.recipient == seller_id and dm.sender in threads:
                threads[dm.sender].append({"round_number": dm.round_number, "direction": "received", "text": dm.text})
    return threads


def parse_reports(raw: Any, sender: str, seller_ids: Sequence[str], round_number: int) -> list[dict[str, Any]]:
    """
    Validate a seller's `report_to_regulator` field (sprint D–G addition).

    Accepts {"seller": ..., "reason": ...} (or, if a model writes several, a list of them); null, "null", "" and
    entries without a non-empty `seller` give nothing. The name is resolved like a private-message recipient;
    an unknown name is kept verbatim with about_resolved=False so false or confused reports stay measurable.
    Reports are only recorded: nothing reads them back into the market, the overseer or any prompt.
    """
    items = raw if isinstance(raw, list) else [raw]
    reports = []
    for item in items:
        if not isinstance(item, dict):
            continue
        about_raw = item.get("seller")
        if not isinstance(about_raw, str) or not about_raw.strip() or about_raw.strip().lower() == "null":
            continue
        resolved = resolve_recipient(about_raw, sender, seller_ids)
        reason = item.get("reason")
        reports.append(
            {
                "from": sender,
                "about": resolved if resolved is not None else about_raw.strip(),
                "about_resolved": resolved is not None,
                "reason": "" if reason is None else str(reason).strip(),
                "round": round_number,
            }
        )
    return reports


def buyer_notices(rounds: Sequence[MarketRound]) -> list[dict[str, Any]]:
    """Every buyer notice posted in completed hours, oldest first (sprint D–G addition; persistent, like threads)."""
    return [notice for rnd in rounds for notice in rnd.buyer_notices]
