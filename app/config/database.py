from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, List, Dict, Any
from app.config.settings import settings
import dns.resolver
import logging
import socket
import threading
import time
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, quote
from pymongo import errors as pymongo_errors

logger = logging.getLogger(__name__)

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db = None

database = Database()
_doh_cache: Dict[str, Dict[str, Any]] = {}
_doh_cache_lock = threading.Lock()
_doh_patch_lock = threading.Lock()
_doh_patch_applied = False

async def connect_to_mongo():
    """Connect to MongoDB with improved error handling and DNS fallbacks."""
    doh_override = False
    mongodb_uri = settings.MONGODB_URL or ""
    allow_doh_fallback = mongodb_uri.startswith("mongodb+srv://") and not settings.MONGODB_FORCE_DOH

    while True:
        try:
            if settings.MONGODB_DNS_SERVERS:
                logger.info("Custom DNS configuration enabled")
            elif settings.MONGODB_FORCE_DOH or doh_override:
                logger.info("Forcing DNS-over-HTTPS for MongoDB resolution")
            else:
                logger.info("Using system default DNS resolution")

            configure_dns_resolver(force_doh=settings.MONGODB_FORCE_DOH or doh_override)

            effective_uri = build_effective_mongo_uri(
                mongodb_uri,
                force_doh=settings.MONGODB_FORCE_DOH or doh_override,
            )

            database.client = AsyncIOMotorClient(
                effective_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
            )
            database.db = database.client[settings.MONGODB_DB_NAME]

            await database.client.admin.command("ping")
            logger.info("Connected to MongoDB: %s", settings.MONGODB_DB_NAME)
            await create_indexes()
            break

        except pymongo_errors.ConfigurationError as exc:
            if allow_doh_fallback and _looks_like_dns_failure(exc):
                logger.warning("MongoDB SRV lookup failed via system DNS: %s", exc)
                logger.info("Retrying MongoDB connection with DoH fallback enabled")
                doh_override = True
                allow_doh_fallback = False
                continue
            _log_connection_failure(exc)
            raise
        except Exception as exc:
            _log_connection_failure(exc)
            raise


def build_effective_mongo_uri(uri: str, force_doh: Optional[bool] = None) -> str:
    """Convert mongodb+srv URIs to standard ones using DoH when requested."""
    if not uri or not uri.startswith("mongodb+srv://"):
        return uri

    parsed = urlparse(uri)
    host = parsed.hostname
    if not host:
        return uri

    query_params = parse_qs(parsed.query, keep_blank_values=True)
    base_params = {key: values[-1] for key, values in query_params.items()}

    use_doh = settings.MONGODB_FORCE_DOH if force_doh is None else force_doh
    if not use_doh:
        logger.info("Using mongodb+srv:// with system DNS resolution")
        return uri

    auth = ""
    if parsed.username:
        auth += quote(parsed.username)
        if parsed.password:
            auth += f":{quote(parsed.password)}"
        auth += "@"

    try:
        srv_records = _doh_query(f"_mongodb._tcp.{host}", "SRV")
        if not srv_records:
            logger.warning("Could not resolve SRV records for %s via DoH, falling back to heuristics", host)
            raise RuntimeError("No SRV answers via DoH")

        hosts = []
        for record in srv_records:
            data = record.get("data", "")
            parts = data.split()
            if len(parts) != 4:
                continue
            _, _, port, target = parts
            cleaned_target = target.rstrip(".")
            hosts.append(f"{cleaned_target}:{port}".replace(" ", ""))

        if not hosts:
            raise RuntimeError(f"No usable SRV entries returned for {host}")

        txt_records = _doh_query(f"_mongodb._tcp.{host}", "TXT")
        txt_params = {}
        if txt_records:
            raw_txt = txt_records[0].get("data", "").strip('"')
            if raw_txt:
                for item in raw_txt.split("&"):
                    if "=" in item:
                        key, value = item.split("=", 1)
                        txt_params[key] = value

        merged_params = dict(base_params)
        merged_params.update(txt_params)

        netloc = f"{auth}{','.join(hosts)}"
        new_url = urlunparse(
            (
                "mongodb",
                netloc,
                parsed.path or "",
                parsed.params,
                urlencode(merged_params),
                parsed.fragment,
            )
        )
        logger.info("Using SRV-resolved MongoDB URI via DoH")
        return new_url
    except Exception as exc:
        logger.warning("Failed to build MongoDB URI via DoH: %s", exc)
        fallback_uri = _build_atlas_seedlist_uri(parsed, auth, base_params, host)
        if fallback_uri:
            logger.warning(
                "Falling back to heuristic Atlas seed list for %s. Consider adding a mongodb:// URI to your .env to avoid DNS entirely.",
                host,
            )
            return fallback_uri
        return uri

