BIN_NODE_IDS = {
    "recyclable": 10,
    "reusable": 11,
    "biodegradable": 12,
    "hazardous": 13,
    "residual": 14,
}

BIN_NAME_ALIASES = {
    "Recyclable Bin": "recyclable",
    "Reusable/Donation Bin": "reusable",
    "Reusable Bin": "reusable",
    "Biodegradable/Compost Bin": "biodegradable",
    "Biodegradable Bin": "biodegradable",
    "Hazardous Collection": "hazardous",
    "Hazardous Bin": "hazardous",
    "Residual/Landfill Bin": "residual",
    "Residual Bin": "residual",
}


def normalize_bin_name(bin_name: str | None) -> str | None:
    if bin_name is None:
        return None
    return BIN_NAME_ALIASES.get(bin_name, bin_name)
