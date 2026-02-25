from pathlib import Path

base_dir = Path("techcorp-docs")

folders = ["policies", "products", "support"]

documents = {
    "policies": {
        "remote_work.md": """
# Remote Work Policy

Employees may work remotely up to 3 days per week with manager approval.
All remote employees must remain available during core business hours (9am–3pm).
VPN usage is required when accessing internal systems.
""",
        "dress_code.md": """
# Dress Code Policy

Business casual is required Monday through Thursday.
Jeans are permitted on Fridays.
Client-facing meetings require formal attire.
"""
    },
    "products": {
        "cloudsync.md": """
# CloudSync Product Specification

CloudSync is a distributed file synchronization platform.
Supports real-time replication across regions.
Includes AES-256 encryption at rest and TLS 1.3 in transit.
""",
        "datastream.md": """
# DataStream Analytics Engine

DataStream processes up to 1 million events per second.
Provides real-time dashboards and anomaly detection.
Integrates with AWS, Azure, and GCP.
"""
    },
    "support": {
        "password_reset.md": """
# Password Reset Guide

Users can reset passwords using the self-service portal.
Password must be at least 12 characters long.
Multi-factor authentication is required.
""",
        "vpn_troubleshooting.md": """
# VPN Troubleshooting

Ensure VPN client is updated to the latest version.
Check firewall settings if connection fails.
Contact IT support if issue persists.
"""
    }
}

# Create folders and files
for folder in folders:
    folder_path = base_dir / folder
    folder_path.mkdir(parents=True, exist_ok=True)

    for filename, content in documents[folder].items():
        file_path = folder_path / filename
        file_path.write_text(content.strip())

print("✅ Synthetic TechCorp dataset created successfully!")