def configure_dns_resolver(force_doh: Optional[bool] = None):
    """Allow overriding DNS resolution strategy before creating the MongoDB client."""
    configured_custom = _apply_custom_nameservers()
    configured_doh = _apply_dns_over_https(force_doh=force_doh)
    
    if not configured_custom and not configured_doh:
        logger.info("No custom DNS configuration applied, using system defaults")

def _build_atlas_seedlist_uri(parsed, auth: str, base_params: Dict[str, Any], host: str) -> str:
    """Best-effort fallback to Atlas shard hostnames when DNS is unavailable."""
    seed_hosts = _guess_atlas_seedlist(host)
    if not seed_hosts:
        return ""

    params = dict(base_params)
    _ensure_tls_param(params)
    if settings.MONGODB_REPLICA_SET and "replicaSet" not in params:
        params["replicaSet"] = settings.MONGODB_REPLICA_SET

    netloc = f"{auth}{','.join(seed_hosts)}"
    return urlunparse(
        (
            "mongodb",
            netloc,
            parsed.path or "",
            parsed.params,
            urlencode(params),
            parsed.fragment,
        )
    )

def _ensure_tls_param(params: Dict[str, Any]) -> None:
    """Make sure TLS stays enabled when converting SRV -> standard URI."""
    lower_keys = {key.lower() for key in params.keys()}
    if "tls" not in lower_keys and "ssl" not in lower_keys:
        params["tls"] = "true"

def _guess_atlas_seedlist(host: str) -> List[str]:
    """Heuristically derive Atlas shard hostnames when SRV lookup is impossible."""
    if not host or not host.endswith(".mongodb.net"):
        return []

    prefix, _, domain = host.partition(".")
    if not prefix or not domain:
        return []

    # If the user already supplied a direct shard hostname, nothing to do.
    if "-shard-00-" in prefix:
        return []

    return [
        f"{prefix}-shard-00-0{i}.{domain}:27017"
        for i in range(3)
    ]

def _apply_custom_nameservers():
    """Apply custom DNS nameservers if configured."""
    if not settings.MONGODB_DNS_SERVERS:
        return False

    servers = [
        server.strip()
        for server in settings.MONGODB_DNS_SERVERS.split(",")
        if server.strip()
    ]
    if not servers:
        return False

    try:
        resolver = dns.resolver.Resolver(configure=False)  # ✅ Don't use system config
        resolver.nameservers = servers
        resolver.timeout = 5  # ✅ Add timeout
        resolver.lifetime = 10  # ✅ Add lifetime
        dns.resolver.default_resolver = resolver
        logger.info("Configured custom DNS servers for MongoDB resolution: %s", servers)
        return True
    except Exception as e:
        logger.error("Failed to configure custom DNS servers: %s", e)
        return False

def _apply_dns_over_https(force_doh: Optional[bool] = None):
    """Force DNS queries through HTTPS (helps when UDP/TCP port 53 is blocked)."""
    enable_doh = settings.MONGODB_FORCE_DOH if force_doh is None else force_doh
    if not enable_doh:
        return False

    suffixes = [
        suffix.strip().lower()
        for suffix in settings.MONGODB_DOH_DOMAINS.split(",")
        if suffix.strip()
    ]
    if not suffixes:
        return False

    endpoints = _get_doh_endpoints()

    global _doh_patch_applied
    with _doh_patch_lock:
        if _doh_patch_applied:
            return True

        original_getaddrinfo = socket.getaddrinfo

        def doh_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
            if host and _should_handle_host(host, suffixes):
                try:
                    resolved_port = _normalize_port(port)
                    addresses = _doh_lookup(host)
                    if addresses:
                        return [
                            (
                                socket.AF_INET,
                                type or socket.SOCK_STREAM,
                                proto or 0,
                                "",
                                (addr, resolved_port),
                            )
                            for addr in addresses
                        ]
                except Exception as exc:
                    logger.warning(
                        "DNS-over-HTTPS lookup failed for %s: %s, falling back to system DNS",
                        host,
                        exc,
                    )

            return original_getaddrinfo(host, port, family, type, proto, flags)

        socket.getaddrinfo = doh_getaddrinfo
        _doh_patch_applied = True
        logger.info(
            "Enabled DNS-over-HTTPS fallback via %s for suffixes: %s",
            endpoints[0],
            suffixes,
        )
    return True

