import yaml
import json
import logging


def get_yaml_prompt(prompt_file_path: str, key: str = "text"):
    """
    get the prompt from a yaml file.
    """
    try:
        with open(prompt_file_path, "r") as f:
            prompt = yaml.safe_load(f)
        return prompt[key]
    except FileNotFoundError:
        logging.error(f"Prompt file not found: {prompt_file_path}")
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
    except KeyError:
        logging.error(f"The key: {key} is not in the YAML file.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")