from uuid import uuid4

import httpx
import pytest


@pytest.mark.asyncio
async def test_market_bet_and_resolve_flow(market_client: httpx.AsyncClient) -> None:
    user_id = str(uuid4())
    wallet_response = await market_client.post(
        "/api/v1/wallets",
        json={"user_id": user_id, "initial_balance": 1000.0},
    )
    assert wallet_response.status_code == 201
    assert wallet_response.json()["balance"] == pytest.approx(1000.0)

    market_response = await market_client.post(
        "/api/v1/markets",
        json={
            "event_id": str(uuid4()),
            "title": "Forward transfer",
            "description": "Forward can move in summer.",
            "initial_probability": 0.25,
            "liquidity_parameter": 1000.0,
        },
    )
    assert market_response.status_code == 201
    market = market_response.json()
    assert market["status"] == "active"
    assert market["yes_probability"] == pytest.approx(0.25)
    assert market["yes_odds"] == pytest.approx(4.0)

    bet_response = await market_client.post(
        f"/api/v1/markets/{market['id']}/bets",
        json={"user_id": user_id, "side": "yes", "amount": 100.0},
    )
    assert bet_response.status_code == 201
    bet = bet_response.json()
    assert bet["shares"] > 100.0
    assert bet["probability_after"] > bet["probability_before"]

    wallet_after_bet = await market_client.get(f"/api/v1/wallets/{user_id}")
    assert wallet_after_bet.status_code == 200
    assert wallet_after_bet.json()["balance"] == pytest.approx(900.0)

    current_market_response = await market_client.get(f"/api/v1/markets/{market['id']}")
    assert current_market_response.status_code == 200
    assert current_market_response.json()["yes_probability"] > 0.25

    resolve_response = await market_client.post(
        f"/api/v1/markets/{market['id']}/resolve",
        json={"outcome": "yes"},
    )
    assert resolve_response.status_code == 200
    assert resolve_response.json()["status"] == "resolved"
    assert resolve_response.json()["outcome"] == "yes"

    wallet_after_resolve = await market_client.get(f"/api/v1/wallets/{user_id}")
    assert wallet_after_resolve.status_code == 200
    assert wallet_after_resolve.json()["balance"] == pytest.approx(
        900.0 + bet["shares"]
    )

    positions_response = await market_client.get(
        f"/api/v1/markets/{market['id']}/positions"
    )
    assert positions_response.status_code == 200
    positions = positions_response.json()["items"]
    assert len(positions) == 1
    assert positions[0]["realized_payout"] == pytest.approx(bet["shares"])


@pytest.mark.asyncio
async def test_place_bet_requires_wallet(market_client: httpx.AsyncClient) -> None:
    market_response = await market_client.post(
        "/api/v1/markets",
        json={
            "event_id": str(uuid4()),
            "title": "Coach exit",
            "description": "Coach can leave the club.",
            "initial_probability": 0.5,
            "liquidity_parameter": 1000.0,
        },
    )
    assert market_response.status_code == 201
    market = market_response.json()

    bet_response = await market_client.post(
        f"/api/v1/markets/{market['id']}/bets",
        json={"user_id": str(uuid4()), "side": "no", "amount": 50.0},
    )

    assert bet_response.status_code == 400
    assert "Wallet for user" in bet_response.json()["detail"]


@pytest.mark.asyncio
async def test_public_market_read_routes_do_not_require_auth(
    market_client: httpx.AsyncClient,
) -> None:
    market_response = await market_client.post(
        "/api/v1/markets",
        json={
            "event_id": str(uuid4()),
            "title": "Public browsing",
            "description": "Should be visible without auth.",
            "initial_probability": 0.4,
            "liquidity_parameter": 1000.0,
        },
    )
    assert market_response.status_code == 201
    market = market_response.json()

    market_client.headers.pop("Authorization", None)

    list_response = await market_client.get("/api/v1/markets")
    assert list_response.status_code == 200

    detail_response = await market_client.get(f"/api/v1/markets/{market['id']}")
    assert detail_response.status_code == 200

    positions_response = await market_client.get(
        f"/api/v1/markets/{market['id']}/positions"
    )
    assert positions_response.status_code == 200