def _looks_like_dns_failure(exc: Exception) -> bool:
    """Heuristic check to decide if the exception is DNS related."""
    message = str(exc).lower()
    keywords = [
        "resolution lifetime expired",
        "dns operation timed out",
        "failed to resolve",
        "srv record lookup failed",
        "nodename nor servname provided",
        "name or service not known",
        "temporary failure in name resolution",
    ]
    return any(keyword in message for keyword in keywords)

def _log_connection_failure(exc: Exception) -> None:
    logger.error(f"Could not connect to MongoDB: {exc}")
    logger.error("Troubleshooting tips:")
    logger.error("1. Check MONGODB_URL in your .env file")
    logger.error("2. Ensure MONGODB_FORCE_DOH=false unless DoH is required")
    logger.error("3. Verify network connection")
    logger.error("4. Check MongoDB Atlas IP whitelist (if using Atlas)")
    logger.error("5. Try using a standard mongodb:// URI instead of mongodb+srv://")

def _should_handle_host(host: str, suffixes: List[str]) -> bool:
    host_lower = host.lower()
    return any(host_lower.endswith(suffix) for suffix in suffixes)

def _normalize_port(port: Any) -> int:
    if isinstance(port, int):
        return port
    if isinstance(port, str) and port.isdigit():
        return int(port)
    return 0

def _doh_lookup(host: str) -> List[str]:
    now = time.time()
    with _doh_cache_lock:
        cached = _doh_cache.get(host)
        if cached and cached["expires_at"] > now:
            return cached["addresses"]

    answers = _doh_query(host, "A")

    addresses = [
        answer.get("data")
        for answer in answers
        if answer.get("type") == 1 and answer.get("data")
    ]
    if not addresses:
        raise RuntimeError(f"No A records returned for {host}")

    ttl_values = [answer.get("TTL") for answer in answers if answer.get("TTL")]
    ttl = min(ttl_values) if ttl_values else 60
    expires_at = now + max(ttl, 30)

    with _doh_cache_lock:
        _doh_cache[host] = {
            "addresses": addresses,
            "expires_at": expires_at,
        }
    return addresses

def _doh_query(name: str, record_type: str) -> List[Dict[str, Any]]:
    """Query DNS over HTTPS with timeout, retries, and error handling."""
    params = {"name": name, "type": record_type}
    headers = {"accept": "application/dns-json"}
    endpoints = _get_doh_endpoints()
    last_error: Optional[Exception] = None

    for endpoint in endpoints:
        try:
            request_params = dict(params)
            if "cloudflare-dns.com" in endpoint and "ct" not in request_params:
                request_params["ct"] = "application/dns-json"
            response = requests.get(
                endpoint,
                params=request_params,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            payload = response.json()
            answers = payload.get("Answer", [])
            if answers:
                return answers
            logger.warning(
                "DoH query via %s returned no answers for %s (type %s)",
                endpoint,
                name,
                record_type,
            )
        except requests.exceptions.Timeout as exc:
            logger.error(
                "DoH query timeout via %s for %s (type %s)",
                endpoint,
                name,
                record_type,
            )
            last_error = exc
        except requests.exceptions.RequestException as exc:
            logger.error(
                "DoH query failed via %s for %s: %s",
                endpoint,
                name,
                exc,
            )
            last_error = exc

    message = (
        f"DNS-over-HTTPS query failed for {name} (type {record_type}) via endpoints: "
        + ", ".join(endpoints)
    )
    if last_error:
        raise RuntimeError(message) from last_error
    raise RuntimeError(message)

def _get_doh_endpoints() -> List[str]:
    raw = settings.MONGODB_DOH_ENDPOINT or ""
    endpoints = [endpoint.strip() for endpoint in raw.split(",") if endpoint.strip()]
    if endpoints:
        return endpoints
    return [
        "https://cloudflare-dns.com/dns-query",
        "https://dns.google/resolve",
    ]

async def close_mongo_connection():
    """Close MongoDB connection"""
    try:
        if database.client:
            database.client.close()
            logger.info("Closed MongoDB connection")
    except Exception as e:
        logger.error(f"Error closing MongoDB connection: {e}")

async def create_indexes():
    """Create database indexes for better performance"""
    try:
        # Fixed: Use 'is not None' instead of boolean evaluation
        if database.db is None:
            logger.warning("Database not yet available for creating indexes")
            return
            
        db = database.db
        
        # Users indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("phone")
        
        # Menu items indexes
        await db.menu_items.create_index("category")
        await db.menu_items.create_index("is_available")
        
        # Orders indexes
        await db.orders.create_index("user_id")
        await db.orders.create_index("order_number", unique=True)
        await db.orders.create_index("status")
        
        logger.info("Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

def get_database():
    """Get database instance"""
    if database.db is None:
        logger.warning("Database not connected yet")
    return database.db
