# Service Tagger for AWS

## Limitations

* This script currently works for lambda only. Let us know which services you are interested in!

## Install dependencies

`pip install -r requirements.txt`

## Config structure

The yaml config specifies which tags and which functions should get which tag values.

### Structure
```yaml
target_tag:
    tag_value:
      - arn_part
```

The `target_tag` specifies the key of the tag. The `tag_value` specifies the value of the tag. This tag is applied to every resource of the given service whose ARN contains the `arn_part`. 

### Example
```yaml
department:
  research:
    - aws-scheduler
    - stock-watch
    - bottleneck-testing
    - testing-mail
  business:
    - market-watch
    - contracts-appraisal
project:
  scheduler:
    - aws-scheduler
    - bottleneck-testing
  stock-watch:
    - stock-watch
  mail:
    - testing-mail
  market-watch:
    - market-watch
  contracts-appraisal:
    - contracts-appraisal
```

## Run

* Show the help: `python tagger.py --help`
* Show existing tags: `python tagger.py TAG_1,TAG_2,TAG_N`
* Use the region `eu-central-1` instead of the default `us-east-1`: `python tagger.py TAG --region eu-central-1`
* Do a dry run for writing new tags: `python tagger.py TAG --write --dry-run`
* Use a different yaml file than `tag_config.yarml`: `python tagger.py TAG --write --file my_config.yaml`
* Overwrite existing tags: `python tagger.py TAG --write --overwrite`

## Contributions

Yes please! Open a ticket or send a pull request.
