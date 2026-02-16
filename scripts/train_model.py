#!/usr/bin/env python3
"""Train the ACJI revenue proxy model."""

from __future__ import annotations

import json

from acji.config import get_settings
from acji.model.train import train_revenue_model



def main() -> None:
    settings = get_settings()
    metrics = train_revenue_model(settings)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
