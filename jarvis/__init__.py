import os

from dotenv import dotenv_values, load_dotenv


load_dotenv(".env.secret")

# config = {
#     **dotenv_values(".env.shared"),  # load shared development variables
#     **dotenv_values(".env.secret"),  # load sensitive variables
#     **os.environ,  # override loaded values with environment variables
# }
# load_dotenv(config)

# print(f"envvars {config}")
