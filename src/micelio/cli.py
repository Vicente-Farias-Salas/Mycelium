"""Command Line Interface for Mycelium Enterprise."""

import argparse
import sys
import httpx
from typing import Optional

def get_api_client(api_key: str, base_url: str = "http://localhost:8000") -> httpx.Client:
    return httpx.Client(base_url=base_url, headers={"X-Mycelium-API-Key": api_key})

def main() -> None:
    parser = argparse.ArgumentParser(description="Mycelium Enterprise CLI")
    parser.add_argument("--url", default="http://localhost:8000", help="Base API URL")
    parser.add_argument("--key", required=True, help="X-Mycelium-API-Key for authentication")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Health check command
    subparsers.add_parser("health", help="Check system health")
    
    # Tenants command
    tenant_parser = subparsers.add_parser("tenant-create", help="Create a commercial tenant")
    tenant_parser.add_argument("--id", required=True, help="Tenant ID")
    tenant_parser.add_argument("--name", required=True, help="Tenant Name")
    tenant_parser.add_argument("--tier", default="STARTER", choices=["STARTER", "PROFESSIONAL", "ENTERPRISE"])
    tenant_parser.add_argument("--quota", type=int, default=3, help="Max active projects")

    args = parser.parse_args()
    client = get_api_client(args.key, args.url)
    
    if args.command == "health":
        try:
            res = client.get("/health")
            res.raise_for_status()
            print("OK -", res.json())
        except Exception as e:
            print("ERROR connecting to Mycelium:", e)
            sys.exit(1)
            
    elif args.command == "tenant-create":
        payload = {
            "tenant_id": args.id,
            "name": args.name,
            "tier": args.tier,
            "max_active_projects": args.quota
        }
        try:
            res = client.post("/api/tenants", json=payload)
            res.raise_for_status()
            print("Tenant created successfully:", res.json())
        except httpx.HTTPStatusError as e:
            print("API ERROR:", e.response.status_code, e.response.text)
            sys.exit(1)
        except Exception as e:
            print("NETWORK ERROR:", e)
            sys.exit(1)

if __name__ == "__main__":
    main()
