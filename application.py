#!/usr/bin/python3
import boto3
import snowlib
import json
import sys


def main():
    logger = snowlib.Logger()
    # Get config
    config = snowlib.ConfigHelper()
    if not config.validate_config():
        sys.exit(1)

    # Create objects we'll interact with later
    halo = snowlib.Halo(config.halo_api_key, config.halo_api_secret_key, config.halo_api_hostname)
    # Get issues created, changed, deleted since starting timestamp
    logger.info(f"Getting all Halo issues")

    issues_count = 0

    for rule in config.rules:
        halo_issues = halo.get_issues(rule.get("filters", {}))

        # Print initial stats
        logger.info(f"Posting {len(halo_issues)} Halo issues")
        snow = snowlib.Snow(config.snow_api_user, config.snow_api_pwd, config.snow_api_url, rule)

        if halo_issues:
            snow.push_halo_issues(halo_issues)

        logger.info("Updating issues")
        snow.update_all_issues(halo)

    logger.info("Done!")

    return {"result": json.dumps(
                {"message": "Halo/SNOW issue sync complete",
                 "total_issues": issues_count})}


if __name__ == "__main__":
    main()
