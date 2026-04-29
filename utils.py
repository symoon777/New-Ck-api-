import httpx
from config import cfg


def calc_cut_100(success: int) -> int:
    return 1 if success >= 70 else 0


def calc_cut_200(success: int) -> int:
    if success >= 150: return 2
    if success >= 70:  return 1
    return 0


async def call_like_api(url: str, uid: str) -> dict:
    """
    তোমার API format:
    GET https://ff.api.emonaxc.com/like?key=YSXHC6&uid={UID}
    """
    # URL এ {UID} থাকলে replace করো
    final_url = url.replace("{UID}", uid).replace("{uid}", uid)

    # Query params এ uid add করো (যদি URL এ না থাকে)
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            final_url,
            headers={"User-Agent": "AMS-FF-Like/2.0"},
        )
        resp.raise_for_status()
        data = resp.json()

        # তোমার API যে format এ return করে সেটা handle করো
        success = (
            data.get("success") or
            data.get("likes_sent") or
            data.get("count") or
            data.get("sent") or
            data.get("total") or
            data.get("like") or
            0
        )
        return {"success": int(success), "raw": data}
