"""Financieel Beheer – Home Assistant integratie.

Biedt:
- Sensor: aantal transacties dat review vereist
- Service: ha_finance.sync_transactions         – haal nieuwe transacties op van alle banken
- Service: ha_finance.book_monthly_bookings     – boek openstaande maandelijkse boekingen
- Service: ha_finance.book_loan_installments    – boek openstaande leningtermijnen
- Service: ha_finance.book_depreciations        – boek openstaande afschrijvingen
"""
import logging
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_URL, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Stel de integratie in vanuit een config entry."""
    url = entry.data[CONF_URL]
    token = entry.data[CONF_TOKEN]

    async def _fetch_stats() -> dict:
        session = async_get_clientsession(hass)
        try:
            async with session.get(
                f"{url}/api/integration/stats",
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"API antwoordde met status {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Verbindingsfout: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_stats",
        update_method=_fetch_stats,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "url": url,
        "token": token,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def handle_sync_transactions(call: ServiceCall) -> None:
        """Service handler: synchroniseer transacties van alle bankverbindingen."""
        session = async_get_clientsession(hass)
        try:
            async with session.post(
                f"{url}/api/integration/sync-all",
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    _LOGGER.error("Sync mislukt (status %s): %s", resp.status, body)
                    return
                results = await resp.json()
                total_imported = sum(r.get("imported", 0) for r in results)
                total_review = sum(r.get("needs_review", 0) for r in results)
                _LOGGER.info(
                    "Sync klaar: %d transacties geïmporteerd, %d vereisen review",
                    total_imported,
                    total_review,
                )
        except aiohttp.ClientError as err:
            _LOGGER.error("Sync verbindingsfout: %s", err)
        finally:
            await coordinator.async_request_refresh()

    async def handle_book_monthly_bookings(call: ServiceCall) -> None:
        """Service handler: boek alle openstaande maandelijkse boekingen."""
        session = async_get_clientsession(hass)
        try:
            async with session.post(
                f"{url}/api/integration/book-monthly-bookings",
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    _LOGGER.error("Maandelijkse boekingen mislukt (status %s): %s", resp.status, body)
                    return
                result = await resp.json()
                _LOGGER.info(
                    "Maandelijkse boekingen klaar: %d transacties aangemaakt, %d overgeslagen",
                    result.get("booked", 0),
                    result.get("skipped", 0),
                )
        except aiohttp.ClientError as err:
            _LOGGER.error("Maandelijkse boekingen verbindingsfout: %s", err)
        finally:
            await coordinator.async_request_refresh()

    async def handle_book_loan_installments(call: ServiceCall) -> None:
        """Service handler: boek alle openstaande leningtermijnen."""
        session = async_get_clientsession(hass)
        try:
            async with session.post(
                f"{url}/api/integration/book-loan-installments",
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    _LOGGER.error("Lening-boekingen mislukt (status %s): %s", resp.status, body)
                    return
                result = await resp.json()
                _LOGGER.info(
                    "Lening-boekingen klaar: %d termijnen geboekt, %d overgeslagen",
                    result.get("booked", 0),
                    result.get("skipped", 0),
                )
        except aiohttp.ClientError as err:
            _LOGGER.error("Lening-boekingen verbindingsfout: %s", err)
        finally:
            await coordinator.async_request_refresh()

    async def handle_book_depreciations(call: ServiceCall) -> None:
        """Service handler: boek alle openstaande afschrijvingen."""
        session = async_get_clientsession(hass)
        try:
            async with session.post(
                f"{url}/api/integration/book-depreciations",
                headers={"Authorization": f"Bearer {token}"},
                timeout=aiohttp.ClientTimeout(total=120),
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    _LOGGER.error("Afschrijvingen mislukt (status %s): %s", resp.status, body)
                    return
                result = await resp.json()
                _LOGGER.info(
                    "Afschrijvingen klaar: %d maanden geboekt, %d overgeslagen",
                    result.get("booked", 0),
                    result.get("skipped", 0),
                )
        except aiohttp.ClientError as err:
            _LOGGER.error("Afschrijvingen verbindingsfout: %s", err)
        finally:
            await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, "sync_transactions"):
        hass.services.async_register(DOMAIN, "sync_transactions", handle_sync_transactions)
    if not hass.services.has_service(DOMAIN, "book_monthly_bookings"):
        hass.services.async_register(DOMAIN, "book_monthly_bookings", handle_book_monthly_bookings)
    if not hass.services.has_service(DOMAIN, "book_loan_installments"):
        hass.services.async_register(DOMAIN, "book_loan_installments", handle_book_loan_installments)
    if not hass.services.has_service(DOMAIN, "book_depreciations"):
        hass.services.async_register(DOMAIN, "book_depreciations", handle_book_depreciations)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Verwijder de integratie."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "sync_transactions")
            hass.services.async_remove(DOMAIN, "book_monthly_bookings")
            hass.services.async_remove(DOMAIN, "book_loan_installments")
            hass.services.async_remove(DOMAIN, "book_depreciations")
    return unloaded
